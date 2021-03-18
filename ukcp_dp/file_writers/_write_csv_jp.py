"""
This module contains the JpCsvWriter class, which implements the _write_csv method
from the BaseCsvWriter base class.

"""
import logging

import numpy as np
from ukcp_dp.constants import InputType
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter


LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class JpCsvWriter(BaseCsvWriter):
    """
    The joint probability CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).

    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with a JP plot.

        """

        x_value = self.cube_list[0].data
        y_value = self.cube_list[1].data

        h, xedges, yedges = np.histogram2d(x_value, y_value, bins=10)
        xbins = xedges[:-1] + (xedges[1] - xedges[0]) / 2
        ybins = yedges[:-1] + (yedges[1] - yedges[0]) / 2
        h = h.T

        # add axis titles to the header
        x_label = self.input_data.get_value_label(InputType.VARIABLE)[0]
        y_label = self.input_data.get_value_label(InputType.VARIABLE)[1]
        self.header.append(f"x-axis,{x_label}\n")
        self.header.append(f"y-axis,{y_label}\n")

        # add the x values to the header
        self.header.append("--")
        for x_bin in xbins:
            self.header.append(str(x_bin))
        key_list = []
        # add a line of data for each y value
        for i, y in enumerate(sorted(ybins, reverse=True)):
            y = str(y)
            for value in h[len(h) - (1 + i)]:
                value = str(value)
                try:
                    self.data_dict[y].append(value)
                except KeyError:
                    key_list.append(y)
                    self.data_dict[y] = [value]

        # now write the data
        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path, key_list)

        return [output_data_file_path]
