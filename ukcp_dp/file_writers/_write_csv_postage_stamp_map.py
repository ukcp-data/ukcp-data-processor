import logging

import iris
from ukcp_dp.constants import AreaType, InputType
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter


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
            return self._write_x_y_csv()
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

            # New Code
            # get the numpy representation of the sub-cube
            data = ensemble_slice.data
            # get the coordinates for the sub-cube
            y_coords = ensemble_slice.coord('projection_y_coordinate').points
            x_coords = ensemble_slice.coord('projection_x_coordinate').points

            # rows of data
            for y in range(0, y_coords.shape[0]):
                y_coord = str(y_coords[y])
                # columns of data
                for x in range(0, x_coords.shape[0]):
                    if write_header is True:
                        self.header.append(str(x_coords[x]))

                    value = str(data[y, x])
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
            ###

        return output_file_list

    def _write_region_csv(self):

        cube = self.cube_list[0]

        # update the header
        self.header.append(str(
            cube.coords(var_name='geo_region')[0].long_name))

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
                region = str(region_slice.coords(var_name='geo_region')[
                    0].points[0])

                value = str(region_slice.data)
                try:
                    self.data_dict[region].append(value)
                except KeyError:
                    key_list = [region] + key_list
                    self.data_dict[region] = [value]

        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]
