from ukcp_dp.constants import ANNUAL, DATA_SOURCE_PROB, InputType, \
    MONTHLY, SEASONAL, TEMP_ANOMS
from ukcp_dp.ukcp_common_analysis.common_analysis import make_climatology, \
    make_anomaly
from ukcp_dp.vocab_manager import get_months
import cf_units
import iris
import iris.plot as iplt
import iris.quickplot as qplt

import logging
log = logging.getLogger(__name__)


class DataExtractor():
    """
    Extract data from a list of files and filter it based on user selection
    criteria.
    """

    def __init__(self, file_lists, input_data):
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
        """
        self.file_lists = file_lists
        self.input_data = input_data
        self.cubes = self._get_main_cubes()
        self.overlay_cube = self._get_overlay_cube()

    def get_cubes(self):
        """
        Get an iris cube list.

        The data are based on the selection criteria from the input_data.

        @return an iris cube list, one cube per scenario, per variable
        """
        log.info('get_cubes')
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

        If the variable type is an anomaly then then a climatology may be need
        to be produced in order to generate the anomalies.

        @return an iris cube list containing the main data, one cube per
            scenario, per variable
        """
        cubes = iris.cube.CubeList()

        for variable in self.file_lists['main'].keys():
            # for each variable there is a list of files per scenario
            for file_list in self.file_lists['main'][variable]:

                if (variable.endswith('Anom') and
                        self.input_data.get_value(InputType.DATA_SOURCE) !=
                        DATA_SOURCE_PROB):
                    # we need anomalies so lets calculate them
                    # TODO we may get these directly from file in future
                    cube = self._get_anomaly_cube(file_list, variable)

                else:
                    # we can use the values directly from the file
                    cube = self._get_cube(file_list)

                # do we need to convert percentiles?
                if self.input_data.get_value(InputType.CONVERT_TO_PERCENTILES):
                    cube = (self._convert_to_percentiles_from_ensembles(cube))

                if variable in TEMP_ANOMS:
                    # this in an anomaly so set the units to Celsius, otherwise
                    # they will get converted later and that would be bad
                    cube.units = cf_units.Unit("Celsius")
                    log.debug('updated cube units to Celsius')

                cubes.append(cube)

        log.debug(cubes)

        return cubes

    def _get_anomaly_cube(self, file_list, variable):
        # anomalies have been selected for something other than LS1,
        # therefore we need to calculate the climatology using the
        # baseline and then the anomalies
        cube_absoute = self._get_cube(file_list)

        cube_baseline = self._get_cube(file_list, baseline=True)

        cube_climatology = make_climatology(
            cube_baseline, climtype=self.input_data.get_value_label(
                InputType.TEMPORAL_AVERAGE_TYPE).lower())
        if (self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) ==
                MONTHLY or
            self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) ==
                SEASONAL):
            # we have to collapse the time coord so the dimensions match those
            # of the cube_absoute
            cube_climatology = cube_climatology.collapsed(
                'time', iris.analysis.MEAN)

        # we need to remove these to be able to make the anomaly
        for coord in ['month', 'month_number', 'season']:
            try:
                cube_climatology.remove_coord(coord)
            except iris.exceptions.CoordinateNotFoundError:
                pass

        percent_anomalies = ['hussAnom', 'prAnom', 'rain5DayAccumMaxAnom',
                             'petAnom']
        if variable in percent_anomalies:
            preferred_unit = cf_units.Unit("%")
        else:
            preferred_unit = None

        cube_anomaly = make_anomaly(
            cube_absoute, cube_climatology, preferred_unit)

        # add the attributes back in and add info about the baseline and
        # anomaly
        cube_anomaly.attributes = cube_absoute.attributes
        cube_anomaly.attributes['baseline_period'] = (
            self.input_data.get_value(InputType.BASELINE))
        cube_anomaly.attributes['anomaly_type'] = 'relative_change'

        return cube_anomaly

    def _get_overlay_cube(self):
        """
        Get an iris cube based on the given files and using selection criteria
        from the input_data.

        The cube produced containing the 10th, 50th and 90th percentiles.

        @return an iris cube, maybe 'None'
        """
        overlay_cube = None
        if (self.input_data.get_value(InputType.DATA_SOURCE) !=
                DATA_SOURCE_PROB and
            self.input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is
                True):

            for variable in self.file_lists['overlay'].keys():
                # for each variable there is a list of files per scenario
                for file_list in self.file_lists['overlay'][variable]:

                    overlay_cube = (self._get_cube(
                        file_list, overlay_probability_levels=True))
                    if variable in TEMP_ANOMS:
                        overlay_cube.units = cf_units.Unit("Celsius")

        log.debug('Overlay cube: {}'.format(overlay_cube))

        return overlay_cube

    def _get_cube(self, file_list, baseline=False,
                  overlay_probability_levels=False):
        """
        Get an iris cube based on the given files using selection criteria
        from the input_data.

        @param file_list (list[str]): a list of file name to retrieve data from
        @param baseline (boolean): if True calculate the baseline data
        @param overlay_probability_levels (boolean): if True only include the
            10th, 50th and 90th percentile data

        @return an iris cube
        """
        # Load the cubes
        cubes = iris.load(file_list)

        # Remove attribute ensemble_member_id to allow us to merge cubes
        if (self.input_data.get_value(InputType.DATA_SOURCE) !=
                DATA_SOURCE_PROB):
            for cube in cubes:
                try:
                    del cube.metadata.attributes['ensemble_member']
                except KeyError:
                    pass

        cubes = iris.cube.CubeList(cubes)

        cube = cubes.concatenate_cube()

        if baseline is True:
            # generate a time slice constraint based on the baseline
            time_slice_constraint = self._time_slice_selector(True)
        else:
            # generate a time slice constraint
            time_slice_constraint = self._time_slice_selector(False)
        if time_slice_constraint is not None:
            with iris.FUTURE.context(cell_datetime_objects=True):
                cube = cube.extract(time_slice_constraint)

        if cube is None:
            raise Exception('Selection constraints resulted in no data being'
                            ' selected')

        # generate a temporal constraint
        temporal_constraint = self._get_temporal_selector()
        if temporal_constraint is not None:
            with iris.FUTURE.context(cell_datetime_objects=True):
                cube = cube.extract(temporal_constraint)

        if cube is None:
            raise Exception('Selection constraints resulted in no data being'
                            ' selected')

        # extract 10, 50 and 90 percentiles
        if (overlay_probability_levels is True):
            cube = get_probability_levels(cube)

        # generate an area constraint
        area_constraint = self._get_spatial_selector(cube)
        if area_constraint is not None:
            cube = cube.extract(area_constraint)

        if cube is None:
            raise Exception('Selection constraints resulted in no data being'
                            ' selected')

        return cube

    def _convert_to_percentiles_from_ensembles(self, cube):
        # generate the 10th,50th and 90th percentiles for the ensembles
        result = cube.collapsed('Ensemble member', iris.analysis.PERCENTILE,
                                percent=[10, 50, 90])
        result.coord(
            'percentile_over_Ensemble member').long_name = 'percentile'
        return result

    def _get_spatial_selector(self, cube):
        # generate an area constraint
        area_constraint = None

        if self.input_data.get_area_type() == 'point':
            # coordinates are coming in as OSGB, x, y
            resolution = self._get_resolution_m(cube)
            half_grid_size = resolution / 2
            bng_x = self.input_data.get_area()[0]
            bng_y = self.input_data.get_area()[1]
            x_constraint = iris.Constraint(
                projection_x_coordinate=lambda cell:
                (bng_x - half_grid_size) <= cell < (bng_x + half_grid_size))
            y_constraint = iris.Constraint(
                projection_y_coordinate=lambda cell:
                (bng_y - half_grid_size) <= cell < (bng_y + half_grid_size))
            area_constraint = x_constraint & y_constraint

        elif self.input_data.get_area_type() == 'bbox':
            # coordinates are coming in as OSGB, w, s, e, n
            resolution = self._get_resolution_m(cube)
            half_grid_size = resolution / 2
            bng_w = self.input_data.get_area()[0]
            bng_s = self.input_data.get_area()[1]
            bng_e = self.input_data.get_area()[2]
            bng_n = self.input_data.get_area()[3]
            x_constraint = iris.Constraint(
                projection_x_coordinate=lambda cell:
                (bng_w - half_grid_size) <= cell < (bng_e + half_grid_size))
            y_constraint = iris.Constraint(
                projection_y_coordinate=lambda cell:
                (bng_s - half_grid_size) <= cell < (bng_n + half_grid_size))
            area_constraint = x_constraint & y_constraint

        elif (self.input_data.get_area_type() == 'admin_region' or
                self.input_data.get_area_type() == 'country' or
                self.input_data.get_area_type() == 'river_basin'):

            if self.input_data.get_area() != 'all':
                area_constraint = iris.Constraint(
                    region=self.input_data.get_area())
        else:
            raise Exception(
                "Unknown area type: {}.".format(
                    self.input_data.get_area_type()))

        return area_constraint

    def _get_temporal_selector(self):
        # generate a temporal constraint
        temporal_constraint = None
        temporal_average_type = self.input_data.get_value(
            InputType.TEMPORAL_AVERAGE_TYPE)

        if (self.input_data.get_value(InputType.TIME_PERIOD) == 'all' or
                temporal_average_type == ANNUAL):
            # we want everything, so no need to add a restriction
            pass

        elif temporal_average_type == MONTHLY:
            for i, term in enumerate(
                    get_months()):
                if term == self.input_data.get_value(InputType.TIME_PERIOD):
                    # i is the index not the month number
                    temporal_constraint = iris.Constraint(
                        time=lambda t: i < t.point.month <= i + 1)
                    break

        elif temporal_average_type == SEASONAL:
            temporal_constraint = iris.Constraint(
                clim_season=self.input_data.get_value(InputType.TIME_PERIOD))

        else:
            raise Exception(
                "Unknown temporal average type: {}.".format(
                    self.input_data.get_value(
                        InputType.TEMPORAL_AVERAGE_TYPE)))

        return temporal_constraint

    def _time_slice_selector(self, baseline):
        # generate a time slice constraint
        time_slice_constraint = None
        year_max = None

        if baseline is True:
            year_min = int(self.input_data.get_value(
                InputType.BASELINE).split('-')[0])
            year_max = int(self.input_data.get_value(
                InputType.BASELINE).split('-')[1])
        else:
            try:
                # year
                year_min = self.input_data.get_value(InputType.YEAR)
                year_max = self.input_data.get_value(InputType.YEAR) + 1
            except KeyError:
                # year_minimum, year_maximum
                year_min = self.input_data.get_value(InputType.YEAR_MINIMUM)
                year_max = self.input_data.get_value(InputType.YEAR_MAXIMUM)

        if year_max is not None:
            # we have some form of time slice
            time_slice_constraint = iris.Constraint(
                time=lambda t: year_min <= t.point.year < year_max)

        return time_slice_constraint

    def get_title(self):
        """
        Generate the title for the data.

        @return a str containing the title
        """
        if (self.input_data.get_value(
                InputType.TEMPORAL_AVERAGE_TYPE) == ANNUAL
                or self.input_data.get_value(InputType.TIME_PERIOD) == 'all'):
            title = ('Demonstration Version - {temporal_type} average '
                     '{variable}\n'
                     'for'.format(
                         temporal_type=self.input_data.get_value_label(
                             InputType.TEMPORAL_AVERAGE_TYPE),
                         variable=" and ".join(self.input_data.get_value_label(
                             InputType.VARIABLE))))
        else:
            title = ('Demonstration Version - {temporal_type} average '
                     '{variable} for\n'
                     '{time_period} in'.format(
                         temporal_type=self.input_data.get_value_label(
                             InputType.TEMPORAL_AVERAGE_TYPE),
                         time_period=self.input_data.get_value_label(
                             InputType.TIME_PERIOD),
                         variable=" and ".join(self.input_data.get_value_label(
                             InputType.VARIABLE))))

        if (self.input_data.get_value(InputType.YEAR_MINIMUM) ==
                self.input_data.get_value(InputType.YEAR_MAXIMUM)):
            title = '{t} {year}'.format(
                t=title, year=self.input_data.get_value(InputType.YEAR))
        else:
            start_year = self.input_data.get_value(InputType.YEAR_MINIMUM)
            end_year = self.input_data.get_value(InputType.YEAR_MAXIMUM)
            title = '{t} {start_year} to {end_year}'.format(
                t=title, start_year=start_year, end_year=end_year)

        if self.input_data.get_area_type() == 'point':
            grid_x = (self.cubes[0].coord('projection_x_coordinate')
                      .bounds[0][0])
            grid_y = (self.cubes[0].coord('projection_y_coordinate')
                      .bounds[0][0])
            title = "{t} for grid square {x}, {y}".format(
                t=title, x=grid_x, y=grid_y)

        elif self.input_data.get_area_type() == 'bbox':
            x_bounds = self.cubes[0].coord('projection_x_coordinate').bounds
            y_bounds = self.cubes[0].coord('projection_y_coordinate').bounds
            grid_x1 = (x_bounds[0][0])
            grid_y1 = (y_bounds[0][0])
            grid_x2 = (x_bounds[-1][1])
            grid_y2 = (y_bounds[-1][1])
            title = "{t} in area {x1}, {y1} to {x2}, {y2}".format(
                t=title, x1=grid_x1, y1=grid_y1, x2=grid_x2, y2=grid_y2)

        else:
            title = "{t} in {area}".format(
                t=title, area=self.input_data.get_area_label())

        return title

    def _get_resolution_m(self, cube):
        resolution = cube.attributes['resolution']
        try:
            return int(resolution.split('km')[0]) * 1000
        except Exception:
            return


def get_probability_levels(cube):
    """
    Extract a the 10, 50 and 90 percentiles from a cube.

    @return a cube containing the 10, 50 and 90 percentiles
    """
    percentile_cubes = iris.cube.CubeList()
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=10)))
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=50)))
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=90)))
    return percentile_cubes.merge_cube()
