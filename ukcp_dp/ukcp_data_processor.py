"""
ukcp_data_processor.py
======================

Holds the top-level UKCPDataProcessor class that is typically used as
the entry point for this package.

"""

from ukcp_dp._input_data import InputData
from ukcp_dp.constants import COLLECTION_PROB, InputType, VERSION
from ukcp_dp.data_extractor import DataExtractor
from ukcp_dp.file_finder import get_absolute_paths, get_file_lists
from ukcp_dp.file_writers import write_file
from ukcp_dp.plotters import write_plot as plotter_write_plot
from ukcp_dp.processors import SamplingProcessor
from ukcp_dp.validator import Validator
from ukcp_dp.vocab_manager import Vocab
from ukcp_dp.utils import get_plot_settings


class UKCPDataProcessor:
    def __init__(self, process_version=None):
        self.cube_list = None
        self.input_data = None
        self.overlay_cube = None
        self.plot_settings = None
        self.plot_type = None
        self.title = None
        self.vocab = Vocab()
        self.validator = Validator(self.vocab)
        self.validated = False
        if process_version is None:
            self.process_version = VERSION
        else:
            self.process_version = process_version

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
            raise Exception("Invalid state, input data has not been set")

        self.input_data = self.validator.validate(self.input_data)
        self.validated = True

        return True

    def select_data(self):
        """
        Use the data set via 'set_inputs' to generate an iris cube list.

        @return a list of file paths of the files containing the selected data
        """
        if self.validated is False:
            self.validate_inputs()

        file_lists = get_file_lists(self.input_data)

        # The plot settings are customised to the first variable in the list
        # We may want to change this in the future
        if (
            self.input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB
            and self.input_data.get_value(InputType.RETURN_PERIOD) is not None
        ):
            extreme = True
        else:
            extreme = False
        self.plot_settings = get_plot_settings(
            self.vocab,
            self.input_data.get_value(InputType.IMAGE_SIZE),
            self.input_data.get_font_size(),
            self.input_data.get_value(InputType.VARIABLE)[0],
            extreme,
        )

        data_extractor = DataExtractor(file_lists, self.input_data, self.plot_settings)

        self.title = data_extractor.get_title()
        self.cube_list = data_extractor.get_cubes()
        self.overlay_cube = data_extractor.get_overlay_cube()

        if self.input_data.get_value(InputType.SAMPLING_METHOD) is not None:
            sampling_processor = SamplingProcessor(
                self.cube_list, self.input_data, self.vocab
            )
            self.cube_list = sampling_processor.get_cubes()

        return get_absolute_paths(file_lists)

    def write_plot(self, plot_type, output_path, image_format=None, title=None):
        """
        Generate a plot.

        For some of the plot types not all of the data will be plotted, i.e.
        where the 10th 50 and 90th percentiles are plotted. A subsequent call
        to write_data_files will only write out the data used for the plot.

        @param plot_type (PlotType): the type of plot to generate
        @param output_path (str): the full path to the file
        @param image_format (ImageFormat): the format of the image to generate.
            If None the value from the inputs will be used.
        @param title (str): optional. If a title is not provided one will be
            generated.
        """
        if self.cube_list is None:
            self.select_data()

        if image_format is None:
            image_format = self.input_data.get_value(InputType.IMAGE_FORMAT)

        if image_format is None:
            raise Exception("image_format cannot be None")

        if title is None:
            title = self.title

        image_file = plotter_write_plot(
            plot_type,
            output_path,
            image_format,
            self.input_data,
            self.cube_list,
            self.overlay_cube,
            title,
            self.vocab,
            self.plot_settings,
        )
        self.plot_type = plot_type

        return image_file

    def write_data_files(self, output_data_file_path, data_format=None):
        """
        Write the data to a file.

        @param output_data_file_path (str): the full path to the file
        @param data_format (DataFormat): the type of the output data.
            If None the value from the inputs will be used.
        """
        # validate the value of data_format
        if data_format is None:
            data_format = self.input_data.get_value(InputType.DATA_FORMAT)

        if data_format is None:
            raise Exception("data_format cannot be None")

        if (
            self.vocab.get_collection_term_label(InputType.DATA_FORMAT, data_format)
            is None
        ):
            raise Exception(
                "Unknown {value_type}: {value}.".format(
                    value_type=InputType.DATA_FORMAT, value=data_format
                )
            )

        if self.cube_list is None:
            self.select_data()

        cubes = self.cube_list

        output_file_list = write_file(
            cubes,
            self.overlay_cube,
            output_data_file_path,
            data_format,
            self.input_data,
            self.plot_type,
            self.process_version,
            self.vocab,
        )
        self.plot_type = None
        return output_file_list
