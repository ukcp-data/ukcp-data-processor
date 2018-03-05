import collections
import logging
import os
from time import gmtime, strftime


log = logging.getLogger(__name__)


class BaseCsvWriter(object):
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
        self.timestamp
    """

    def write_csv(self, input_data, cube_list, output_data_file_path, vocab,
                  plot_type, overlay_cube=None):
        """
        Write a CSV file.

        @param input_data (InputData): an object containing user defined values
        @param cube_list (iris cube list): a list of cubes containing the
            selected data, one cube per scenario, per variable
        @param output_data_file_path (str): the full path to the file
        @param vocab (Vocab): an instance of the ukcp_dp Vocab class
        @param overlay_cube (iris cube): a cube containing the data for
            the overlay
        """
        log.info('write_csv, {plot}'.format(plot=plot_type))
        # an object containing user defined values
        self.input_data = input_data
        # an iris cube list
        self.cube_list = cube_list
        self.overlay_cube = overlay_cube
        self.vocab = vocab
        self.data_dict = collections.OrderedDict()
        self.header = []
        self.output_data_file_path = output_data_file_path.split('output.csv')[
            0]
        self.timestamp = strftime("%Y-%m-%dT%H-%M-%S", gmtime())
        self.plot_type = plot_type
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
        pass

    def _write_data_dict(self, output_data_file_path):
        """
        Write out the column headers and data_dict.
        """
        user_inputs = self.input_data.get_user_inputs()
        header_string = ','.join(self.header)
        header_length = len(header_string.split('\n')) + \
            len(user_inputs.keys()) + 1
        with open(output_data_file_path, 'w') as output_data_file:
            output_data_file.write('header length,{}\n'.format(header_length))
            keys = user_inputs.keys()
            keys.sort()
            for key in keys:
                output_data_file.write('{key},{value}\n'.format(
                    key=key, value=user_inputs[key]))
            output_data_file.write(header_string)
            output_data_file.write('\n')
            for key, values in self.data_dict.items():
                line_out = '{key},{values}\n'.format(
                    key=key, values=','.join(values))
                output_data_file.write(line_out)

    def _get_full_file_name(self, file_name_suffix=None):
        if file_name_suffix is None:
            file_name_suffix = ''
        file_name = '{plot_type}_{timestamp}{suffix}.csv'.format(
            plot_type=self.plot_type.lower(), timestamp=self.timestamp,
            suffix=file_name_suffix)
        return os.path.join(self.output_data_file_path, file_name)
