from os import path
import unittest

from ukcp_dp import AreaType, InputType
from ukcp_dp._input_data import InputData
from ukcp_dp.constants import HADUK_DIR
from ukcp_dp.file_finder import get_file_lists
from ukcp_dp.validator import Validator
from ukcp_dp.vocab_manager import Vocab


def get_ls6_test_bbox():
    variable = "tasmax"
    data = {}
    data[InputType.AREA] = [AreaType.BBOX, -84667.14, -114260.0, 676489.68, 1230247.3]
    data[InputType.SPATIAL_REPRESENTATION] = "12km"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = variable

    # temporal options
    data[InputType.TIME_PERIOD] = "mam"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "seas"
    data[InputType.YEAR] = 2018

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "12km/tasmax/seas/latest/tasmax_hadukgrid_uk_12km_seas_201801-201812.nc",
            )
        ]
    ]

    return data, expected_file_lists, variable


def get_ls6_test_bbox_ann():
    data, _, _ = get_ls6_test_bbox()
    variable = "sun"
    data[InputType.VARIABLE] = variable

    # temporal options
    data[InputType.TIME_PERIOD] = "ann"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "ann"

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "12km/sun/ann/latest/sun_hadukgrid_uk_12km_ann_201801-201812.nc",
            )
        ]
    ]

    return data, expected_file_lists, variable


def get_ls6_test_bbox_mon():
    data, _, variable = get_ls6_test_bbox()

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"
    del data[InputType.YEAR]
    data[InputType.YEAR_MINIMUM] = 1980
    data[InputType.YEAR_MAXIMUM] = 1990

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198001-198012.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198101-198112.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198201-198212.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198301-198312.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198401-198412.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198501-198512.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198601-198612.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198701-198712.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198801-198812.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_198901-198912.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/mon/latest/tasmax_hadukgrid_uk_12km_mon_199001-199012.nc",
            ),
        ]
    ]

    return data, expected_file_lists, variable


def get_ls6_test_region():
    variable = "tasmax"
    data = {}
    data[InputType.AREA] = "admin_region|All administrative regions"
    data[InputType.SPATIAL_REPRESENTATION] = "admin_region"
    data[InputType.COLLECTION] = "land-obs"
    data[InputType.VARIABLE] = variable

    # temporal options
    data[InputType.TIME_PERIOD] = "aug"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "mon"
    data[InputType.YEAR] = 2018

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "region/tasmax/mon/latest/tasmax_hadukgrid_uk_region_mon_188401-202212.nc",
            )
        ]
    ]

    return data, expected_file_lists, variable


def get_ls6_test_river():
    data, _, _ = get_ls6_test_region()
    variable = "rainfall"
    data[InputType.AREA] = "river_basin|All river basins"
    data[InputType.SPATIAL_REPRESENTATION] = "river_basin"
    data[InputType.VARIABLE] = variable

    # temporal options
    del data[InputType.YEAR]
    data[InputType.YEAR_MINIMUM] = 1980
    data[InputType.YEAR_MAXIMUM] = 1981

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "river/rainfall/mon/latest/rainfall_hadukgrid_uk_river_mon_183601-202212.nc",
            )
        ]
    ]

    return data, expected_file_lists, variable


def get_ls6_test_country():
    data, _, _ = get_ls6_test_region()
    variable = "sun"
    data[InputType.AREA] = "country|England"
    data[InputType.SPATIAL_REPRESENTATION] = "country"
    data[InputType.VARIABLE] = variable

    # temporal options
    del data[InputType.YEAR]
    data[InputType.YEAR_MINIMUM] = 1980
    data[InputType.YEAR_MAXIMUM] = 1981

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "country/sun/mon/latest/sun_hadukgrid_uk_country_mon_191001-202212.nc",
            )
        ]
    ]

    return data, expected_file_lists, variable


def get_ls6_test_region_daily():
    data, _, variable = get_ls6_test_region()
    data[InputType.VARIABLE] = variable

    # temporal options
    data[InputType.TIME_PERIOD] = "day"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "day"
    data[InputType.YEAR] = 2018

    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "region/tasmax/day/latest/tasmax_hadukgrid_uk_region_day_19600101-20221231.nc",
            )
        ]
    ]

    return data, expected_file_lists, variable


def get_ls6_test_river_daily():
    data, _, variable = get_ls6_test_river()
    data[InputType.VARIABLE] = variable

    # temporal options
    data[InputType.TIME_PERIOD] = "day"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "day"

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "river/rainfall/day/latest/rainfall_hadukgrid_uk_river_day_18910101-20221231.nc",
            )
        ]
    ]

    return data, expected_file_lists, variable


def get_ls6_test_point():
    data, _, variable = get_ls6_test_bbox()

    data[InputType.AREA] = ["point", 437500.0, 337500.0]

    # temporal options
    data[InputType.TIME_PERIOD] = "day"
    data[InputType.TEMPORAL_AVERAGE_TYPE] = "day"
    del data[InputType.YEAR]
    data[InputType.YEAR_MINIMUM] = 2018
    data[InputType.YEAR_MAXIMUM] = 2018
    # image options
    data[InputType.FONT_SIZE] = "m"
    data[InputType.IMAGE_SIZE] = 1200

    expected_file_lists = [
        [
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180101-20180131.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180201-20180228.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180301-20180331.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180401-20180430.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180501-20180531.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180601-20180630.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180701-20180731.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180801-20180831.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20180901-20180930.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20181001-20181031.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20181101-20181130.nc",
            ),
            path.join(
                HADUK_DIR,
                "12km/tasmax/day/latest/tasmax_hadukgrid_uk_12km_day_20181201-20181231.nc",
            ),
        ]
    ]

    return data, expected_file_lists, variable


class LandObsFileFinderTestCase(unittest.TestCase):
    def setUp(self):
        self.vocab = Vocab()
        self.validator = Validator(self.vocab)

    def test_land_obs_file_finder(self):
        """
        Test that the land obs file finder finds the correct files.

        """
        inputs = [
            (get_ls6_test_bbox()),
            (get_ls6_test_bbox_ann()),
            (get_ls6_test_bbox_mon()),
            (get_ls6_test_region()),
            (get_ls6_test_river()),
            (get_ls6_test_country()),
            (get_ls6_test_region_daily()),
            (get_ls6_test_river_daily()),
            (get_ls6_test_point()),
        ]

        for data, expected_file_lists, variable in inputs:
            with self.subTest(
                data=data, expected_file_lists=expected_file_lists, variable=variable
            ):
                file_lists = self._run_file_finder_test(data)["main"][variable]
                for index, expected_file_list in enumerate(expected_file_lists):
                    file_lists[index].sort()
                    expected_file_list.sort()
                    self.assertEqual(file_lists[index], expected_file_list)

    def _run_file_finder_test(self, data):
        input_data = InputData(self.vocab)
        input_data.set_inputs(data)
        input_data = self.validator.validate(input_data)
        file_lists = get_file_lists(input_data)
        return file_lists


if __name__ == "__main__":
    unittest.main()
