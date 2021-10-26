from os import path
import unittest

from ukcp_dp import InputType, PlotType
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
            base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


def get_ls6_test_region_data():
    data, _, _, _ = get_ls6_test_bbox_data()
    data[InputType.AREA] = "river_basin|all"
    data[InputType.SPATIAL_REPRESENTATION] = "river_basin"

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Maps_01_river_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS6_Maps_01_river_monthly.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index


class SingleMapCsvTestCase(unittest.TestCase):
    def test_single_map_csv(self):
        """
        Test that the single map csv writer writes the correct csv values.
        """
        inputs = [(get_ls6_test_bbox_data()), (get_ls6_test_region_data())]

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
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
