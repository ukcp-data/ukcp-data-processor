from os import path
import unittest

from ukcp_dp import ImageFormat, InputType, PlotType
from ukcp_dp.test.test_plot import run_plot_test


def get_ls6_test_obs_point_data():
    data = {}
    data[InputType.AREA] = ["point", 438000.0, 282000.0]
    data[InputType.SPATIAL_REPRESENTATION] = "12km"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = "tasmax"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR_MINIMUM] = 1980
    data[InputType.YEAR_MAXIMUM] = 2000

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Time_Series_01_point_seasonal.nc"
    )

    reference_files = path.join(
        base_path, "data", "expected_outputs", "LS6_Time_Series_01_point_seasonal.png"
    )

    return data, input_files, reference_files, None


def get_ls6_test_obs_point_small_data():
    data, _, _, _ = get_ls6_test_obs_point_data()

    # temporal options
    data[InputType.TIME_PERIOD] = "all"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"

    # image options
    data[InputType.FONT_SIZE] = "s"
    data[InputType.IMAGE_SIZE] = 900

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Time_Series_01_point_seasonal_all.nc"
    )

    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Time_Series_01_point_seasonal_s.png"
    )

    return data, input_files, reference_file, None


def get_ls6_test_obs_point_large_data():
    data, input_files, _, _ = get_ls6_test_obs_point_data()

    # image options
    data[InputType.FONT_SIZE] = "l"
    data[InputType.IMAGE_SIZE] = 2400

    base_path = path.abspath(path.dirname(__file__))
    reference_file = path.join(
        base_path, "data", "expected_outputs", "LS6_Time_Series_01_point_seasonal_l.png"
    )

    return data, input_files, reference_file, None


def get_ls6_test_obs_region_data():
    data = {}
    data[InputType.AREA] = "country|England"
    data[InputType.SPATIAL_REPRESENTATION] = "country"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = "tasmax"

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"
    data[InputType.YEAR_MINIMUM] = 1980
    data[InputType.YEAR_MAXIMUM] = 2000

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS6_Time_Series_01_country_monthly.nc"
    )

    reference_files = path.join(
        base_path, "data", "expected_outputs", "LS6_Time_Series_01_country_monthly.png"
    )

    return data, input_files, reference_files, None


class PlumePlotTestCase(unittest.TestCase):
    def test_plume_plot(self):
        """
        Test that the plume plotter writes the correct plot.

        """
        inputs = [
            (get_ls6_test_obs_point_data()),
            (get_ls6_test_obs_point_small_data()),
            (get_ls6_test_obs_point_large_data()),
            (get_ls6_test_obs_region_data()),
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
                    PlotType.TIME_SERIES,
                    "Time Series Test Plot",
                    ImageFormat.PNG,
                    overlay_input_files,
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
