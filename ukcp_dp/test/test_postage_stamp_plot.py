"""
ls1_maps_01.py
=========================

Process ls1_maps_01 that holds the LS1_Maps_01 class.

"""

from ukcp_dp import DataFormat, ImageFormat, InputType, PlotType
from ukcp_dp import UKCPDataProcessor
from ukcp_dp.file_finder import get_file_lists

import time

def set_inputs():

    data = {}
    data[InputType.BASELINE] = 'b8100'
    data[InputType.COLLECTION] = 'land-rcm'
    data[InputType.VARIABLE] = 'tasmaxAnom'
    data[InputType.SCENARIO] = 'rcp85'

    # image options
    data[InputType.FONT_SIZE] = 'm'
    data[InputType.IMAGE_SIZE] = 1200

    # temporal options
    data[InputType.TIME_PERIOD] = 'may'
    data[InputType.TIME_SLICE_TYPE] = '1y'
    data[InputType.TEMPORAL_AVERAGE_TYPE] = 'mon'
    data[InputType.ORDER_BY_MEAN] = True
    data[InputType.YEAR] = 2030

    data[InputType.AREA] = 'admin_region|all'

    # process constants
    data[InputType.DATA_TYPE] = 'cdf'

    # ensemble members input
    data[InputType.ENSEMBLE] = [
        '01', '04', '05', '06', '07', '08', '09', '10', '11',
        '12', '13', '15']

    dp = UKCPDataProcessor('0.0.0-test')

    dp.set_inputs(data, {})

    return dp


if __name__ == '__main__':

    st_time = time.time()
    dp = set_inputs()
    dp.select_data()
    output_dir = '/tmp'
    dp.write_plot(PlotType.POSTAGE_STAMP_MAPS, output_dir, ImageFormat.PNG)
    print (time.time() - st_time)
    dp.write_data_files(output_dir, DataFormat.CSV)
