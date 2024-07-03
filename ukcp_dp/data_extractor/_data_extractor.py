""""
This module contains the DataExtractor class.

"""
import functools
import glob
import logging
from os import path
import signal

import iris
from iris.cube import CubeList
import iris.experimental.equalise_cubes
from iris.time import PartialDateTime
from iris.util import unify_time_units

import cf_units
from ukcp_dp.constants import (
    COLLECTION_PROB,
    InputType,
    TEMP_ANOMS,
    COLLECTION_MARINE,
    AreaType,
    TemporalAverageType,
    COLLECTION_CPM,
    COLLECTION_DERIVED,
    COLLECTION_GCM,
    COLLECTION_OBS,
    COLLECTION_RCM,
    COLLECTION_RCM_GWL,
    IRIS_LOAD_TIMEOUT_SECONDS,
    CUBE_NAME_MAPPING,
)
from ukcp_dp.data_extractor._utils import get_anomaly
from ukcp_dp.exception import (
    UKCPDPDataNotFoundException,
    UKCPDPInvalidParameterException,
)
from ukcp_dp.utils import get_baseline_range, get_spatial_resolution_m
from ukcp_dp.vocab_manager import get_months


LOG = logging.getLogger(__name__)


class DataExtractor:
    """
    Extract data from a list of files and filter it based on user selection
    criteria.
    """

    def __init__(self, file_lists, input_data, plot_settings):
        """
        Initialise the DataExtractor.

        @param a dict of lists of files, including their full paths
            key - 'main' or 'overlay'
            value - a dict where
                key: (str) variable name
                value: list of lists where:
                    each list is a list of files per scenario, including their
                    full paths
        @param input_data (InputData) an object containing user defined values
        @param plot_settings (StandardMap): an object containing plot settings
        """
        self.file_lists = file_lists
        self.input_data = input_data
        self.plot_settings = plot_settings
        self.cubes = self._get_main_cubes()
        self.overlay_cube = self._get_overlay_cube()
        LOG.debug("DataExtractor __init__ finished")

    def get_cubes(self):
        """
        Get an iris cube list.

        The data are based on the selection criteria from the input_data.

        @return an iris cube list, one cube per scenario, per variable
        """
        LOG.info("get_cubes")
        return self.cubes

    def get_overlay_cube(self):
        """
        Get an iris cube for the overlay data.

        The data are based on the selection criteria from the input_data. The
        cube will contain the 10th, 50th and 90th percentiles.

        @return an iris cube, may be 'None'
        """
        return self.overlay_cube

    def _get_main_cubes(self):
        """
        Get an iris cube list based on the given files and using selection
        criteria from the input_data.

        If a baseline has been provided then a climatology may be need to be
        produced in order to generate the anomalies.

        @return an iris cube list containing the main data, one cube per
            scenario, per variable
        """
        LOG.debug("_get_main_cubes")
        cubes = iris.cube.CubeList()

        for variable in self.input_data.get_value(InputType.VARIABLE):
            # for each variable there is a list of files per scenario
            for i, file_list in enumerate(self.file_lists["main"][variable]):

                if variable.endswith("Anom") and self.input_data.get_value(
                    InputType.COLLECTION
                ) not in [COLLECTION_PROB, COLLECTION_MARINE]:
                    # we need anomalies so lets calculate them
                    cube = self._get_anomaly_cube(
                        file_list, self.file_lists["baseline"][variable][i]
                    )

                else:
                    # we can use the values directly from the file
                    cube = self._get_cube(file_list)

                # do we need to convert percentiles?
                if (
                    self.input_data.get_value(InputType.CONVERT_TO_PERCENTILES)
                    is not None
                ) and (
                    self.input_data.get_value(InputType.CONVERT_TO_PERCENTILES) is True
                ):
                    cube = self._convert_to_percentiles_from_ensembles(cube)

                cubes.append(cube)

        LOG.debug("Final cubes:\n%s", cubes)

        return cubes

    def _get_anomaly_cube(self, file_list, climatology_file_list):
        LOG.debug("_get_anomaly_cube")
        # anomalies have been selected for something other than LS1,
        # therefore we need to calculate the anomalies using the
        # climatology
        cube_absoute = self._get_cube(file_list)

        cube_climatology = self._get_cube(climatology_file_list, climatology=True)

        baseline = self.input_data.get_value(InputType.BASELINE)

        LOG.debug("cube_absoute\n%s", cube_absoute)
        LOG.debug("cube_climatology\n%s", cube_climatology)

        anomaly = get_anomaly(
            cube_climatology,
            cube_absoute,
            baseline,
            self.plot_settings.preferred_unit,
            self.input_data.get_value(InputType.SCENARIO),
            self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
            self.input_data.get_value(InputType.TIME_PERIOD),
            self.input_data.get_value(InputType.COLLECTION),
            self.input_data.get_value(InputType.VARIABLE),
        )

        return anomaly

    def _get_overlay_cube(self):
        """
        Get an iris cube based on the given files and using selection criteria
        from the input_data.

        The cube produced containing the 10th, 50th and 90th percentiles.

        @return an iris cube, maybe 'None'
        """
        LOG.debug("_get_overlay_cube")
        overlay_cube = None
        if (
            self.input_data.get_value(InputType.COLLECTION) != COLLECTION_PROB
            and self.input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS)
            is not None
            and self.input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is True
            and "overlay" in self.file_lists.keys()
        ):

            for variable in self.file_lists["overlay"].keys():
                # for each variable there is a list of files per scenario
                for file_list in self.file_lists["overlay"][variable]:

                    overlay_cube = self._get_cube(
                        file_list, overlay_probability_levels=True
                    )
                    if overlay_cube is not None and variable in TEMP_ANOMS:
                        overlay_cube.units = cf_units.Unit("Celsius")

        LOG.debug("Overlay cube:\n%s", overlay_cube)

        return overlay_cube

    def _get_cube(self, file_list, climatology=False, overlay_probability_levels=False):
        """
        Get an iris cube based on the given files using selection criteria
        from the input_data.

        @param file_list (list[str]): a list of file name to retrieve data from
        @param climatology (boolean): if True extract the climatology data
        @param overlay_probability_levels (boolean): if True only include the
            10th, 50th and 90th percentile data

        @return an iris cube, maybe 'None' if overlay_probability_levels=True
        """
        if overlay_probability_levels is True:
            collection = COLLECTION_PROB
        else:
            collection = self.input_data.get_value(InputType.COLLECTION)

        cube = self._load_cubes(
            file_list, climatology, overlay_probability_levels, collection
        )

        LOG.debug("Concatenated cube:\n%s", cube)

        if climatology is True:
            # generate a time slice constraint based on the baseline
            time_slice_constraint = self._time_slice_selector(True)
        else:
            # generate a time slice constraint
            time_slice_constraint = self._time_slice_selector(False)
        if time_slice_constraint is not None:
            cube = cube.extract(time_slice_constraint)

        if cube is None:
            if time_slice_constraint is not None:
                LOG.warning(
                    "Time slice constraint resulted in no cubes being " "returned: %s",
                    time_slice_constraint,
                )
            raise UKCPDPDataNotFoundException(
                "Selection constraints resulted in no data being" " selected"
            )

        # generate a temporal constraint
        temporal_constraint = self._get_temporal_selector()
        if temporal_constraint is not None:
            cube = cube.extract(temporal_constraint)

        if cube is None:
            if temporal_constraint is not None:
                LOG.warning(
                    "Temporal constraint resulted in no cubes being " "returned: %s",
                    temporal_constraint,
                )
            raise UKCPDPDataNotFoundException(
                "Selection constraints resulted in no data being" " selected"
            )

        # extract 10, 50 and 90 percentiles
        if overlay_probability_levels is True:
            cube = get_probability_levels(cube, False)

        # generate an area constraint
        area_constraint = self._get_spatial_selector(cube, collection)
        if area_constraint is not None:
            cube = cube.extract(area_constraint)
            if self.input_data.get_area_type() == AreaType.BBOX:
                # Make sure we still have x, y dimension coordinated for
                # bboxes
                cube = self._promote_x_y_coords(cube)

        if cube is None:
            if area_constraint is not None:
                LOG.warning(
                    "Area constraint resulted in no cubes being " "returned: %s",
                    area_constraint,
                )
            raise UKCPDPDataNotFoundException(
                "Selection constraints resulted in no data being" " selected"
            )

        return cube

    def _load_cubes(
        self, file_list, climatology, overlay_probability_levels, collection
    ):
        """
        Get an iris cube based on the given files.

        @param file_list (list[str]): a list of file name to retrieve data from
        @param climatology (boolean): if True extract the climatology data
        @param overlay_probability_levels (boolean): if True only include the
            10th, 50th and 90th percentile data
        @param collection(str): the name of the collection being processed

        @return an iris cube, maybe 'None' if overlay_probability_levels=True
        """
        if climatology is True:
            LOG.info("_load_cubes for climatology")
        elif overlay_probability_levels is True:
            LOG.info("_load_cubes, overlay probability levels")
        else:
            LOG.info("_load_cubes")

        if LOG.getEffectiveLevel() == logging.DEBUG:
            LOG.debug("_load_cubes from %s files", len(file_list))
            for fpath in file_list:
                LOG.debug(" - FILE: %s", fpath)

        if (
            collection == COLLECTION_PROB
            and self.input_data.get_value(InputType.GWL) is not None
        ):
            return self._load_cubes_prob_gwl(file_list)
        else:
            return self._load_cubes_standard(
                file_list, overlay_probability_levels, collection
            )

    def _load_cubes_prob_gwl(self, file_list):
        """
        Get an iris cube based on the given files.

        @param file_list (list[str]): a list of file name to retrieve data from

        @return an iris cube
        """
        LOG.info("_load_cubes_prob_gwl")

        # Load the cubes
        cubes = CubeList()
        try:
            for file_path in file_list:
                LOG.debug(" - FILE: %s", file_path)
                f_list = glob.glob(file_path)

                cube_list = []
                for nc_file in f_list:
                    LOG.debug(" - file: %s", nc_file)
                    cube_list.append(iris.load(nc_file, CUBE_NAME_MAPPING))
                    LOG.debug(" - cube appended")
                cubes.extend(cube_list)
        except IOError as ex:
            for file_name in file_list:
                file_name = file_name.split("*")[0]
                if not path.exists(file_name):
                    LOG.error("File not found: %s", file_name)
            raise UKCPDPDataNotFoundException from ex

        try:
            cube = cubes.concatenate_cube()
        except iris.exceptions.ConcatenateError as ex:
            LOG.error("Failed to concatenate cubes:\n%s\n%s", ex, cubes)

            # pylint: disable=W0707
            raise UKCPDPDataNotFoundException(
                "No data found for given selection options"
            )

        return cube

    def _load_cubes_standard(self, file_list, overlay_probability_levels, collection):
        """
        Get an iris cube based on the given files.

        @param file_list (list[str]): a list of file name to retrieve data from
        @param overlay_probability_levels (boolean): if True only include the
            10th, 50th and 90th percentile data
        @param collection(str): the name of the collection being processed

        @return an iris cube, maybe 'None' if overlay_probability_levels=True
        """
        LOG.info("_load_cubes_prob_gwl")

        # Load the cubes
        cubes = CubeList()
        try:
            for file_path in file_list:
                LOG.debug(" - FILE: %s", file_path)
                f_list = glob.glob(file_path)

                cube_list = []
                for nc_file in f_list:
                    LOG.debug(" - file: %s", nc_file)
                    cube_list.append(_load_cube(nc_file))
                    LOG.debug(" - cube appended")
                cubes.extend(cube_list)

        except IOError as ex:
            if overlay_probability_levels is True:
                # not all variables have corresponding probabilistic data
                return None
            for file_name in file_list:
                file_name = file_name.split("*")[0]
                if not path.exists(file_name):
                    LOG.error("File not found: %s", file_name)
            raise UKCPDPDataNotFoundException from ex

        # Remove time_bnds cubes
        if collection == COLLECTION_PROB:
            unfiltered_cubes = cubes
            cubes = CubeList()
            for cube in unfiltered_cubes:
                if cube.name() != "time_bnds":
                    cubes.append(cube)

        # Different creation dates will stop cubes concatenating, so lets
        # remove them
        for cube in cubes:
            coords = cube.coords(var_name="creation_date")
            for coord in coords:
                cube.remove_coord(coord)

        if len(cubes) == 0:
            LOG.warning("No data was retrieved from the following files:%s", file_list)
            raise UKCPDPDataNotFoundException(
                "No data found for given selection options"
            )

        LOG.debug("First cube:\n%s", cubes[0])
        LOG.debug("Concatenate cubes:\n%s", cubes)

        iris.experimental.equalise_cubes.equalise_attributes(cubes)
        unify_time_units(cubes)

        try:
            cube = cubes.concatenate_cube()
        except iris.exceptions.ConcatenateError as ex:
            LOG.error("Failed to concatenate cubes:\n%s\n%s", ex, cubes)
            error_cubes = CubeList()
            for error_cube in cubes:
                error_cubes.append(error_cube)
                try:
                    LOG.info(
                        "Appending %s", error_cube.coord("ensemble_member_id").points[0]
                    )
                except iris.exceptions.CoordinateNotFoundError:
                    pass
                try:
                    error_cubes.concatenate_cube()
                except iris.exceptions.ConcatenateError as ex:
                    message = ""
                    try:
                        message = " {}".format(
                            error_cube.coord("ensemble_member_id").points[0]
                        )
                    except iris.exceptions.CoordinateNotFoundError:
                        pass
                    LOG.error(
                        "Error when concatenating cube%s:\n%s\n%s",
                        message,
                        ex,
                        error_cube,
                    )
                    break

            # pylint: disable=W0707
            raise UKCPDPDataNotFoundException(
                "No data found for given selection options"
            )

        return cube

    def _convert_to_percentiles_from_ensembles(self, cube):
        # generate the 10th,50th and 90th percentiles for the ensembles
        LOG.debug("convert to percentiles")
        result = cube.collapsed(
            "ensemble_member", iris.analysis.PERCENTILE, percent=[10, 50, 90]
        )
        result.coord("percentile_over_ensemble_member").long_name = "percentile"
        return result

    def _get_spatial_selector(self, cube, collection):
        LOG.debug("_get_spatial_selector")
        # generate an area constraint
        area_constraint = None

        if self.input_data.get_area_type() == AreaType.POINT:
            # coordinates are coming in as OSGB, x, y
            bng_x = self.input_data.get_area()[0]
            bng_y = self.input_data.get_area()[1]
            x_constraint = iris.Constraint(projection_x_coordinate=bng_x)
            y_constraint = iris.Constraint(projection_y_coordinate=bng_y)
            area_constraint = x_constraint & y_constraint

        elif self.input_data.get_area_type() == AreaType.BBOX:
            # coordinates are coming in as OSGB, w, s, e, n
            resolution = get_spatial_resolution_m(cube)
            half_grid_size = resolution / 2
            bng_w = self.input_data.get_area()[0]
            bng_s = self.input_data.get_area()[1]
            bng_e = self.input_data.get_area()[2]
            bng_n = self.input_data.get_area()[3]
            x_constraint = iris.Constraint(
                projection_x_coordinate=lambda cell: (bng_w - half_grid_size)
                < cell.point
                < (bng_e + half_grid_size)
            )
            y_constraint = iris.Constraint(
                projection_y_coordinate=lambda cell: (bng_s - half_grid_size)
                < cell.point
                < (bng_n + half_grid_size)
            )
            area_constraint = x_constraint & y_constraint

        elif self.input_data.get_area_type() in [
            AreaType.COAST_POINT,
            AreaType.GAUGE_POINT,
        ]:
            # coordinates are coming in as lat, long
            # TODO half_grid_size = ?
            half_grid_size = 0.05
            latitude = self.input_data.get_area()[0]
            longitude = self.input_data.get_area()[1]
            latitude_constraint = iris.Constraint(
                latitude=lambda cell: (latitude - half_grid_size)
                <= cell
                < (latitude + half_grid_size)
            )
            longitude_constraint = iris.Constraint(
                longitude=lambda cell: (longitude - half_grid_size)
                <= cell
                < (longitude + half_grid_size)
            )
            area_constraint = latitude_constraint & longitude_constraint

        elif self.input_data.get_area_type() == AreaType.ADMIN_REGION:
            if self.input_data.get_area() != "all":
                if collection in [
                    COLLECTION_CPM,
                    COLLECTION_DERIVED,
                    COLLECTION_GCM,
                    COLLECTION_RCM,
                    COLLECTION_RCM_GWL,
                ]:
                    area_constraint = iris.Constraint(
                        Region=self.input_data.get_area_label()
                    )
                else:
                    area_constraint = iris.Constraint(
                        coord_values={
                            "Administrative Region": self.input_data.get_area_label()
                        }
                    )

        elif self.input_data.get_area_type() == AreaType.COUNTRY:
            if self.input_data.get_area() != "all":
                area_constraint = iris.Constraint(
                    Country=self.input_data.get_area_label()
                )

        elif self.input_data.get_area_type() == AreaType.RIVER_BASIN:
            if self.input_data.get_area() != "all":

                if self.input_data.get_area_label() == "Orkney and Shetland":
                    basin = "Orkney and Shetlands"
                else:
                    basin = self.input_data.get_area_label()

                if collection in [
                    COLLECTION_CPM,
                    COLLECTION_DERIVED,
                    COLLECTION_GCM,
                    COLLECTION_RCM,
                    COLLECTION_RCM_GWL,
                ]:
                    area_constraint = iris.Constraint(River=basin)
                else:
                    area_constraint = iris.Constraint(
                        coord_values={"River Basin": basin}
                    )
        else:
            raise UKCPDPInvalidParameterException(
                "Unknown area type: {}.".format(self.input_data.get_area_type())
            )

        return area_constraint

    def _get_temporal_selector(self):
        LOG.debug("_get_temporal_selector")
        # generate a temporal constraint
        temporal_constraint = None
        temporal_average_type = self.input_data.get_value(
            InputType.TEMPORAL_AVERAGE_TYPE
        )

        if self.input_data.get_value(
            InputType.TIME_PERIOD
        ) == "all" or temporal_average_type in [
            TemporalAverageType.HOURLY,
            TemporalAverageType.THREE_HOURLY,
            TemporalAverageType.DAILY,
            TemporalAverageType.ANNUAL,
            None,
        ]:
            # we want everything, so no need to add a restriction
            pass

        elif temporal_average_type == TemporalAverageType.MONTHLY:
            for i, term in enumerate(get_months()):
                if term == self.input_data.get_value(InputType.TIME_PERIOD):
                    # i is the index not the month number
                    temporal_constraint = iris.Constraint(
                        time=lambda t: i < t.point.month <= i + 1
                    )
                    LOG.debug("Constraint(%s <= t.point.month <= %s)", i, i + 1)
                    break

        elif temporal_average_type == TemporalAverageType.SEASONAL:
            if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
                temporal_constraint = iris.Constraint(
                    clim_season=self.input_data.get_value(InputType.TIME_PERIOD)
                )
                LOG.debug(
                    "Constraint(clim_season=%s)",
                    self.input_data.get_value(InputType.TIME_PERIOD),
                )
            else:
                temporal_constraint = iris.Constraint(
                    season=self.input_data.get_value(InputType.TIME_PERIOD)
                )
                LOG.debug(
                    "Constraint(season=%s)",
                    self.input_data.get_value(InputType.TIME_PERIOD),
                )

        else:
            raise UKCPDPInvalidParameterException(
                "Unknown temporal average type: {}.".format(
                    self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)
                )
            )

        return temporal_constraint

    def _time_slice_selector(self, baseline):
        LOG.debug("_time_slice_selector")
        # generate a time slice constraint
        time_slice_constraint = None
        year_max = None

        if baseline is True:
            year_min, year_max = get_baseline_range(
                self.input_data.get_value(InputType.BASELINE)
            )

        elif self.input_data.get_value(InputType.TIME_SLICE_TYPE) == "20y":
            year_min, year_max = self._get_20y_range()

        elif self.input_data.get_value(InputType.TIME_SLICE_TYPE) == "30y":
            year_min, year_max = self._get_30y_range()

        else:
            if self.input_data.get_value(InputType.YEAR) is not None:
                # year
                year_min = self.input_data.get_value(InputType.YEAR)
                if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
                    year_max = self.input_data.get_value(InputType.YEAR)
                else:
                    year_max = self.input_data.get_value(InputType.YEAR) + 1
            else:
                # year_minimum, year_maximum
                year_min = self.input_data.get_value(InputType.YEAR_MINIMUM)
                year_max = self.input_data.get_value(InputType.YEAR_MAXIMUM)

        if year_max is not None:
            # we have some form of time slice
            if self.input_data.get_value(InputType.GWL) is not None:
                # We start from December in the previous year
                year_min = year_min - 1
                pdt1 = PartialDateTime(year=year_min, month=12)
                pdt2 = PartialDateTime(year=year_max, month=12)
                time_slice_constraint = iris.Constraint(
                    time=lambda cell: pdt1 <= cell.point < pdt2
                )
                LOG.debug("Constraint(%s <= t.point.year < %s)", pdt1, pdt2)

            elif self.input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
                time_slice_constraint = iris.Constraint(
                    time=lambda t: year_min <= t.point.year <= year_max
                )
                LOG.debug("Constraint(%s <= t.point.year <= %s)", year_min, year_max)
            else:
                time_slice_constraint = iris.Constraint(
                    time=lambda t: year_min <= t.point.year < year_max
                )
                LOG.debug("Constraint(%s <= t.point.year < %s)", year_min, year_max)

        return time_slice_constraint

    def _get_20y_range(self):
        year_min = self.input_data.get_value(InputType.YEAR_MINIMUM) + 8
        year_max = self.input_data.get_value(InputType.YEAR_MAXIMUM) - 8
        return year_min, year_max

    def _get_30y_range(self):
        year_min = self.input_data.get_value(InputType.YEAR_MINIMUM) + 12
        year_max = self.input_data.get_value(InputType.YEAR_MAXIMUM) - 12
        return year_min, year_max

    def _promote_x_y_coords(self, cube):
        # ensure the x and y coordinates are dimension coordinates
        dim_coords = []
        for coord in cube.coords(dim_coords=True):
            dim_coords.append(coord.name())

        # no x coordinate
        if "projection_x_coordinate" not in dim_coords:
            # no x or y coordinate
            if "projection_y_coordinate" not in dim_coords:
                # add the y coordinate and mark it as one from the end
                cube = iris.util.new_axis(cube, "projection_y_coordinate")
                dimension_order = list(range(2, len(dim_coords) + 2))
                dimension_order.append(1)
            else:
                dimension_order = list(range(1, len(dim_coords) + 1))

            # add the x coordinate and mark it as the end coordinate
            cube = iris.util.new_axis(cube, "projection_x_coordinate")
            dimension_order.append(0)
            cube.transpose(dimension_order)

        # no y coordinate
        elif "projection_y_coordinate" not in dim_coords:
            # add the y coordinate and add it before the y coordinate
            cube = iris.util.new_axis(cube, "projection_y_coordinate")
            dimension_order = list(range(1, len(dim_coords) + 1))

            # find the x coordinate
            for ind, coord in enumerate(dim_coords):
                if coord == "projection_x_coordinate":
                    x_index = ind
                    break
            dimension_order.insert(x_index, 0)
            cube.transpose(dimension_order)

        return cube

    def get_title(self):
        """
        Generate the title for the data.

        @return a str containing the title
        """
        LOG.debug("get_title")

        # user defined title?
        if (
            self.input_data.get_value(InputType.PLOT_TITLE) is not None
            and self.input_data.get_value(InputType.PLOT_TITLE) != ""
        ):
            return self.input_data.get_value(InputType.PLOT_TITLE)

        variable = " and ".join(self.input_data.get_value_label(InputType.VARIABLE))
        if self.input_data.get_value(InputType.VARIABLE)[0] in ["hursAnom", "hussAnom"]:
            variable = "percentage {variable}".format(variable=variable)

        if self.input_data.get_value(InputType.RETURN_PERIOD) is not None:
            title = "{variable} for {time_period} in".format(
                time_period=self.input_data.get_value_label(InputType.TIME_PERIOD),
                variable=variable,
            )

        elif (
            self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE)
            == TemporalAverageType.ANNUAL
            or self.input_data.get_value(InputType.TIME_PERIOD) == "all"
        ):
            title = "{temporal_type} average {variable} for".format(
                temporal_type=self.input_data.get_value_label(
                    InputType.TEMPORAL_AVERAGE_TYPE
                ),
                variable=variable,
            )

        elif self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) is None:
            title = "{variable} for".format(variable=variable)

        else:
            title = "{temporal_type} average {variable} for {time_period} in".format(
                temporal_type=self.input_data.get_value_label(
                    InputType.TEMPORAL_AVERAGE_TYPE
                ),
                time_period=self.input_data.get_value_label(InputType.TIME_PERIOD),
                variable=variable,
            )

        if self.input_data.get_value(
            InputType.YEAR_MINIMUM
        ) == self.input_data.get_value(InputType.YEAR_MAXIMUM):
            title = "{t} {year}".format(
                t=title, year=self.input_data.get_value(InputType.YEAR)
            )
        else:
            start_year = self.input_data.get_value(InputType.YEAR_MINIMUM)
            end_year = self.input_data.get_value(InputType.YEAR_MAXIMUM)
            if self.input_data.get_value(InputType.COLLECTION) != COLLECTION_OBS:
                end_year = end_year - 1
            title = "{t} years {start_year} up to and including {end_year},".format(
                t=title, start_year=start_year, end_year=end_year
            )

        if self.input_data.get_value(InputType.RETURN_PERIOD) is not None:
            title = "{t} for a return period of {return_period},".format(
                t=title,
                return_period=self.input_data.get_value(InputType.RETURN_PERIOD),
            )

        if self.input_data.get_area_type() == AreaType.POINT:
            grid_x = int(self.cubes[0].coord("projection_x_coordinate").points[0])
            grid_y = int(self.cubes[0].coord("projection_y_coordinate").points[0])
            title = "{t} for grid square {x}, {y}".format(t=title, x=grid_x, y=grid_y)

        elif self.input_data.get_area_type() == AreaType.BBOX:
            x_bounds = self.cubes[0].coord("projection_x_coordinate").bounds
            y_bounds = self.cubes[0].coord("projection_y_coordinate").bounds
            grid_x1 = int(x_bounds[0][0])
            grid_y1 = int(y_bounds[0][0])
            grid_x2 = int(x_bounds[-1][1])
            grid_y2 = int(y_bounds[-1][1])
            title = "{t} in area {x1}, {y1} to {x2}, {y2}".format(
                t=title, x1=grid_x1, y1=grid_y1, x2=grid_x2, y2=grid_y2
            )

        elif self.input_data.get_area_type() in [
            AreaType.COAST_POINT,
            AreaType.GAUGE_POINT,
        ]:
            # coordinates are coming in as lat, long
            latitude = str(round(self.cubes[0].coord("latitude").points[0], 2))
            longitude = str(round(self.cubes[0].coord("longitude").points[0], 2))
            title = "{t} for grid square {latitude}°, {longitude}°".format(
                t=title, latitude=latitude, longitude=longitude
            )

        else:
            area = self.input_data.get_area_label()
            area = area.replace("All ", "all ")
            title = "{t} in {area}".format(t=title, area=area)

        # add baseline
        if self.input_data.get_value(InputType.BASELINE) is not None:
            title = "{t}, using baseline {baseline}".format(
                t=title, baseline=self.input_data.get_value_label(InputType.BASELINE)
            )

        try:
            # add scenario, if only one of them. If len > 1 then the scenarios will
            # be on the plot legend
            scenario = self.input_data.get_value_label(InputType.SCENARIO)
            if len(scenario) == 1:
                title = "{t}, and scenario {scenario}".format(
                    t=title, scenario=scenario[0]
                )
        except KeyError:
            # there is no scenario for the Had Grid Obs data
            pass

        return title


