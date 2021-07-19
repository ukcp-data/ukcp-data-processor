from os import path
import unittest

from ukcp_dp import InputType, PlotType
from ukcp_dp.test.test_write import run_write_test


def get_ls1_test_prob_point_data():
    data = {}
    data[InputType.AREA] = ["point", 437500.0, 337500.0]
    data[InputType.SPATIAL_REPRESENTATION] = "25km"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = ["rcp26", "rcp85"]

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR] = 2018
    data[InputType.TIME_SLICE_TYPE] = "1y"

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "cdf"

    base_path = path.abspath(path.dirname(__file__))
    input_files = [
        path.join(
            base_path, "data", "input_files", "LS1_CDF_PDF_01_point_seasonal_1.nc"
        ),
        path.join(
            base_path, "data", "input_files", "LS1_CDF_PDF_01_point_seasonal_3.nc"
        ),
    ]

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS1_CDF_01_point_seasonal.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


class LS1CDFCsvTestCase(unittest.TestCase):
    def test_ls1_point_csv(self):
        data, input_files, reference_files, output_file_index = (
            get_ls1_test_prob_point_data()
        )
        diff = run_write_test(
            data, input_files, reference_files, output_file_index, PlotType.CDF_PLOT
        )
        self.assertEqual(diff, "")


if __name__ == "__main__":
    unittest.main()
