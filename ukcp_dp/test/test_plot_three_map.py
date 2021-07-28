from os import path
import unittest

from ukcp_dp import AreaType, ImageFormat, InputType, PlotType
from ukcp_dp.test.test_plot import run_plot_test


def get_ls1_test_prob_bbox_data():
    data = {}
    data[InputType.AREA] = [AreaType.BBOX, -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "25km"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp26"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR] = 2018
    data[InputType.TIME_SLICE_TYPE] = "1y"

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200
    data[InputType.LEGEND_POSITION] = 2

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "cdf"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS1_Maps_01_bbox_seasonal.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_Maps_01_bbox_seasonal.png"
    )

    return data, input_files, reference_file


def get_ls1_test_prob_bbox_ls_data():
    data, _, _ = get_ls1_test_prob_bbox_data()
    data[InputType.AREA] = [AreaType.BBOX, -73600.0, 190400.0, 595200.0, 641600.0]
    data[InputType.SHOW_BOUNDARIES] = AreaType.RIVER_BASIN

    # temporal options
    data[InputType.TIME_PERIOD] = "ann"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "ann"
    data[InputType.YEAR] = 2018

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(base_path, "data", "input_files", "LS1_Maps_01_bbox_ann.nc")

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_Maps_01_bbox_ann.png"
    )

    return data, input_files, reference_file


def get_ls1_test_prob_region_data():
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

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200
    data[InputType.LEGEND_POSITION] = 2

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "cdf"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS1_Maps_01_admin_monthly.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_Maps_01_admin_monthly.png"
    )

    return data, input_files, reference_file


class ThreeMapPlotTestCase(unittest.TestCase):
    def test_three_map_plot(self):
        """
        Test that the three map plotter writes the correct plot.
        """
        inputs = [
            (get_ls1_test_prob_bbox_data()),
            (get_ls1_test_prob_bbox_ls_data()),
            (get_ls1_test_prob_region_data()),
        ]

        for data, input_files, reference_file in inputs:
            with self.subTest(
                data=data, input_files=input_files, reference_file=reference_file
            ):
                diff = run_plot_test(
                    data,
                    input_files,
                    reference_file,
                    PlotType.THREE_MAPS,
                    "Three Map Test Plot",
                    ImageFormat.PNG,
                )
                self.assertEqual(diff, "")


if __name__ == "__main__":
    unittest.main()
