import iris
import iris.plot as iplt
import iris.quickplot as qplt
from ukcp_dp.constants import InputType
from ukcp_dp.vocab_manager import get_collection_terms


class DataExtractor():
    """
    Extract data from a list of files and filter it based on user selection
    criteria.
    """

    def __init__(self, file_list, input_data):
        """
        Initialise the DataExtractor.

        @param file_list (list(str)) a list of file names
        @param input_data (InputData) an object containing user defined values
        """
        self.file_list = file_list
        self.input_data = input_data
        self.cube = self._get_cube()

    def get_cube(self):
        """
        Get an iris data cube based on the given files and using selection
        criteria from the input_data

        @return an iris data cube
        """
        return self.cube

    def _get_cube(self):
        """
        Get an iris data cube based from the given files using selection
        criteria from the input_data

        @return an iris data cube
        """
        # Load the cubes based on the variable
        if self.input_data.get_value(InputType.VARIABLE) == 'pr':
            cubes = iris.load(self.file_list, ["precipitation rate"])
        elif self.input_data.get_value(InputType.VARIABLE) == 'tas':
            cubes = iris.load(self.file_list, ["air_temperature"])
        else:
            raise Exception(
                "Unknown variable: {}.".format(self.input_data.get_value(
                    InputType.VARIABLE)))
        cube = cubes.concatenate_cube()

        # generate an area constraint
        area_constraint = self._get_spatial_selector()
        cube = cube.extract(area_constraint)

        # generate a temporal constraint
        temporal_constraint = self._get_temporal_selector()
        if temporal_constraint is not None:
            cube = cube.extract(temporal_constraint)

        # show 10, 50 and 90 percentiles
        if (self.input_data.get_value(InputType.SHOW_PROBABILITY_LEVELS) is
                True):
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
                self.input_data.get_area_type() == 'catchment'):
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
            pass
        elif (temporal_average_type == 'mon' or
              temporal_average_type == 'seasonal'):
            for i in [i for i, term in enumerate(
                    get_collection_terms(temporal_average_type))
                    if term == self.input_data.get_value(
                        InputType.TIME_PERIOD)]:
                temporal_constraint = iris.Constraint(meaning_period=i)
        else:
            raise Exception(
                "Unknown temporal average type: {}.".format(
                    self.input_data.get_value(
                        InputType.TEMPORAL_AVERAGE_TYPE)))
        return temporal_constraint

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
            grid_x = self.cube.coord('projection_x_coordinate').bounds[0][0]
            grid_y = self.cube.coord('projection_y_coordinate').bounds[0][0]
            title = "{t} at grid {x}, {y}".format(t=title, x=grid_x, y=grid_y)

        elif self.input_data.get_area_type() == 'bbox':
            # TODO bbox
            grid_x = self.cube.coord('projection_x_coordinate').bounds[0][0]
            grid_y = self.cube.coord('projection_y_coordinate').bounds[0][0]
            title = "{t} at grid {x}, {y}".format(t=title, x=grid_x, y=grid_y)

        else:
            title = "{t} in {area}".format(
                t=title, area=self.input_data.get_area())

        return title
