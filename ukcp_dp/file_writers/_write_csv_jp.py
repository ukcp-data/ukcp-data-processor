import logging

import numpy as np
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter


log = logging.getLogger(__name__)


class JpCsvWriter(BaseCsvWriter):
    """
    The joint probability CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).
    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with a JP plot.
        """

        x = self.cube_list[0].data
        y = self.cube_list[1].data

        h, xedges, yedges = np.histogram2d(x, y, bins=10)
        xbins = xedges[:-1] + (xedges[1] - xedges[0]) / 2
        ybins = yedges[:-1] + (yedges[1] - yedges[0]) / 2
        h = h.T

        # add the x values to the header
        self.header.append('--')
        for x in xbins:
            self.header.append(str(x))

        # add a line of data for each y value
        for i, y in enumerate(sorted(ybins, reverse=True)):
            for value in h[len(h) - (1 + i)]:
                try:
                    self.data_dict[str(y)].append(str(value))
                except KeyError:
                    self.data_dict[str(y)] = [str(value)]

        # now write the data
        output_data_file_path = self._get_full_file_name()
        self._write_data_dict(output_data_file_path)

        return [output_data_file_path]
