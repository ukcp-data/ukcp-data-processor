from os import path
import unittest

from ukcp_dp import InputType, PlotType
from ukcp_dp.constants import DataFormat
from ukcp_dp.test.test_write import run_write_test


def get_ls6_test_bbox_data():
    data = {}
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "12km"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = "tasmax"

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_FORMAT] = "png"
    data[InputType.IMAGE_SIZE] = 1200

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR] = 2018

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Maps_01_bbox_seasonal.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal.prj"
        ),
    ]

    output_file_index = [1, 2, 3]
    return data, input_files, reference_files, output_file_index


def get_ls6_test_prob_region_data_1():
    data = {}
    data[InputType.AREA] = "admin_region|All administrative regions"
    data[InputType.SPATIAL_REPRESENTATION] = "admin_region"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = "tasmax"

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"
    data[InputType.YEAR] = 2018

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Maps_01_admin_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_admin_monthly.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_admin_monthly.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_admin_monthly.prj"
        ),
    ]

    output_file_index = [1, 2, 3]
    return data, input_files, reference_files, output_file_index


def get_ls6_test_prob_region_data_2():
    data, _, _, _ = get_ls6_test_prob_region_data_1()
    data[InputType.AREA] = "country|All countries"
    data[InputType.SPATIAL_REPRESENTATION] = "country"
    data[InputType.VARIABLE] = "rainfall"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Maps_01_country_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_country_monthly.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_country_monthly.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_country_monthly.prj"
        ),
    ]

    output_file_index = [1, 2, 3]
    return data, input_files, reference_files, output_file_index


class SingleMapShpTestCase(unittest.TestCase):
    def test_single_map_sho(self):
        """
        Test that the single map shape file writer writes the correct shape file values.

        """
        inputs = [
            (get_ls6_test_bbox_data()),
            (get_ls6_test_prob_region_data_1()),
            (get_ls6_test_prob_region_data_2()),
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
                    PlotType.SINGLE_MAP,
                    data_format=DataFormat.SHAPEFILE,
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
