from os import path
import unittest

from ukcp_dp import InputType, PlotType
from ukcp_dp.constants import DataFormat
from ukcp_dp.test.test_write import run_write_test


def get_ls1_test_prob_bbox_data():
    data = {}
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "25km"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp26"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR] = 2018
    data[InputType.TIME_SLICE_TYPE] = "1y"

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "cdf"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS1_Maps_01_bbox_seasonal.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_bbox_seasonal.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_bbox_seasonal.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_bbox_seasonal.prj"
        ),
    ]

    output_file_index = [1, 2, 3]
    return data, input_files, reference_files, output_file_index


def get_ls1_test_prob_region_data_1():
    data = {}
    data[InputType.AREA] = "admin_region|All administrative regions"
    data[InputType.SPATIAL_REPRESENTATION] = "admin_region"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp26"

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"
    data[InputType.YEAR] = 2018
    data[InputType.TIME_SLICE_TYPE] = "1y"

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "cdf"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS1_Maps_01_admin_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_admin_monthly.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_admin_monthly.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_admin_monthly.prj"
        ),
    ]

    output_file_index = [1, 2, 3]
    return data, input_files, reference_files, output_file_index


def get_ls1_test_prob_region_data_2():
    data, _, _, _ = get_ls1_test_prob_region_data_1()
    data[InputType.AREA] = "country|All countries"
    data[InputType.SPATIAL_REPRESENTATION] = "country"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS1_Maps_01_country_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_country_monthly.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_country_monthly.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS1_Maps_01_country_monthly.prj"
        ),
    ]

    output_file_index = [1, 2, 3]
    return data, input_files, reference_files, output_file_index


class ThreeMapShpTestCase(unittest.TestCase):
    def test_three_map_sho(self):
        """
        Test that the three map shape file writer writes the correct shape file values.
        """
        inputs = [
            (get_ls1_test_prob_bbox_data()),
            (get_ls1_test_prob_region_data_1()),
            (get_ls1_test_prob_region_data_2()),
        ]

        for data, input_files, reference_files, output_file_index in inputs:
            with self.subTest(
                data=data,
                input_files=input_files,
                reference_files=reference_files,
                output_file_index=output_file_index,
            ):
                diff = run_write_test(
                    data,
                    input_files,
                    reference_files,
                    output_file_index,
                    PlotType.THREE_MAPS,
                    data_format=DataFormat.SHAPEFILE,
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
