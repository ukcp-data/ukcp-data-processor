from os import path
import unittest

from ukcp_dp import ImageFormat, InputType, PlotType
from ukcp_dp.test.test_plot import run_plot_test


def get_ls1_test_prob_point_data():
    data = {}
    data[InputType.AREA] = ["point", 437500.0, 287500.0]
    data[InputType.SPATIAL_REPRESENTATION] = "25km"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp85"
    data[InputType.SHOW_LABELS] = True

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2038
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
        base_path, "data", "input_files", "LS1_Plume_01_point_seasonal.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_Plume_01_point_seasonal.png"
    )

    return data, input_files, reference_file, None


def get_ls2_test_point_data():
    data = {}
    data[InputType.AREA] = ["point", 450000.0, 270000.0]
    data[InputType.SPATIAL_REPRESENTATION] = "60km"
    data[InputType.COLLECTION] = "land-gcm"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp85"
    data[InputType.BASELINE] = "b8100"
    data[InputType.OVERLAY_PROBABILITY_LEVELS] = False

    data[InputType.DATA_TYPE] = "cdf"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2038
    data[InputType.TIME_SLICE_TYPE] = "1y"

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200
    data[InputType.LEGEND_POSITION] = 2
    data[InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS] = []

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
        base_path, "data", "input_files", "LS2_Plume_01_point_seasonal.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Plume_01_point_seasonal.png"
    )

    return data, input_files, reference_file, None


def get_ls2_test_region_data():
    data, _, _, _ = get_ls2_test_point_data()
    data[InputType.AREA] = "country|England and Wales"
    data[InputType.SPATIAL_REPRESENTATION] = "country"
    data[InputType.OVERLAY_PROBABILITY_LEVELS] = True

    data[InputType.DATA_TYPE] = "cdf"

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"

    # image options
    data[InputType.FONT_SIZE] = "s"
    data[InputType.IMAGE_SIZE] = 900
    data[InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS] = ["02", "05"]
    data[InputType.COLOUR_MODE] = "c"
    data[InputType.Y_AXIS_MIN] = -1
    data[InputType.Y_AXIS_MAX] = 3

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Plume_01_country_monthly.nc"
    )
    overlay_input_files = path.join(
        base_path, "data", "input_files", "LS2_Plume_01_country_monthly_overlay.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS2_Plume_01_country_monthly.png"
    )

    return data, input_files, reference_file, overlay_input_files


def get_ms4_test_gauge_point_data():
    data = {}
    data[InputType.AREA] = ["gauge_point", 50.83, -1.08]
    data[InputType.COLLECTION] = "marine-sim"
    data[InputType.VARIABLE] = "stillWaterReturnLevel"
    data[InputType.SCENARIO] = "rcp45"

    # temporal options
    data[InputType.YEAR] = 2060

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200
    data[InputType.LEGEND_POSITION] = 2

    # process constants
    data[InputType.METHOD] = "return-periods"
    data[InputType.DATA_TYPE] = "percentile"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "MS4_ReturnLevels_01_gauge_point.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "MS4_ReturnLevels_01_gauge_point.png"
    )

    return data, input_files, reference_file, None


class PlumePlotTestCase(unittest.TestCase):
    def test_plume_plot(self):
        """
        Test that the plume plotter writes the correct plot.

        """
        inputs = [
            (get_ls1_test_prob_point_data()),
            (get_ls2_test_point_data()),
            (get_ls2_test_region_data()),
            (get_ms4_test_gauge_point_data()),
        ]

        for (data, input_files, reference_file, overlay_input_files) in inputs:
            with self.subTest(
                data=data,
                input_files=input_files,
                reference_file=reference_file,
                overlay_input_files=overlay_input_files,
            ):
                diff = run_plot_test(
                    data,
                    input_files,
                    reference_file,
                    PlotType.PLUME_PLOT,
                    "Plume Test Plot",
                    ImageFormat.PNG,
                    overlay_input_files,
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
