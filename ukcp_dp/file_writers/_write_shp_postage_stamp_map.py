import logging

from ukcp_dp.file_writers._base_shp_writer import BaseShpWriter


log = logging.getLogger(__name__)


class PostageStampMapShpWriter(BaseShpWriter):
    """
    The postage stamp map shapefile writer class.
    This class extends BaseShpWriter with a _write_shp(self).
    """

    def _write_shp(self):
        """
        Write out the data, in shapefile format, associated with postage stamp
        maps.
        @return a list of file paths/names
        """
        return []
