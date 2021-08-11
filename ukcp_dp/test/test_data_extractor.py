from os import path
import unittest

from ukcp_dp import InputType
from ukcp_dp.data_extractor import DataExtractor
from ukcp_dp._input_data import InputData
from ukcp_dp.vocab_manager import Vocab


def get_ls2_test_bbox_data():
    data = {}
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "60km"
    data[InputType.COLLECTION] = "land-gcm"
    data[InputType.VARIABLE] = "tas"
    data[InputType.SCENARIO] = "rcp26"

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2028

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
        base_path, "data", "input_files", "LS2_Subset_01_bbox_seasonal.nc*"
    )

    file_lists = {"main": {data[InputType.VARIABLE]: [[input_files]]}}
    # file_lists["main"][data[InputType.VARIABLE]] = input_files

    return data, file_lists


def get_ls2_test_y_line_data():
    data, file_lists = get_ls2_test_bbox_data()
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, -84667.14, 1230247.3]

    return data, file_lists


def get_ls2_test_x_line_data():
    data, file_lists = get_ls2_test_bbox_data()
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, 676489.68, -114260.0]

    return data, file_lists


def get_ls2_test_dot_line_data():
    data, file_lists = get_ls2_test_bbox_data()
    data[InputType.AREA] = ["bbox", -84667.14, -114260.0, -84667.14, -114260.0]

    return data, file_lists


class DataEtractorPromoteXYTestCase(unittest.TestCase):
    def test_promote_x_y_coords(self):
        """
        Test that the y and x coordinates are added back in the correct place in the
        cube dimensions.
        """
        inputs = [
            (get_ls2_test_bbox_data()),
            (get_ls2_test_y_line_data()),
            (get_ls2_test_x_line_data()),
            (get_ls2_test_dot_line_data()),
        ]

        for data, input_files in inputs:
            with self.subTest(data=data, input_files=input_files):

                vocab = Vocab()
                input_data = InputData(vocab)
                input_data.set_inputs(data)

                data_extractor = DataExtractor(input_files, input_data, None)

                cube = data_extractor.get_cubes()[0]
                dim_coords = []
                for coord in cube.coords(dim_coords=True):
                    dim_coords.append(coord.name())

                self.assertEqual(dim_coords[0], "ensemble_member")
                self.assertEqual(dim_coords[1], "time")
                self.assertEqual(dim_coords[2], "projection_y_coordinate")
                self.assertEqual(dim_coords[3], "projection_x_coordinate")


if __name__ == "__main__":
    unittest.main()
