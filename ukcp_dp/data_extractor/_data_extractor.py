import iris
import iris.plot as iplt
import iris.quickplot as qplt
from ukcp_dp.constants import InputType
from ukcp_dp.vocab_manager import get_months, get_season_months


class DataExtractor():
    """
    Extract data from a list of files and filter it based on user selection
    criteria.
    """

    def __init__(self, file_lists, input_data):
        """
        Initialise the DataExtractor.

        @param file_lists dict, a dict with two lists of files
            key - 'main' or 'overlay'
            value - list(str) a list of file names
        @param input_data (InputData) an object containing user defined values
        """
        self.file_lists = file_lists
        self.input_data = input_data
        self.cubes = self._get_cubes()

    def get_cubes(self):
        """
        Get a list of iris data cubes based on the given files and using
        selection criteria from the input_data.
        If requested, the second cube will be the 10, 50 and 90 percentiles.

        @return a list of iris data cubes
        """
        return self.cubes

    def _get_cubes(self):
        """
        Get a list of iris data cubes based from the given files using
        selection criteria from the input_data.
        If requested, the second cube will be the 10, 50 and 90 percentiles.

        @return an iris data cube
        """
        cubes = []
        cubes.append(self._get_cube(self.file_lists['main']))

        # show 10, 50 and 90 percentiles
        if (self.input_data.get_value(InputType.SHOW_PROBABILITY_LEVELS) is
                True):
            cubes.append(self._get_cube(self.file_lists['overlay'], True))

        return cubes

    def _get_cube(self, file_list, show_probability_levels=False):
        """
        Get an iris data cube based on the given files using selection
        criteria from the input_data.

        @return an iris data cube
        """

        # Load the cubes based on the variable
        if self.input_data.get_value(InputType.VARIABLE) == 'pr':
            cubes = iris.load(file_list, ["precipitation rate"])
        elif self.input_data.get_value(InputType.VARIABLE) == 'tas':
            cubes = iris.load(file_list, ["air_temperature"])
        else:
            raise Exception(
                "Unknown variable: {}.".format(self.input_data.get_value(
                    InputType.VARIABLE)))

        # Hack as ensemble_member is included as a attribute and coordinate
        ENSEMBLE_MEMBER = 'ensemble_member'
        for cube in cubes:
            try:
                del cube.metadata.attributes[ENSEMBLE_MEMBER]
            except KeyError:
                pass

        cubes = iris.cube.CubeList(cubes)
        cube = cubes.concatenate_cube()

        # generate a time slice constraint
        time_slice_constraint = self._time_slice_selector()
        if time_slice_constraint is not None:
            with iris.FUTURE.context(cell_datetime_objects=True):
                cube = cube.extract(time_slice_constraint)

        # generate a temporal constraint
        temporal_constraint = self._get_temporal_selector()
        if temporal_constraint is not None:
            with iris.FUTURE.context(cell_datetime_objects=True):
                cube = cube.extract(temporal_constraint)

        # generate an area constraint
        area_constraint = self._get_spatial_selector()
        cube = cube.extract(area_constraint)

        # show 10, 50 and 90 percentiles
        if (show_probability_levels is True):
            cube = self._get_probability_levels(cube)

        return cube

    def _get_probability_levels(self, cube):
        # get a cube with the 10, 50 and 90 percentiles
        percentile_cubes = iris.cube.CubeList()
        percentile_cubes.append(cube.extract(iris.Constraint(percentile=10)))
        percentile_cubes.append(cube.extract(iris.Constraint(percentile=50)))
        percentile_cubes.append(cube.extract(iris.Constraint(percentile=90)))
        return percentile_cubes.merge_cube()

    def _get_spatial_selector(self):
        # generate an area constraint
        if self.input_data.get_area_type() == 'point':
            # coordinates are coming in as OSGB, x, y
            bng_x = self.input_data.get_area()[0]
            bng_y = self.input_data.get_area()[1]
            x_constraint = iris.Constraint(
                projection_x_coordinate=lambda cell:
                (bng_x - 12500) <= cell < (bng_x + 12500))
            y_constraint = iris.Constraint(
                projection_y_coordinate=lambda cell:
                (bng_y - 12500) <= cell < (bng_y + 12500))
            area_constraint = x_constraint & y_constraint

        elif self.input_data.get_area_type() == 'bbox':
            # Hack for bbox
            bng_x = 112873.63
            bng_y = 276711.27
            x_constraint = iris.Constraint(
                projection_x_coordinate=lambda cell:
                (bng_x - 12500) <= cell < (bng_x + 12500))
            y_constraint = iris.Constraint(
                projection_y_coordinate=lambda cell:
                (bng_y - 12500) <= cell < (bng_y + 12500))
            area_constraint = x_constraint & y_constraint

        elif (self.input_data.get_area_type() == 'admin_region' or
                self.input_data.get_area_type() == 'country' or
                self.input_data.get_area_type() == 'river_basin'):
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
                temporal_average_type == 'annual'):
            # we want everything, so no need to add a restriction
            pass

        elif temporal_average_type == 'mon':
            for i, term in enumerate(
                    get_months()):
                if term == self.input_data.get_value(InputType.TIME_PERIOD):
                    # i is the index not the month number
                    temporal_constraint = iris.Constraint(
                        time=lambda t: i < t.point.month <= i + 1)
                    break

        elif temporal_average_type == 'seasonal':
            months = get_season_months(
                self.input_data.get_value(InputType.TIME_PERIOD))
            temporal_constraint = iris.Constraint(
                time=lambda t: t.point.month in months)

        else:
            raise Exception(
                "Unknown temporal average type: {}.".format(
                    self.input_data.get_value(
                        InputType.TEMPORAL_AVERAGE_TYPE)))

        return temporal_constraint

    def _time_slice_selector(self):
        # generate a time slice constraint
        time_slice_constraint = None
        year_max = None

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
                InputType.TEMPORAL_AVERAGE_TYPE) == 'annual'
                or self.input_data.get_value(InputType.TIME_PERIOD) == 'all'):
            title = ('Demonstration Version - {temporal_type} average '
                     '{variable}\n'
                     'for {start_year} to {end_year}'.format(
                         temporal_type=self.input_data.get_value_label(
                             InputType.TEMPORAL_AVERAGE_TYPE),
                         start_year=self.input_data.get_value(
                             InputType.YEAR_MINIMUM),
                         end_year=self.input_data.get_value(
                             InputType.YEAR_MAXIMUM),
                         variable=self.input_data.get_value_label(
                             InputType.VARIABLE)))
        else:
            title = ('Demonstration Version - {temporal_type} average '
                     '{variable} for\n'
                     '{time_period} in {start_year} to {end_year}'.format(
                         temporal_type=self.input_data.get_value_label(
                             InputType.TEMPORAL_AVERAGE_TYPE),
                         time_period=self.input_data.get_value_label(
                             InputType.TIME_PERIOD),
                         start_year=self.input_data.get_value(
                             InputType.YEAR_MINIMUM),
                         end_year=self.input_data.get_value(
                             InputType.YEAR_MAXIMUM),
                         variable=self.input_data.get_value_label(
                             InputType.VARIABLE)))

        if self.input_data.get_area_type() == 'point':
            grid_x = (self.cubes[0].coord('projection_x_coordinate')
                      .bounds[0][0])
            grid_y = (self.cubes[0].coord('projection_y_coordinate')
                      .bounds[0][0])
            title = "{t} at grid {x}, {y}".format(t=title, x=grid_x, y=grid_y)

        elif self.input_data.get_area_type() == 'bbox':
            # TODO bbox
            grid_x = (self.cubes[0].coord('projection_x_coordinate')
                      .bounds[0][0])
            grid_y = (self.cubes[0].coord('projection_y_coordinate')
                      .bounds[0][0])
            title = "{t} at grid {x}, {y}".format(t=title, x=grid_x, y=grid_y)

        else:
            title = "{t} in {area}".format(
                t=title, area=self.input_data.get_area_label())

        return title
