from os import path
import unittest

from ukcp_dp import InputType
from ukcp_dp.test.test_write import run_write_test


def get_ls1_test_prob_point_data():
    data = {}
    data[InputType.AREA] = ["point", 437500.0, 337500.0]
    data[InputType.SPATIAL_REPRESENTATION] = "25km"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp85"
    data[InputType.SAMPLING_METHOD] = "id"
    data[InputType.SAMPLING_ID] = list(range(1, 301))

    # temporal options
    data[InputType.TIME_PERIOD] = "all"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR] = 2018
    data[InputType.TIME_SLICE_TYPE] = "1y"

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "sample"

    base_path = path.abspath(path.dirname(__file__))
    input_files = [
        path.join(
            base_path, "data", "input_files", "LS1_Sample_01_point_seasonal_all.nc"
        )
    ]

    reference_files = [
        path.join(
            base_path,
            "data",
            "expected_outputs",
            "LS1_Sample_01_point_seasonal_all.csv",
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


def get_ls1_test_prob_region_data():
    data, _, _, _ = get_ls1_test_prob_point_data()

    data[InputType.AREA] = "admin_region|West Midlands"
    data[InputType.SPATIAL_REPRESENTATION] = "admin_region"
    data[InputType.VARIABLE] = ["tasAnom", "prAnom"]
    data[InputType.SAMPLING_METHOD] = "id"
    data[InputType.SAMPLING_ID] = list(range(1, 301))

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"

    base_path = path.abspath(path.dirname(__file__))
    input_files = [
        path.join(base_path, "data", "input_files", "LS1_Sample_01_admin_monthly_1.nc"),
        path.join(base_path, "data", "input_files", "LS1_Sample_01_admin_monthly_2.nc"),
    ]

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS1_Sample_01_admin_monthly.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


class SampleCsvTestCase(unittest.TestCase):
    def test_ls1_sample_csv(self):
        """
        Test that the sample csv writer writes the correct csv values.
        """
        inputs = [(get_ls1_test_prob_point_data()), (get_ls1_test_prob_region_data())]

        for data, input_files, reference_files, output_file_index in inputs:
            with self.subTest(
                data=data,
                input_files=input_files,
                reference_files=reference_files,
                output_file_index=output_file_index,
            ):
                diff = run_write_test(
                    data, input_files, reference_files, output_file_index
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
