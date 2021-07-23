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
    data[InputType.DATA_TYPE] = ["cdf", "pdf"]

    base_path = path.abspath(path.dirname(__file__))
    input_files = [
        path.join(
            base_path, "data", "input_files", "LS1_CDF_PDF_01_point_seasonal_1.nc"
        ),
        path.join(
            base_path, "data", "input_files", "LS1_CDF_PDF_01_point_seasonal_2.nc"
        ),
        path.join(
            base_path, "data", "input_files", "LS1_CDF_PDF_01_point_seasonal_3.nc"
        ),
        path.join(
            base_path, "data", "input_files", "LS1_CDF_PDF_01_point_seasonal_4.nc"
        ),
    ]

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS1_PDF_01_point_seasonal.png"
    )

    return data, input_files, reference_file


class LS1PDFPlotTestCase(unittest.TestCase):
    def test_ls1_point_plot(self):
        """
        Test that the PDF plotter writes the correct plot.

        """
        data, input_files, reference_file = get_ls1_test_prob_point_data()
        diff = run_plot_test(
            data,
            input_files,
            reference_file,
            PlotType.PDF_PLOT,
            "PDF Test Plot",
            ImageFormat.PNG,
        )
        self.assertEqual(diff, "")


if __name__ == "__main__":
    unittest.main()
