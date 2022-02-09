from os import path
import unittest

from ukcp_dp import InputType, PlotType
from ukcp_dp.constants import DataFormat
from ukcp_dp.test.test_write import run_write_test
from ukcp_dp.test.test_write_csv_plume import get_ls2_test_point_data


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
        path.join(base_path, "data", "input_files", "LS2_Plume_01_country_monthly.nc"),
        path.join(
            base_path, "data", "input_files", "LS2_Plume_01_country_monthly_overlay.nc"
        ),
    ]

    output_file_index = [0, 1]
    return data, input_files, reference_files, output_file_index, overlay_input_files


class NetcdfTestCase(unittest.TestCase):
    def test_netcdf(self):
        """
        Test that the Net CDF writer writes the correct Net CDF values.
        """
        inputs = [(get_ls2_test_region_data())]

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
                    data_format=DataFormat.NET_CDF,
                )
                self.assertEqual(diff, "", diff)


if __name__ == "__main__":
    unittest.main()
