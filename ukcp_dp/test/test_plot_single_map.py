from os import path
import unittest

from ukcp_dp import AreaType, ImageFormat, InputType, PlotType
from ukcp_dp.test.test_plot import run_plot_test


def get_ls6_test_bbox():
    data = {}
    data[InputType.AREA] = [AreaType.BBOX, -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "12km"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = "tasmax"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR] = 2018

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Maps_01_bbox_seasonal.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal.png"
    )

    return data, input_files, reference_file


def get_ls6_test_bbox_ls():
    data, _, _ = get_ls6_test_bbox()
    data[InputType.AREA] = [AreaType.BBOX, -73600.0, 190400.0, 595200.0, 641600.0]
    data[InputType.SHOW_BOUNDARIES] = AreaType.RIVER_BASIN

    # temporal options
    data[InputType.TIME_PERIOD] = "ann"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "ann"
    data[InputType.YEAR] = 2018

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(base_path, "data", "input_files", "LS6_Maps_01_bbox_ann.nc")

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_ann.png"
    )

    return data, input_files, reference_file


def get_ls6_test_bbox_small():
    data, input_files, _ = get_ls6_test_bbox()

    # image options
    data[InputType.FONT_SIZE] = "s"
    data[InputType.IMAGE_SIZE] = 900

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal_s.png"
    )

    return data, input_files, reference_file


def get_ls6_test_bbox_large():
    data, input_files, _ = get_ls6_test_bbox()

    # image options
    data[InputType.FONT_SIZE] = "l"
    data[InputType.IMAGE_SIZE] = 2400

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal_l.png"
    )

    return data, input_files, reference_file


def get_ls6_test_bbox_admin_overlay():
    data, input_files, _ = get_ls6_test_bbox()

    data[InputType.SHOW_BOUNDARIES] = "admin_region"

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal_admin.png"
    )

    return data, input_files, reference_file


def get_ls6_test_bbox_country_overlay():
    data, input_files, _ = get_ls6_test_bbox()

    data[InputType.SHOW_BOUNDARIES] = "country"

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal_country.png"
    )

    return data, input_files, reference_file


def get_ls6_test_bbox_river_overlay():
    data, input_files, _ = get_ls6_test_bbox()

    data[InputType.SHOW_BOUNDARIES] = "river_basin"

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Maps_01_bbox_seasonal_river.png"
    )

    return data, input_files, reference_file


def get_ls6_test_region():
    data = {}
    data[InputType.AREA] = "admin_region|All administrative regions"
    data[InputType.SPATIAL_REPRESENTATION] = "admin_region"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = "tasmax"

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"
    data[InputType.YEAR] = 2018

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Maps_01_admin_monthly.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Maps_01_admin_monthly.png"
    )

    return data, input_files, reference_file


class SingleMapPlotTestCase(unittest.TestCase):
    def test_single_map_plot(self):
        """
        Test that the single map plotter writes the correct plot.
        """
        inputs = [
            (get_ls6_test_bbox()),
            (get_ls6_test_bbox_ls()),
            (get_ls6_test_bbox_small()),
            (get_ls6_test_bbox_large()),
            (get_ls6_test_bbox_admin_overlay()),
            (get_ls6_test_bbox_country_overlay()),
            (get_ls6_test_bbox_river_overlay()),
            (get_ls6_test_region()),
        ]

        for data, input_files, reference_file in inputs:
            with self.subTest(
                data=data, input_files=input_files, reference_file=reference_file
            ):
                diff = run_plot_test(
                    data,
                    input_files,
                    reference_file,
                    PlotType.SINGLE_MAP,
                    "Single Map Test Plot",
                    ImageFormat.PNG,
                )
                self.assertEqual(diff, "")


if __name__ == "__main__":
    unittest.main()
