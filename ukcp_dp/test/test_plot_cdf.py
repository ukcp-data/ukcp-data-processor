from os import path
import unittest

from ukcp_dp import ImageFormat, InputType, PlotType
from ukcp_dp.test.test_plot import run_plot_test


def get_ls1_test_prob_point_data():
    data = {}
    data[InputType.AREA] = ["point", 437500.0, 337500.0]
    data[InputType.SPATIAL_REPRESENTATION] = "25km"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = ["rcp26", "rcp85"]

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
    input_files = [
        path.join(
            base_path, "data", "input_files", "LS1_CDF_PDF_01_point_seasonal_1.nc"
        ),
        path.join(
            base_path, "data", "input_files", "LS1_CDF_PDF_01_point_seasonal_3.nc"
        ),
    ]

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_CDF_01_point_seasonal.png"
    )

    return data, input_files, reference_file


def get_ls1_test_prob_point_colour_data():
    data, input_files, _ = get_ls1_test_prob_point_data()

    # image options
    data[InputType.COLOUR_MODE] = "c"

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_CDF_01_point_seasonal_c.png"
    )

    return data, input_files, reference_file


def get_ls1_test_prob_point_small_data():
    data, input_files, _ = get_ls1_test_prob_point_data()

    # image options
    data[InputType.FONT_SIZE] = "s"
    data[InputType.IMAGE_SIZE] = 900

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_CDF_01_point_seasonal_s.png"
    )

    return data, input_files, reference_file


def get_ls1_test_prob_point_large_data():
    data, input_files, _ = get_ls1_test_prob_point_data()

    # image options
    data[InputType.FONT_SIZE] = "l"
    data[InputType.IMAGE_SIZE] = 2400

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_CDF_01_point_seasonal_l.png"
    )

    return data, input_files, reference_file


class LS1CDFPlotTestCase(unittest.TestCase):
    def test_ls1_point_plot(self):
        """
        Test that the CDF plotter writes the correct plot.

        """

        inputs = [
            (get_ls1_test_prob_point_data()),
            (get_ls1_test_prob_point_colour_data()),
            (get_ls1_test_prob_point_small_data()),
            (get_ls1_test_prob_point_large_data()),
        ]

        for data, input_files, reference_file in inputs:
            with self.subTest(
                data=data, input_files=input_files, reference_file=reference_file
            ):

                diff = run_plot_test(
                    data,
                    input_files,
                    reference_file,
                    PlotType.CDF_PLOT,
                    "CDF Test Plot",
                    ImageFormat.PNG,
                )
                self.assertEqual(diff, "")


if __name__ == "__main__":
    unittest.main()