def get_probability_levels(cube, extended_range):
    """
    Extract a the 10th, 50th and 90th percentiles from a cube and optionally
    the 5th, 25th, 75th and 95th dependent on extended_range

    @param cube(Cube): the original data
    @param extended_range(boolean): if True also return the 5th, 25th, 75th
                and 95th

    @return a cube containing the 10th, 50th and 90th percentiles and
                optionally the 5th, 25th, 75th and 95th
    """
    LOG.debug("get_probability_levels")
    percentile_cubes = iris.cube.CubeList()
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=10)))
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=50)))
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=90)))

    if extended_range is True:
        percentile_cubes.append(cube.extract(iris.Constraint(percentile=5)))
        percentile_cubes.append(cube.extract(iris.Constraint(percentile=25)))
        percentile_cubes.append(cube.extract(iris.Constraint(percentile=75)))
        percentile_cubes.append(cube.extract(iris.Constraint(percentile=95)))

    return percentile_cubes.merge_cube()


def timeout(seconds=10):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def handle_timeout(signum, frame):
                raise TimeoutError()

            signal.signal(signal.SIGALRM, handle_timeout)
            signal.alarm(seconds)
            result = func(*args, **kwargs)
            signal.alarm(0)
            return result

        return wrapper

    return decorator


@timeout(seconds=IRIS_LOAD_TIMEOUT_SECONDS)
def _load_cube(filename):
    try:
        cube = iris.load_cube(filename)
    except TimeoutError:
        LOG.error(f"Timeout accessing {filename}")
        raise UKCPDPDataNotFoundException("Timeout error accessing file")
    return cube
