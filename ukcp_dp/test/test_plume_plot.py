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
    data[InputType.COLLECTION] = 'land-prob'
    data[InputType.VARIABLE] = 'prAnom'
    data[InputType.SCENARIO] = 'rcp85'

    # image options
    data[InputType.FONT_SIZE] = 'm'
    data[InputType.IMAGE_SIZE] = 1200

    # temporal options
    data[InputType.TIME_PERIOD] = 'all'
    data[InputType.TIME_SLICE_TYPE] = '1y'
    data[InputType.TEMPORAL_AVERAGE_TYPE] = 'mon'
    data[InputType.YEAR_MINIMUM] = 1961
    data[InputType.YEAR_MAXIMUM] = 2100

    data[InputType.AREA] = ['point', 441600.00, 1142400.00]

    # process constants
    data[InputType.DATA_TYPE] = 'cdf'

    dp = UKCPDataProcessor('0.0.0-test')

    dp.set_inputs(data, {})

    return dp


if __name__ == '__main__':

    dp = set_inputs()
    dp.select_data()
    output_dir = '/tmp'
    st_time = time.time()
    dp.write_plot(PlotType.PLUME_PLOT, output_dir, ImageFormat.PNG)
    print (time.time() - st_time)
    dp.write_data_files(output_dir, DataFormat.CSV)
