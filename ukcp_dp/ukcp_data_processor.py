"""
ukcp_data_processor.py
======================

Holds the top-level UKCPDataProcessor class that is typically used as
the entry point for this package.

"""

from iris.cube import CubeList
from ukcp_dp._input_data import InputData
from ukcp_dp.constants import DATA_SOURCE_PROB, InputType, PlotType
from ukcp_dp.data_extractor import DataExtractor, get_probability_levels
from ukcp_dp.file_finder import get_file_lists
from ukcp_dp.file_writers import write_file
from ukcp_dp.plotters import write_plot as plotter_write_plot
from ukcp_dp.validator import Validator
from ukcp_dp.vocab_manager import Vocab


class UKCPDataProcessor(object):

    def __init__(self):
        self.cube_list = None
        self.input_data = None
        self.overlay_cube = None
        self.plot_type = None
        self.vocab = Vocab()
        self.validator = Validator(self.vocab)
        self.validated = False

    def get_vocab(self):
        """
        Get the instance of the Vocab class.

        @return a Vocab object
        """
        return self.vocab

    def set_inputs(self, inputs, allowed_values=None):
        """
        Set the input values.

        An optional list of allowed values can be used to make additional
        checks when validating the input. They should define a subset of the
        facet values to use.

        @param inputs (dict):
            key(string) - this should match a value from the INPUT_TYPES list
            value(list or string or int) - the value(s) to set. These should
                match value(s) in the vocabulary as well as any constraints set
                by 'allowed_values'

        @param allowed_values (dict):
            key(string) - this should match a value from the INPUT_TYPES list
            value(list or string or int) - these are the values that the input
                are validated against
        """
        self.input_data = InputData(self.vocab)
        self.input_data.set_inputs(inputs, allowed_values)

        return self.input_data

    def validate_inputs(self):
        if self.input_data is None:
            raise Exception('Invalid state, input data has not been set')

        self.input_data = self.validator.validate(self.input_data)
        self.validated = True

        return True

    def select_data(self):
        """
        Use the data set via 'set_inputs' to generate an iris cube list.

        @return an iris cube list
        """
        if self.validated is False:
            self.validate_inputs()

        file_lists = get_file_lists(self.input_data)
        data_extractor = DataExtractor(file_lists, self.input_data)
        self.title = data_extractor.get_title()
        self.cube_list = data_extractor.get_cubes()
        self.overlay_cube = data_extractor.get_overlay_cube()
        return self.cube_list

    def write_plot(self, plot_type, output_path, title=None):
        """
        Generate a plot.

        For some of the plot types not all of the data will be plotted, i.e.
        where the 10th 50 and 90th percentiles are plotted. A subsequent call
        to write_data_files will only write out the data used for the plot.

        @param plot_type (PlotType): the type of plot to generate
        @param output_path (str): the full path to the file
        @param title (str): optional. If a title is not provided one will be
            generated.
        """
        if self.cube_list is None:
            self.select_data()

        if title is None:
            title = self.title

        plotter_write_plot(plot_type, output_path, self.input_data,
                           self.cube_list, self.overlay_cube, title,
                           self.vocab)
        self.plot_type = plot_type

        return

    def write_data_files(self, output_data_file_path):
        """
        Write the data to a file.

        If a plot has been written that used a subset of the selected data then
        only that subset will be written out. Subsequent calls will write all
        of the selected data.

        @param output_data_file_path (str): the full path to the file
        """
        if self.cube_list is None:
            self.select_data()

        cubes = self.cube_list

        # The data in the cube may contain more data than was used to make a
        # plot. If the data has not been written out since the last plot then
        # we may need to constrain it. Next time round all the data will be
        # written.
        if (self.plot_type is not None and
            (self.plot_type == PlotType.PLUME_PLOT or
             self.plot_type == PlotType.THREE_MAPS) and
            (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB)):
            cubes = CubeList()
            for cube in self.cube_list:
                # extract 10th, 50th and 90th percentiles
                cubes.append(get_probability_levels(cube))
            self.plot_type = None

        write_file(cubes, self.title, output_data_file_path)
