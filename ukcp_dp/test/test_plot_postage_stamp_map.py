from os import path
import unittest

from ukcp_dp import AreaType, ImageFormat, InputType, PlotType
from ukcp_dp.test.test_plot import run_plot_test


def get_ls2_test_bbox_28_data():
    data = {}
    data[InputType.AREA] = [AreaType.BBOX, -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "60km"
    data[InputType.COLLECTION] = "land-gcm"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp26"
    data[InputType.BASELINE] = "b8100"
    data[InputType.ORDER_BY_MEAN] = False

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
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
    ]

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Maps_02_bbox_seasonal_28.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_seasonal_28.png"
    )

    return data, input_files, reference_file


def get_ls2_test_bbox_15_data():
    data, _, _ = get_ls2_test_bbox_28_data()

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

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_seasonal_15.png"
    )

    return data, input_files, reference_file


def get_ls2_test_bbox_12_data():
    data, _, _ = get_ls2_test_bbox_28_data()
    data[InputType.ORDER_BY_MEAN] = True

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
        base_path, "data", "input_files", "LS2_Maps_02_bbox_seasonal_12.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_seasonal_12.png"
    )

    return data, input_files, reference_file


def get_ls2_test_bbox_28_ls_data():
    data, _, _ = get_ls2_test_bbox_28_data()
    data[InputType.AREA] = [AreaType.BBOX, -84667.14, 119200.0, 676489.68, 647200.0]

    # temporal options
    data[InputType.TIME_PERIOD] = "ann"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "ann"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Maps_02_bbox_ann_28_ls.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_ann_28_ls.png"
    )

    return data, input_files, reference_file


def get_ls2_test_bbox_15_ls_data():
    data, _, _ = get_ls2_test_bbox_28_ls_data()

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
        base_path, "data", "input_files", "LS2_Maps_02_bbox_ann_15_ls.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_ann_15_ls.png"
    )

    return data, input_files, reference_file


def get_ls2_test_bbox_12_ls_data():
    data, _, _ = get_ls2_test_bbox_28_ls_data()

    # ensemble members input
    data[InputType.ENSEMBLE] = [
        "01",
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
        "15",
    ]

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Maps_02_bbox_ann_12_ls.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Maps_02_bbox_ann_12_ls.png"
    )

    return data, input_files, reference_file


def get_ls2_test_region_data():
    data, _, _ = get_ls2_test_bbox_12_data()
    data[InputType.AREA] = "river_basin|all"
    data[InputType.SPATIAL_REPRESENTATION] = "river_basin"

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Maps_02_river_monthly.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Maps_02_river_monthly.png"
    )

    return data, input_files, reference_file


def get_ls3_test_bbox_12_data():
    data, _, _ = get_ls2_test_bbox_12_data()

    data[InputType.SPATIAL_REPRESENTATION] = "12km"
    data[InputType.COLLECTION] = "land-rcm"
    data[InputType.SCENARIO] = "rcp85"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS3_Maps_02_bbox_seasonal_12.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS3_Maps_02_bbox_seasonal_12.png"
    )

    return data, input_files, reference_file


def get_ls3a_test_bbox_12_data():
    data, _, _ = get_ls2_test_bbox_12_data()

    data[InputType.SPATIAL_REPRESENTATION] = "5km"
    data[InputType.COLLECTION] = "land-cpm"
    data[InputType.SCENARIO] = "rcp85"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS3A_Maps_02_bbox_seasonal_12.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS3A_Maps_02_bbox_seasonal_12.png"
    )

    return data, input_files, reference_file


class PostagestampMapTestCase(unittest.TestCase):
    def test_postagestamp_map(self):
        """
        Test that the postage stamp plotter writes the correct plot.
        """
        inputs = [
            (get_ls2_test_bbox_12_data()),
            (get_ls2_test_bbox_28_data()),
            (get_ls2_test_bbox_15_data()),
            (get_ls2_test_bbox_28_ls_data()),
            (get_ls2_test_bbox_15_ls_data()),
            (get_ls2_test_bbox_12_ls_data()),
            (get_ls2_test_region_data()),
            (get_ls3_test_bbox_12_data()),
            # (get_ls3a_test_bbox_12_data()),
        ]

        for data, input_files, reference_file in inputs:
            with self.subTest(
                data=data, input_files=input_files, reference_file=reference_file
            ):
                diff = run_plot_test(
                    data,
                    input_files,
                    reference_file,
                    PlotType.POSTAGE_STAMP_MAPS,
                    "Postage Stamp Map Test Plot",
                    ImageFormat.PNG,
                )
                self.assertEqual(diff, "")


if __name__ == "__main__":
    unittest.main()
