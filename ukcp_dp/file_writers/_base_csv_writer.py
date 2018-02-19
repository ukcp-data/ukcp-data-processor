import collections
import logging


log = logging.getLogger(__name__)


class BaseCsvWriter():
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
    """

    def write_csv(self, input_data, cube_list,
                  output_data_file_path, title, vocab, overlay_cube=None):
        """
        Write a CSV file.

        @param input_data (InputData): an object containing user defined values
        @param cube_list (iris cube list): a list of cubes containing the
            selected data, one cube per scenario, per variable
        @param output_data_file_path (str): the full path to the file
        @param title (str): a title for the plot
        @param vocab (Vocab): an instance of the ukcp_dp Vocab class
        @param overlay_cube (iris cube): a cube containing the data for
            the overlay
        """
        log.info('write_csv')
        # an object containing user defined values
        self.input_data = input_data
        # an iris cube list
        self.cube_list = cube_list
        self.overlay_cube = overlay_cube
        self.vocab = vocab
        self.data_dict = collections.OrderedDict()
        self.header = []

        self._write_csv()
        _write_data_dict(title, self.data_dict, self.header,
                         output_data_file_path)

    def _write_csv(self):
        """
        This method should be overridden to produce the column headers in
        self.header and put the data in self.data_dict.
        """
        pass


def _write_data_dict(title, data_dict, header, output_data_file_path):
    """
    Write out the column headers and data_dict.
    """
    with open(output_data_file_path, 'w') as output_data_file:
        output_data_file.write(','.join(header))
        output_data_file.write('\n')
        for key, values in data_dict.items():
            line_out = '{key},{values}\n'.format(
                key=key, values=','.join(values))
            output_data_file.write(line_out)
