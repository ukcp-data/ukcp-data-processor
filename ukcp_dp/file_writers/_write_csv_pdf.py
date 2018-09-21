import collections
import logging

from ukcp_dp.constants import DataType, InputType, PDF_LABEL, SOFTWARE_VERSION
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
            self.header.append('{var}'.format(var=var))
            self.header.append(PDF_LABEL)

            pdf_data = self._get_pdf_data_for_scenario(
                cube.attributes['scenario'])
            cdf_data = cube.data
            self._add_data(cdf_data, pdf_data, key_list)

            # now write the data
            output_data_file_path = self._get_full_file_name(
                '_{}'.format(cube.attributes['scenario']))
            self._write_data_dict(output_data_file_path, key_list, scenario)
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

    def _write_data_dict(self, output_data_file_path, key_list, scenario):
        """
        Write out the column headers and data_dict.

        We have to override the method in the base class as we do not wish all
        of the scenarios to be written to the headers
        """
        user_inputs = {}
        all_user_inputs = self.input_data.get_user_inputs()
        for key in all_user_inputs:
            if key in self.ignore_in_header:
                    continue
            user_inputs[key] = all_user_inputs[key]
        user_inputs['Software Version'] = SOFTWARE_VERSION

        header_string = ','.join(self.header)
        header_string = header_string.replace('\n,', '\n')
        header_length = len(header_string.split('\n')) + \
            len(user_inputs.keys()) + 1
        with open(output_data_file_path, 'w') as output_data_file:
            output_data_file.write('header length,{}\n'.format(header_length))
            keys = user_inputs.keys()
            keys.sort()
            for key in keys:
                if key == 'Scenario':
                    output_data_file.write('Scenario,{value}\n'.format(value=scenario))
                else:
                    output_data_file.write('{key},{value}\n'.format(
                        key=key, value=user_inputs[key]))
            output_data_file.write(header_string)
            output_data_file.write('\n')

            for key in key_list:
                line_out = '{key},{values}\n'.format(
                    key=key, values=','.join(self.data_dict[key]))
                output_data_file.write(line_out)

        # reset the data dict
        self.data_dict = collections.OrderedDict()
