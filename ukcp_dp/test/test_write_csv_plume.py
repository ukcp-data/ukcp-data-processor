from os import path
import unittest

from ukcp_dp import InputType, PlotType
from ukcp_dp.test.test_write import run_write_test


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

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "cdf"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS1_Plume_01_point_seasonal.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS1_Plume_01_point_seasonal.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index, None


def get_ls1_test_prob_region_data():
    data = {}
    data[InputType.AREA] = "country|England"
    data[InputType.SPATIAL_REPRESENTATION] = "country"
    data[InputType.COLLECTION] = "land-prob"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp85"
    data[InputType.SHOW_LABELS] = True

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2038
    data[InputType.TIME_SLICE_TYPE] = "1y"

    # process constants
    data[InputType.BASELINE] = "b8100"
    data[InputType.DATA_TYPE] = "cdf"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS1_Plume_01_country_monthly.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS1_Plume_01_country_monthly.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index, None


def get_ls2_test_point_data():
    data = {}
    data[InputType.AREA] = ["point", 450000.0, 270000.0]
    data[InputType.SPATIAL_REPRESENTATION] = "60km"
    data[InputType.COLLECTION] = "land-gcm"
    data[InputType.VARIABLE] = "tasAnom"
    data[InputType.SCENARIO] = "rcp85"
    data[InputType.BASELINE] = "b8100"
    data[InputType.OVERLAY_PROBABILITY_LEVELS] = False

    # image options
    data[InputType.FONT_SIZE] = "m"
    # data[InputType.IMAGE_FORMAT] = "png"
    data[InputType.IMAGE_SIZE] = 1200
    data[InputType.DATA_TYPE] = "cdf"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2038
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
        base_path, "data", "input_files", "LS2_Plume_01_point_seasonal.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS2_Plume_01_point_seasonal.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index, None


def get_ls2_test_region_data():
    data, _, _, _, _ = get_ls2_test_point_data()
    data[InputType.AREA] = "country|England and Wales"
    data[InputType.SPATIAL_REPRESENTATION] = "country"
    data[InputType.OVERLAY_PROBABILITY_LEVELS] = True

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "LS2_Plume_01_country_monthly.nc"
    )
    overlay_input_files = path.join(
        base_path, "data", "input_files", "LS2_Plume_01_country_monthly_overlay.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "LS2_Plume_01_country_monthly.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index, overlay_input_files


def get_ms4_test_gauge_point_data():
    data = {}
    data[InputType.AREA] = ["gauge_point", 50.83, -1.08]
    data[InputType.COLLECTION] = "marine-sim"
    data[InputType.VARIABLE] = "stillWaterReturnLevel"
    data[InputType.SCENARIO] = "rcp45"

    # temporal options
    data[InputType.YEAR] = 2060

    # process constants
    data[InputType.METHOD] = "return-periods"
    data[InputType.DATA_TYPE] = "percentile"

    base_path = path.abspath(path.dirname(__file__))
    input_files = path.join(
        base_path, "data", "input_files", "MS4_ReturnLevels_01_gauge_point.nc"
    )

    reference_files = [
        path.join(
            base_path, "data", "expected_outputs", "MS4_ReturnLevels_01_gauge_point.csv"
        )
    ]

    output_file_index = [0]
    return data, input_files, reference_files, output_file_index, None


class PlumeCsvTestCase(unittest.TestCase):
    def test_plume_csv(self):
        """
        Test that the plume csv writer writes the correct csv values.
        """
        inputs = [
            (get_ls1_test_prob_point_data()),
            (get_ls1_test_prob_region_data()),
            (get_ls2_test_point_data()),
            (get_ls2_test_region_data()),
            (get_ms4_test_gauge_point_data()),
        ]

        for (
            data,
            input_files,
            reference_files,
            output_file_index,
            overlay_input_files,
        ) in inputs:
            with self.subTest(
                data=data,
                input_files=input_files,
                reference_files=reference_files,
                output_file_index=output_file_index,
                overlay_input_files=overlay_input_files,
            ):
                diff = run_write_test(
                    data,
                    input_files,
                    reference_files,
                    output_file_index,
                    PlotType.PLUME_PLOT,
                    overlay_input_files,
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
