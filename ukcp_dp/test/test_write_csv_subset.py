from os import path
import unittest

from ukcp_dp import InputType
from ukcp_dp.test.test_write import run_write_test


def get_ls1_test_prob_point_data():
    data = {}
    data[InputType.AREA] = ["point", 387500.0, 287500.0]
    data[InputType.SPATIAL_REPRESENTATION] = "25km"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "pr5day"
    data[InputType.SCENARIO] = "rcp85"
    data[InputType.RETURN_PERIOD] = "rp50"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2028

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "cdf"
    data[InputType.TIME_SLICE_TYPE] = "1y"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS1_Subset_02_point_sesonal.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS1_Subset_02_point_sesonal.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


def get_ls2_test_bbox_data():
    data = {}
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "60km"
    data[InputType.COLLECTION] = "land-gcm"
    data[InputType.VARIABLE] = "tas"
    data[InputType.SCENARIO] = "rcp26"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2028

    # ensemble members input
    data[InputType.ENSEMBLE] = [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
    ]

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Subset_01_bbox_seasonal.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS2_Subset_01_bbox_seasonal_1.csv"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Subset_01_bbox_seasonal_2.csv"
        ),
    ]

    output_file_index = [0, -1]
    return data, input_files, reference_files, output_file_index


def get_ls2_test_region_data():
    data, _, _, _ = get_ls2_test_bbox_data()
    data[InputType.AREA] = "admin_region|West Midlands"
    data[InputType.SPATIAL_REPRESENTATION] = "admin_region"

    # temporal options
    data[InputType.TIME_PERIOD] = "may"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Subset_01_admin_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS2_Subset_01_admin_monthly.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


def get_ls3a_test_point_data():
    data = {}
    data[InputType.AREA] = ["point", 452500.0, 262500.0]
    data[InputType.SPATIAL_REPRESENTATION] = "5km"
    data[InputType.COLLECTION] = "land-cpm"
    data[InputType.VARIABLE] = "tas"
    data[InputType.SCENARIO] = "rcp85"

    # temporal options
    data[InputType.TIME_PERIOD] = "1hr"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "1hr"
    data[InputType.YEAR_MINIMUM] = 1981
    data[InputType.YEAR_MAXIMUM] = 1982

    # ensemble members input
    data[InputType.ENSEMBLE] = ["01"]

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS3A_Subset_03_point_hourly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS3A_Subset_03_point_hourly.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


def get_ms4_test_coast_point_data():
    data = {}
    data[InputType.AREA] = ["coast_point", 53.39, -4.25]
    data[InputType.BASELINE] = "b8100"
    data[InputType.COLLECTION] = "marine-sim"
    data[InputType.VARIABLE] = "seaLevelAnom"
    data[InputType.SCENARIO] = "rcp45"

    # temporal options
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2048

    data[InputType.TIME_PERIOD] = "ann"
    data[InputType.DATA_TYPE] = "percentile"
    data[InputType.METHOD] = "msl-proj-expl"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "MS4_Anomalies_Subset_02.nc"
    )

    reference_files = [
        path.join(base_path, "data", "expected_outputs", "MS4_Anomalies_Subset_02.csv")
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


def get_ls6_test_bbox_data():
    data = {}
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "12km"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = "tasmin"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR_MINIMUM] = 1918
    data[InputType.YEAR_MAXIMUM] = 1928

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Subset_01_bbox_seasonal.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS6_Subset_01_bbox_seasonal.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


def get_ls6_test_region_data():
    data, _, _, _ = get_ls6_test_bbox_data()
    data[InputType.AREA] = "admin_region|West Midlands"
    data[InputType.SPATIAL_REPRESENTATION] = "admin_region"

    # temporal options
    data[InputType.TIME_PERIOD] = "may"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Subset_01_admin_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS6_Subset_01_admin_monthly.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


class SubsetCsvTestCase(unittest.TestCase):
    def test_subset_csv(self):
        """
        Test that the subset csv writer writes the correct csv values.
        """
        inputs = [
            (get_ls1_test_prob_point_data()),
            (get_ls2_test_bbox_data()),
            (get_ls2_test_region_data()),
            (get_ls3a_test_point_data()),
            (get_ms4_test_coast_point_data()),
            (get_ls6_test_bbox_data()),
            (get_ls6_test_region_data()),
        ]

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
