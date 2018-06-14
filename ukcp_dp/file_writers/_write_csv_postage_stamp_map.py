import logging

import iris
from ukcp_dp.constants import AreaType, InputType
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter
from ukcp_dp.file_writers._utils import convert_to_2dp


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
        if self.input_data.get_area_type() == AreaType.BBOX:
            return self._write_x_y_csv(self)
        else:
            return self._write_region_csv()

    def _write_x_y_csv(self):
        cube = self.cube_list[0]

        # add axis titles to the header
        self.header.append('x-axis,Eastings (BNG)\n')
        self.header.append('y-axis,Northings (BNG)\n')

        # add the x values to the header
        self.header.append('--')
        write_header = True
        output_file_list = []

        for ensemble_slice in cube.slices_over('ensemble_member'):
            key_list = []
            ensemble_name = ensemble_slice.coord(
                'ensemble_member_id').points[0]

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

    def _write_region_csv(self):

        cube = self.cube_list[0]

        # update the header
        self.header.append(str(cube.coord('region').long_name))

        key_list = []
        for ensemble_slice in cube.slices_over('ensemble_member'):
            ensemble_name = str(ensemble_slice.coord(
                'ensemble_member_id').points[0])

            # update the header
            var = self.input_data.get_value_label(
                InputType.VARIABLE)[0].encode('utf-8')
            self.header.append('{var}({ensemble})'.format(
                ensemble=ensemble_name, var=var))

            # rows of data
            for region_slice in ensemble_slice.slices_over('region'):
                region = str(region_slice.coord('region').points[0])

                value = convert_to_2dp(region_slice.data)
                try:
                    self.data_dict[region].append(value)
                except KeyError:
                    key_list = [region] + key_list
                    self.data_dict[region] = [value]

        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]
