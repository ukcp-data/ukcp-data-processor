"""
This module contains the BaseCsvWriter, a base class for CSV writers.

"""

import collections
import logging
import os
from time import gmtime, strftime


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class BaseCsvWriter:
    """
    The base class for CSV writers.

    This class should be extended with a
    _write_csv(self) method to format the data.
    The following variables are available to overriding methods:
        self.input_data
        self.cube_list
        self.overlay_cube
        self.vocab
        self.data_dict
        self.header
        self.output_data_file_path
        self.plot_type
        self.process_version
        self.timestamp

    """

    ignore_in_header = [
        "Colour Mode",
        "Font Size",
        "Highlighted Members",
        "Image Size",
        "Legend Position",
        "Plot Title",
    ]

    def __init__(self):
        self.input_data = None
        self.cube_list = None
        self.overlay_cube = None
        self.vocab = None
        self.data_dict = None
        self.header = None
        self.output_data_file_path = None
        self.timestamp = None
        self.plot_type = None
        self.process_version = None

    def write_csv(
        self,
        input_data,
        cube_list,
        output_data_file_path,
        vocab,
        plot_type,
        process_version,
        overlay_cube=None,
    ):
        """
        Write a CSV file.

        @param input_data (InputData): an object containing user defined values
        @param cube_list (iris cube list): a list of cubes containing the
            selected data, one cube per scenario, per variable
        @param output_data_file_path (str): the full path to the file
        @param vocab (Vocab): an instance of the ukcp_dp Vocab class
        @param plot_type (PlotType): the type of the plot
        @param process_version (str): the version of the process generating
            this output
        @param overlay_cube (iris cube): a cube containing the data for
            the overlay

        """
        LOG.info("write_csv, %s", plot_type)
        # an object containing user defined values
        self.input_data = input_data
        # an iris cube list
        self.cube_list = cube_list
        self.overlay_cube = overlay_cube
        self.vocab = vocab
        self.data_dict = collections.OrderedDict()
        self.header = []
        self.output_data_file_path = output_data_file_path.split("output.csv")[0]
        self.timestamp = strftime("%Y-%m-%dT%H-%M-%S", gmtime())
        self.plot_type = plot_type
        self.process_version = process_version
        return self._write_csv()

    def _write_csv(self):
        """
        This method should be overridden to produce the column headers in
        self.header and put the data in self.data_dict.

        It should write the data to one or more files and pass back a list of
        file names. The _write_data_dict method has been provided to write the
        data to a file

        self._write_data_dict(output_data_file_path)

        @return a list of file names

        """
        raise NotImplementedError

    def _write_data_dict(self, output_data_file_path, key_list):
        """
        Write out the column headers and data_dict.

        """
        self._write_headers(output_data_file_path)

        with open(output_data_file_path, "a", encoding="utf-8") as output_data_file:
            for key in key_list:
                line_out = f"{key},{','.join(self.data_dict[key])}\n"
                output_data_file.write(line_out)

        # reset the data dict
        self.data_dict = collections.OrderedDict()

    def _write_headers(self, output_data_file_path):
        """
        Write out the column headers.

        """
        user_inputs = {}
        all_user_inputs = self.input_data.get_user_inputs()
        for key in all_user_inputs:
            if key in self.ignore_in_header:
                continue
            user_inputs[key] = all_user_inputs[key]
        user_inputs["Software Version"] = self.process_version
        header_string = ",".join(self.header)
        header_string = header_string.replace("\n,", "\n")
        header_length = len(header_string.split("\n")) + len(user_inputs.keys()) + 1
        with open(output_data_file_path, "w", encoding="utf8") as output_data_file:
            output_data_file.write(f"header length,{header_length}\n")
            for key in sorted(user_inputs.keys()):
                output_data_file.write(f"{key},{user_inputs[key]}\n")
            output_data_file.write(header_string)
            output_data_file.write("\n")

    def _get_full_file_name(self, file_name_suffix=None):
        if file_name_suffix is None:
            file_name_suffix = ""
        try:
            plot_type = self.plot_type.lower()
        except AttributeError:
            plot_type = "subset"
        file_name = f"{plot_type}_{self.timestamp}{file_name_suffix}.csv"
        return os.path.join(self.output_data_file_path, file_name)


def value_to_string(value, variable=None):
    """
    Format the value dependent on the contents of variable.

    The default operation is to return a string.

    @param value(): the value to format
    @param variable(str): the name of the variable that the value represents.

    """
    if variable is None:
        return str(value)

    if variable == "extremeSeaLevel":
        # The value is in metres and we want to the nearest mm
        return str(round(value, 3))

    return str(value)
