"""
ls1_maps_01.py
=========================

Process ls1_maps_01 that holds the LS1_Maps_01 class.

"""

from ukcp_dp import DataFormat, ImageFormat, InputType, PlotType
from ukcp_dp import UKCPDataProcessor
import time

def set_inputs():

    data = {}
    data[InputType.BASELINE] = 'b8100'
    data[InputType.COLLECTION] = 'land-prob'
    data[InputType.VARIABLE] = 'tasAnom'
    data[InputType.SCENARIO] = 'rcp85'

    # image options
    data[InputType.FONT_SIZE] = 'm'
    data[InputType.IMAGE_SIZE] = 1200

    # temporal options
    data[InputType.TIME_PERIOD] = 'may'
    data[InputType.TIME_SLICE_TYPE] = '1y'
    data[InputType.TEMPORAL_AVERAGE_TYPE] = 'mon'
    data[InputType.YEAR] = 2019
    data[InputType.SHOW_BOUNDARIES] = 'admin_region' # river_basin | country | admin_region
    data[InputType.AREA] = ['bbox', -84667.14, -114260.00, 676489.68, 1230247.30]

    # process constants
    data[InputType.DATA_TYPE] = 'cdf'

    dp = UKCPDataProcessor('0.0.0-test')

    dp.set_inputs(data, {})

    return dp


if __name__ == '__main__':

    st_time = time.time()
    dp = set_inputs()
    dp.select_data()
    print (time.time() - st_time)

    output_dir = '/tmp'
    st_time = time.time()
    dp.write_plot(PlotType.THREE_MAPS, output_dir, ImageFormat.PNG)
    print (time.time() - st_time)
    dp.write_data_files(output_dir, DataFormat.CSV)
