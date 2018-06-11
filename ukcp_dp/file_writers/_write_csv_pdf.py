import logging

from ukcp_dp.constants import DataType, InputType, PDF_LABEL
from ukcp_dp.file_writers._base_csv_writer import BaseCsvWriter
from ukcp_dp.file_writers._utils import convert_to_2dp, convert_to_4dp


log = logging.getLogger(__name__)


class PdfCsvWriter(BaseCsvWriter):
    """
    The PDF CSV writer class.

    This class extends BaseCsvWriter with a _write_csv(self).
    """

    def _write_csv(self):
        """
        Write out the data, in CSV format, associated with a PDF plot.

        One file is produced per scenario.
        """
        output_file_list = []

        for cube in self.cube_list:
            if cube.attributes['prob_data_type'] == DataType.PDF:
                continue

            key_list = []

            scenario = self.vocab.get_collection_term_label(
                InputType.SCENARIO, cube.attributes['scenario'])

            var = self.input_data.get_value_label(
                InputType.VARIABLE)[0].encode('utf-8')
            self.header.append('{var}({scenario})'.format(
                scenario=scenario, var=var))
            self.header.append(PDF_LABEL)

            pdf_data = self._get_pdf_data_for_scenario(
                cube.attributes['scenario'])
            cdf_data = cube.data
            self._add_data(cdf_data, pdf_data, key_list)

            # now write the data
            output_data_file_path = self._get_full_file_name(
                '_{}'.format(cube.attributes['scenario']))
            self._write_data_dict(output_data_file_path, key_list)
            output_file_list.append(output_data_file_path)

        return output_file_list

    def _get_pdf_data_for_scenario(self, scenario):
        for scenario_cube in self.cube_list:
            if (scenario_cube.attributes['prob_data_type'] == DataType.PDF and
                    scenario_cube.attributes['scenario'] == scenario):
                return scenario_cube.data

    def _add_data(self, cdf_data, pdf_data, key_list):
        """
        Slice the cube over 'percentile' and update data_dict
        """
        for i, cdf_d in enumerate(cdf_data):
            pdf_point = convert_to_4dp(pdf_data[i])
            cdf_point = convert_to_2dp(cdf_d)
            try:
                self.data_dict[cdf_point].append(pdf_point)
            except KeyError:
                key_list.append(cdf_point)
                self.data_dict[cdf_point] = [pdf_point]
