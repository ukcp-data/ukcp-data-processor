import logging

import iris
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter


log = logging.getLogger(__name__)


class ThreeMapCsvWriter(BaseCsvWriter):
    """
    The three map CSV writer class.

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

        # extract 10th, 50th and 90th percentiles
        percentiles = [10, 50, 90]
        for percentile in percentiles:
            percentile_cube = cube.extract(
                iris.Constraint(percentile=percentile))

            # rows of data
            for projection_y_slice in percentile_cube.slices_over(
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

                    try:
                        self.data_dict[y_coord].append(
                            str(projection_x_slice.data))
                    except KeyError:
                        self.data_dict[y_coord] = [
                            str(projection_x_slice.data)]
                write_header = False

            output_data_file_path = self._get_full_file_name(
                '_{}'.format(percentile))
            self._write_data_dict(output_data_file_path)
            output_file_list.append(output_data_file_path)

        return output_file_list
