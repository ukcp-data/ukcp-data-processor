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
    data[InputType.BASELINE] = "b8100"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = ["rlsAnom", "tasAnom"]
    data[InputType.SCENARIO] = "rcp60"

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    # temporal options
    data[InputType.TIME_PERIOD] = "apr"
    data[InputType.TIME_SLICE_TYPE] = "1y"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"
    data[InputType.YEAR] = 2020

    data[InputType.AREA] = ["point", 344000.00, 470400.00]

    # process constants
    data[InputType.DATA_TYPE] = "sample"

    dp = UKCPDataProcessor("0.0.0-test")

    dp.set_inputs(data, {})

    return dp


if __name__ == "__main__":

    dp = set_inputs()
    dp.select_data()
    output_dir = "/tmp"
    st_time = time.time()
    dp.write_plot(PlotType.JP_PLOT, output_dir, ImageFormat.PNG)
    print(time.time() - st_time)
    dp.write_data_files(output_dir, DataFormat.CSV)
