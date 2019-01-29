import collections
import logging

import iris
from ukcp_dp.constants import AreaType, InputType
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter
from ukcp_dp.file_writers._utils import round_variable


log = logging.getLogger(__name__)


class SubsetCsvWriter(BaseCsvWriter):
    """
    The subset CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).
    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with three maps.
        """
        if self.input_data.get_area_type() == AreaType.BBOX:
            return self._write_x_y_csv()
        else:
            return self._write_region_csv()

    def _write_x_y_csv(self):
        cube = self.cube_list[0]

        # add axis titles to the header
        self.header.append('x-axis,Eastings (BNG)\n')
        self.header.append('y-axis,Northings (BNG)\n')

        # add the x values to the header
        x_values = ['--']
        write_header = True
        output_file_list = []

        # loop over ensembles
        for ensemble_slice in cube.slices_over('ensemble_member'):
            ensemble_name = ensemble_slice.coord(
                'ensemble_member_id').points[0]

            output_data_file_path = self._get_full_file_name(
                '_{}'.format(ensemble_name))
            self._write_headers(output_data_file_path)

            # loop over times
            for time_slice in ensemble_slice.slices_over('time'):
                with iris.FUTURE.context(cell_datetime_objects=True):
                    time_str = time_slice.coord('time').cell(
                        0).point.strftime('%Y-%m-%d')
                key_list = []

                # get the numpy representation of the sub-cube
                data = time_slice.data
                # get the coordinates for the sub-cube
                y_coords = time_slice.coord(
                    'projection_y_coordinate').points
                x_coords = time_slice.coord(
                    'projection_x_coordinate').points

                # rows of data
                for y in range(0, y_coords.shape[0]):
                    y_coord = str(y_coords[y])
                    # columns of data
                    for x in range(0, x_coords.shape[0]):
                        if write_header is True:
                            x_values.append(str(x_coords[x]))

                        value = round_variable(self.input_data.get_value(
                            InputType.VARIABLE)[0], data[y, x])
                        try:
                            self.data_dict[y_coord].append(value)
                        except KeyError:
                            key_list = [y_coord] + key_list
                            self.data_dict[y_coord] = [value]
                    write_header = False

                self._write_data_block(
                    output_data_file_path, key_list, time_str, x_values)
            output_file_list.append(output_data_file_path)

        return output_file_list

    def _write_data_block(self, output_data_file_path, key_list, time_str,
                          x_values):
        """
        Write out the column headers and data_dict.
        """
        with open(output_data_file_path, 'a') as output_data_file:
            output_data_file.write(time_str + '\n')
            line_out = ','.join(x_values) + '\n'
            output_data_file.write(line_out)
            for key in key_list:
                line_out = '{key},{values}\n'.format(
                    key=key, values=','.join(self.data_dict[key]))
                output_data_file.write(line_out)

        # reset the data dict
        self.data_dict = collections.OrderedDict()

    def _write_region_csv(self):

        cube = self.cube_list[0]

        # update the header
        self.header.append('Date')

        key_list = []
        for ensemble_slice in cube.slices_over('ensemble_member'):
            ensemble_name = str(ensemble_slice.coord(
                'ensemble_member_id').points[0])

            # update the header
            var = self.input_data.get_value_label(
                InputType.VARIABLE)[0].encode('utf-8')
            self.header.append('{var}({ensemble})'.format(
                ensemble=ensemble_name, var=var))

            # loop over times
            for time_slice in ensemble_slice.slices_over('time'):
                with iris.FUTURE.context(cell_datetime_objects=True):
                    time_str = time_slice.coord('time').cell(
                        0).point.strftime('%Y-%m-%d')

                value = round_variable(self.input_data.get_value(
                    InputType.VARIABLE)[0], time_slice.data)
                try:
                    self.data_dict[time_str].append(value)
                except KeyError:
                    key_list = [time_str] + key_list
                    self.data_dict[time_str] = [value]

        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]
