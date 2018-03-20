import logging

import iris
from ukcp_dp.constants import DATA_SOURCE_GCM
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter
from ukcp_dp.file_writers._utils import convert_to_2dp
from ukcp_dp.vocab_manager import get_ensemble_member_set


log = logging.getLogger(__name__)


class PostageStampMapCsvWriter(BaseCsvWriter):
    """
    The postage stamp map CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).
    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with three maps.
        """
        cube = self.cube_list[0]

        # add axis titles to the header
        self.header.append('x-axis,Eastings (BNG)\n')
        self.header.append('y-axis,Northings (BNG)\n')

        # add the x values to the header
        self.header.append('--')
        write_header = True
        output_file_list = []
        key_list = []

        for ensemble_slice in cube.slices_over('Ensemble member'):
            # TODO need a better way to get the ensemble_name
            ensemble_name = get_ensemble_member_set(DATA_SOURCE_GCM)[
                int(ensemble_slice.coord('Ensemble member').points[0])]

            # rows of data
            for projection_y_slice in ensemble_slice.slices_over(
                    'projection_y_coordinate'):
                y_coord = str(projection_y_slice.coord(
                    'projection_y_coordinate').points[0])

                # columns of data
                for projection_x_slice in projection_y_slice.slices_over(
                        'projection_x_coordinate'):
                    if write_header is True:
                        x_coord = str(projection_x_slice.coord(
                            'projection_x_coordinate').points[0])
                        self.header.append(x_coord)

                    value = convert_to_2dp(projection_x_slice.data)

                    try:
                        self.data_dict[y_coord].append(value)
                    except KeyError:
                        key_list = [y_coord] + key_list
                        self.data_dict[y_coord] = [value]
                write_header = False

            output_data_file_path = self._get_full_file_name(
                '_{}'.format(ensemble_name))
            self._write_data_dict(output_data_file_path, key_list)
            output_file_list.append(output_data_file_path)

        return output_file_list
