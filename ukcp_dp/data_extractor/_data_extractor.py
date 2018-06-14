# -*- coding: utf-8 -*-
import logging

import cf_units
import iris
from iris.cube import CubeList
import iris.plot as iplt
import iris.quickplot as qplt
import iris.experimental.equalise_cubes

from ukcp_dp.constants import DATA_SOURCE_PROB, InputType, TEMP_ANOMS, \
    DATA_SOURCE_MARINE, PERCENTAGE_ANOMALIES, AreaType, TemporalAverageType
from ukcp_dp.ukcp_common_analysis.common_analysis import make_climatology, \
    make_anomaly
from ukcp_dp.vocab_manager import get_months


log = logging.getLogger(__name__)


class DataExtractor(object):
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
        log.debug('DataExtractor __init__ finished')

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

        If a baseline has been provided then a climatology may be need to be
        produced in order to generate the anomalies.

        @return an iris cube list containing the main data, one cube per
            scenario, per variable
        """
        log.debug('_get_main_cubes')
        cubes = iris.cube.CubeList()

        for variable in self.file_lists['main'].keys():
            # for each variable there is a list of files per scenario
            for i, file_list in enumerate(self.file_lists['main'][variable]):

                if (variable.endswith('Anom') and
                        self.input_data.get_value(InputType.DATA_SOURCE) not in
                        [DATA_SOURCE_PROB, DATA_SOURCE_MARINE]):
                    # we need anomalies so lets calculate them
                    # TODO we may get these directly from file in future
                    cube = self._get_anomaly_cube(
                        file_list, self.file_lists['baseline'][variable][i],
                        variable)

                else:
                    # we can use the values directly from the file
                    cube = self._get_cube(file_list)

                # do we need to convert percentiles?
                if ((self.input_data.get_value(
                        InputType.CONVERT_TO_PERCENTILES) is not None) and
                        (self.input_data.get_value(
                            InputType.CONVERT_TO_PERCENTILES) is True)):
                    cube = (self._convert_to_percentiles_from_ensembles(cube))

                if variable in TEMP_ANOMS:
                    # this in an anomaly so set the units to Celsius, otherwise
                    # they will get converted later and that would be bad
                    cube.units = cf_units.Unit("Celsius")
                    log.debug('updated cube units to Celsius')

                cubes.append(cube)

        log.debug(cubes)

        return cubes

    def _get_anomaly_cube(self, file_list, baseline_file_list, variable):
        log.debug('_get_anomaly_cube')
        # anomalies have been selected for something other than LS1,
        # therefore we need to calculate the climatology using the
        # baseline and then the anomalies
        cube_absoute = self._get_cube(file_list)

        cube_baseline = self._get_cube(baseline_file_list, baseline=True)

        cube_climatology = make_climatology(
            cube_baseline, climtype=self.input_data.get_value_label(
                InputType.TEMPORAL_AVERAGE_TYPE).lower())
        if (self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) ==
                TemporalAverageType.MONTHLY or
            self.input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) ==
                TemporalAverageType.SEASONAL):
            # we have to collapse the time coord so the dimensions match those
            # of the cube_absoute
            cube_climatology = cube_climatology.collapsed(
                'time', iris.analysis.MEAN)

        # we need to remove these to be able to make the anomaly
#         for coord in ['month', 'month_number', 'season']:
        for coord in ['month', 'season']:
            try:
                cube_climatology.remove_coord(coord)
            except iris.exceptions.CoordinateNotFoundError:
                pass

        if variable in PERCENTAGE_ANOMALIES:
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
        log.debug('_get_overlay_cube')
        overlay_cube = None
        if (self.input_data.get_value(InputType.DATA_SOURCE) !=
                DATA_SOURCE_PROB and
            self.input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is
                not None and
            self.input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is
                True):

            for variable in self.file_lists['overlay'].keys():
                # for each variable there is a list of files per scenario
                for file_list in self.file_lists['overlay'][variable]:

                    overlay_cube = (self._get_cube(
                        file_list, overlay_probability_levels=True))
                    if variable in TEMP_ANOMS:
                        overlay_cube.units = cf_units.Unit("Celsius")

        log.debug('Overlay cube:\n{}'.format(overlay_cube))

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
        if log.getEffectiveLevel() == logging.DEBUG:
            log.debug('_get_cube from {} files'.format(len(file_list)))
            for fpath in file_list:
                log.debug(' - FILE: {}'.format(fpath))

        # Load the cubes
        try:
            cubes = iris.load(file_list)
        except IOError:
            log.warn('No data was retrieved from the following files:{}'.
                     format(file_list))
            raise Exception('No data found for given selection options')

        # Remove time_bnds cubes
        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB) or overlay_probability_levels is True:
            unfiltered_cubes = cubes
            cubes = CubeList()
            for cube in unfiltered_cubes:
                if cube.name() != 'time_bnds':
                    cubes.append(cube)

        # TODO Temp hack until removed from data
        for cube in cubes:
            coords = cube.coords(var_name='region')
            for coord in coords:
                cube.remove_coord(coord)

        if len(cubes) == 0:
            log.warn('No data was retrieved from the following files:{}'.
                     format(file_list))
            raise Exception('No data found for given selection options')

        log.debug('First cube:\n{}'.format(cubes[0]))
        log.debug('Concatenate cubes:\n{}'.format(cubes))

        iris.experimental.equalise_cubes.equalise_attributes(cubes)
        cube = cubes.concatenate_cube()

        log.debug('Concatenated cube:\n{}'.format(cube))

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
            if time_slice_constraint is not None:
                log.warn('Time slice constraint resulted in no cubes being '
                         'returned: {}'.format(time_slice_constraint))
            raise Exception('Selection constraints resulted in no data being'
                            ' selected')

        # generate a temporal constraint
        temporal_constraint = self._get_temporal_selector()
        if temporal_constraint is not None:
            with iris.FUTURE.context(cell_datetime_objects=True):
                cube = cube.extract(temporal_constraint)

        if cube is None:
            if temporal_constraint is not None:
                log.warn('Temporal constraint resulted in no cubes being '
                         'returned: {}'.format(temporal_constraint))
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
            if area_constraint is not None:
                log.warn('Area constraint resulted in no cubes being '
                         'returned: {}'.format(area_constraint))
            raise Exception('Selection constraints resulted in no data being'
                            ' selected')

        return cube

    def _convert_to_percentiles_from_ensembles(self, cube):
        # generate the 10th,50th and 90th percentiles for the ensembles
        log.debug("convert to percentiles")
        result = cube.collapsed('ensemble_member', iris.analysis.PERCENTILE,
                                percent=[10, 50, 90])
        result.coord(
            'percentile_over_ensemble_member').long_name = 'percentile'
        return result

    def _get_spatial_selector(self, cube):
        log.debug('_get_spatial_selector')
        # generate an area constraint
        area_constraint = None

        print '\n\n\n'
        print self.input_data.get_area_type()
        print self.input_data.get_value(InputType.DATA_SOURCE)
        print '\n\n'
        if self.input_data.get_area_type() == AreaType.POINT:
            # coordinates are coming in as OSGB, x, y
            resolution = self._get_resolution_m(cube)
            half_grid_size = resolution / 2
            bng_x = self.input_data.get_area()[0]
            bng_y = self.input_data.get_area()[1]
            x_constraint = iris.Constraint(
                projection_x_coordinate=lambda cell:
                (bng_x - half_grid_size) <= cell <
                    (bng_x + half_grid_size))
            y_constraint = iris.Constraint(
                projection_y_coordinate=lambda cell:
                (bng_y - half_grid_size) <= cell <
                    (bng_y + half_grid_size))
            area_constraint = x_constraint & y_constraint

        elif self.input_data.get_area_type() == AreaType.BBOX:
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

        elif (self.input_data.get_area_type() in
              [AreaType.COAST_POINT, AreaType.GAUGE_POINT]):
            # coordinates are coming in as lat, long
            # TODO half_grid_size = ?
            half_grid_size = 0.05
            latitude = self.input_data.get_area()[0]
            longitude = self.input_data.get_area()[1]
            latitude_constraint = iris.Constraint(
                latitude=lambda cell:
                (latitude - half_grid_size) <= cell <
                    (latitude + half_grid_size))
            longitude_constraint = iris.Constraint(
                longitude=lambda cell:
                (longitude - half_grid_size) <= cell <
                    (longitude + half_grid_size))
            area_constraint = latitude_constraint & longitude_constraint

        # TODO temp hack for region, due to differences in LS1 and LS2/3

        elif (self.input_data.get_value(InputType.DATA_SOURCE) !=
                DATA_SOURCE_PROB and
                (self.input_data.get_area_type() == AreaType.ADMIN_REGION or
                 self.input_data.get_area_type() == AreaType.COUNTRY or
                 self.input_data.get_area_type() == AreaType.RIVER_BASIN)):
            if self.input_data.get_area() != 'all':
                area_constraint = iris.Constraint(
                    coord_values={
                        'region':
                        self.input_data.get_area_label()})

        elif self.input_data.get_area_type() == AreaType.ADMIN_REGION:
            if self.input_data.get_area() != 'all':
                area_constraint = iris.Constraint(
                    coord_values={
                        'Administrative Region':
                        self.input_data.get_area_label()})

        elif self.input_data.get_area_type() == AreaType.COUNTRY:
            if self.input_data.get_area() != 'all':
                area_constraint = iris.Constraint(
                    Country=self.input_data.get_area_label())

        elif self.input_data.get_area_type() == AreaType.RIVER_BASIN:
            if self.input_data.get_area() != 'all':
                area_constraint = iris.Constraint(
                    coord_values={
                        'River Basin': self.input_data.get_area_label()})

        else:
            raise Exception(
                "Unknown area type: {}.".format(
                    self.input_data.get_area_type()))

        return area_constraint

    def _get_temporal_selector(self):
        log.debug('_get_temporal_selector')
        # generate a temporal constraint
        temporal_constraint = None
        temporal_average_type = self.input_data.get_value(
            InputType.TEMPORAL_AVERAGE_TYPE)

        if (self.input_data.get_value(InputType.TIME_PERIOD) == 'all' or
                temporal_average_type == TemporalAverageType.ANNUAL):
            # we want everything, so no need to add a restriction
            pass

        elif temporal_average_type == TemporalAverageType.MONTHLY:
            for i, term in enumerate(
                    get_months()):
                if term == self.input_data.get_value(InputType.TIME_PERIOD):
                    # i is the index not the month number
                    temporal_constraint = iris.Constraint(
                        time=lambda t: i < t.point.month <= i + 1)
                    break

        elif temporal_average_type == TemporalAverageType.SEASONAL:
            temporal_constraint = iris.Constraint(
                season=self.input_data.get_value(InputType.TIME_PERIOD))

        else:
            raise Exception(
                "Unknown temporal average type: {}.".format(
                    self.input_data.get_value(
                        InputType.TEMPORAL_AVERAGE_TYPE)))

        return temporal_constraint

    def _time_slice_selector(self, baseline):
        log.debug('_time_slice_selector')
        # generate a time slice constraint
        time_slice_constraint = None
        year_max = None

        if baseline is True:
            year_min = int(self.input_data.get_value(
                InputType.BASELINE).split('-')[0])
            year_max = int(self.input_data.get_value(
                InputType.BASELINE).split('-')[1])
        else:
            if self.input_data.get_value(InputType.YEAR) is not None:
                # year
                year_min = self.input_data.get_value(InputType.YEAR)
                year_max = self.input_data.get_value(InputType.YEAR) + 1
            else:
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
        log.debug('get_title')
        variable = " and ".join(self.input_data.get_value_label(
            InputType.VARIABLE)).encode('utf-8')
        if (self.input_data.get_value(
                InputType.TEMPORAL_AVERAGE_TYPE) == TemporalAverageType.ANNUAL
                or self.input_data.get_value(InputType.TIME_PERIOD) == 'all'):
            title = ('Demonstration Version - {temporal_type} average '
                     '{variable}\n'
                     'for'.format(
                         temporal_type=self.input_data.get_value_label(
                             InputType.TEMPORAL_AVERAGE_TYPE),
                         variable=variable))
        else:
            title = ('Demonstration Version - {temporal_type} average '
                     '{variable} for\n'
                     '{time_period} in'.format(
                         temporal_type=self.input_data.get_value_label(
                             InputType.TEMPORAL_AVERAGE_TYPE),
                         time_period=self.input_data.get_value_label(
                             InputType.TIME_PERIOD),
                         variable=variable))

        if (self.input_data.get_value(InputType.YEAR_MINIMUM) ==
                self.input_data.get_value(InputType.YEAR_MAXIMUM)):
            title = '{t} {year}'.format(
                t=title, year=self.input_data.get_value(InputType.YEAR))
        else:
            start_year = self.input_data.get_value(InputType.YEAR_MINIMUM)
            end_year = self.input_data.get_value(InputType.YEAR_MAXIMUM)
            title = '{t} {start_year} to {end_year}'.format(
                t=title, start_year=start_year, end_year=end_year)

        if self.input_data.get_area_type() == AreaType.POINT:
            grid_x = (self.cubes[0].coord('projection_x_coordinate')
                      .bounds[0][0])
            grid_y = (self.cubes[0].coord('projection_y_coordinate')
                      .bounds[0][0])
            title = "{t} for grid square {x}, {y}".format(
                t=title, x=grid_x, y=grid_y)

        elif self.input_data.get_area_type() == AreaType.BBOX:
            x_bounds = self.cubes[0].coord('projection_x_coordinate').bounds
            y_bounds = self.cubes[0].coord('projection_y_coordinate').bounds
            grid_x1 = (x_bounds[0][0])
            grid_y1 = (y_bounds[0][0])
            grid_x2 = (x_bounds[-1][1])
            grid_y2 = (y_bounds[-1][1])
            title = "{t} in area {x1}, {y1} to {x2}, {y2}".format(
                t=title, x1=grid_x1, y1=grid_y1, x2=grid_x2, y2=grid_y2)

        elif (self.input_data.get_area_type() in
              [AreaType.COAST_POINT, AreaType.GAUGE_POINT]):
            # coordinates are coming in as lat, long
            latitude = round(self.cubes[0].coord('latitude').points[0], 2)
#                          .bounds[0][0]) TODO
            longitude = round(self.cubes[0].coord('longitude').points[0], 2)
#                          .bounds[0][0]) TODO
            title = "{t} for grid square {latitude}°, {longitude}°".format(
                t=title, latitude=latitude, longitude=longitude)

        else:
            title = "{t} in {area}".format(
                t=title, area=self.input_data.get_area_label())

        return title.decode('utf-8')

    def _get_resolution_m(self, cube):
        log.debug('_get_resolution_m')
        resolution = cube.attributes['resolution']
        return int(resolution.split('km')[0]) * 1000


def get_probability_levels(cube):
    """
    Extract a the 10, 50 and 90 percentiles from a cube.

    @return a cube containing the 10, 50 and 90 percentiles
    """
    log.debug('get_probability_levels')
    percentile_cubes = iris.cube.CubeList()
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=10)))
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=50)))
    percentile_cubes.append(cube.extract(iris.Constraint(percentile=90)))
    return percentile_cubes.merge_cube()
