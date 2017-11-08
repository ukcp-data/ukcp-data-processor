"""
ukcp_data_processor.py
======================

Holds the top-level UKCPDataProcessor class that is typically used as
the entry point for this package.

"""

from ukcp_dp._input_data import InputData
from ukcp_dp.constants import PlotType
from ukcp_dp.data_extractor import DataExtractor
from ukcp_dp.file_finder import get_file_lists
from ukcp_dp.file_writers import write_file
from ukcp_dp.plotters import PlumePlotter
from ukcp_dp.validator import Validator


class UKCPDataProcessor(object):

    def __init__(self):
        self.cube = None
        self.input_data = None
        self.validator = Validator()
        self.validated = False

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
        self.input_data = InputData()
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
        Use the data set via 'set_inputs' to generate an iris data cube.

        @return an iris data cube
        """
        if self.validated is False:
            self.validate_inputs()

        file_lists = get_file_lists(self.input_data)
        data_extractor = DataExtractor(file_lists, self.input_data)
        self.title = data_extractor.get_title()
        self.cubes = data_extractor.get_cubes()

        return self.cubes

    def write_plot(self, plot_type, output_path, title=None):
        """
        Generate a plot.

        @param plot_type (PlotType): the type of plot to generate
        @param output_path (str): the full path to the file
        @param title (str): optional. If a title is not provided one will be
            generated.

        @return the data used to generate the plot
        """
        if self.cubes is None:
            self.select_data()

        if title is None:
            title = self.title

        if plot_type == PlotType.PLUME_PLOT:
            plotter = PlumePlotter()

        plot_data = plotter.generate_plot(
            output_path, self.input_data, self.cubes, title)

        return plot_data

    def write_data_files(self, output_data_file_path):
        """
        Write the data to a file.

        @param output_data_file_path (str): the full path to the file
        """
        if self.cubes is None:
            self.select_data()

        write_file(self.cubes, self.title, output_data_file_path)
