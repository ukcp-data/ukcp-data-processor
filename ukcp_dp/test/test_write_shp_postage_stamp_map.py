from os import path
import unittest

from ukcp_dp import InputType, PlotType
from ukcp_dp.constants import DataFormat
from ukcp_dp.test.test_write import run_write_test


def get_ls2_test_bbox_data():
    data = {}
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "60km"
    data[InputType.COLLECTION] = "land-gcm"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp26"
    data[InputType.BASELINE] = "b8100"
    data[InputType.ORDER_BY_MEAN] = True

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_FORMAT] = "png"
    data[InputType.IMAGE_SIZE] = 1200

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR] = 2018
    data[InputType.TIME_SLICE_TYPE] = "1y"

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
        base_path, "data", "input_files", "LS2_Maps_02_bbox_seasonal.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_seasonal.dbf"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_seasonal.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_seasonal.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_seasonal.prj"
        ),
    ]

    output_file_index = [0, 1, 2, 3]
    return data, input_files, reference_files, output_file_index


def get_ls2_test_region_data_1():
    data, _, _, _ = get_ls2_test_bbox_data()
    data[InputType.AREA] = "river_basin|all"
    data[InputType.SPATIAL_REPRESENTATION] = "river_basin"

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Maps_02_river_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_river_monthly.dbf"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_river_monthly.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_river_monthly.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_river_monthly.prj"
        ),
    ]

    output_file_index = [0, 1, 2, 3]
    return data, input_files, reference_files, output_file_index


def get_ls2_test_region_data_2():
    data, _, _, _ = get_ls2_test_region_data_1()
    data[InputType.AREA] = "country|all"
    data[InputType.SPATIAL_REPRESENTATION] = "country"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Maps_02_country_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_country_monthly.dbf"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_country_monthly.shp"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_country_monthly.shx"
        ),
        path.join(
            base_path, "data", "expected_outputs", "LS2_Maps_02_country_monthly.prj"
        ),
    ]

    output_file_index = [0, 1, 2, 3]
    return data, input_files, reference_files, output_file_index


class PostagestampShpTestCase(unittest.TestCase):
    def test_postagestamp_shp(self):
        """
        Test that the postage stamp shape file writer writes the correct shape file
        values.
        """
        inputs = [
            (get_ls2_test_bbox_data()),
            (get_ls2_test_region_data_1()),
            (get_ls2_test_region_data_2()),
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
                    PlotType.POSTAGE_STAMP_MAPS,
                    data_format=DataFormat.SHAPEFILE,
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
