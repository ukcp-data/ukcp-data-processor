from ukcp_dp.constants import DATA_DIR, InputType
from ukcp_dp.vocab_manager import get_ensemble_member_set
import os


def get_file_lists(input_data):
    """
    Get lists of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object

    @return a dict of lists of files, including their full paths
        key - 'main' or 'overlay'
        value - list of file paths
    """
    file_list = {}
    if (input_data.get_value(InputType.DATA_SOURCE) in
            ['land_probabilistic', ]):
        file_list['main'] = _get_file_list_type_1(
            input_data, input_data.get_value(InputType.DATA_SOURCE))
    elif (input_data.get_value(InputType.DATA_SOURCE) in
            ['global_realisations', 'regional_realisations']):
        file_list['main'] = _get_file_list_type_2(input_data)
    if input_data.get_value(InputType.SHOW_PROBABILITY_LEVELS) is True:
        if (input_data.get_value(InputType.DATA_SOURCE) ==
                'land_probabilistic'):
            file_list['overlay'] = file_list['main']
        else:
            file_list['overlay'] = _get_file_list_type_1(
                input_data, input_data.get_value(InputType.DATA_SOURCE))
    return file_list


def _get_file_list_type_1(input_data, data_source):
    """
    Get a list of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object
    @param data_source (Str): the data source

    @return a list of files, including their full paths
    """
    file_path = os.path.join(
        DATA_DIR,
        data_source,
        input_data.get_value(InputType.SPATIAL_REPRESENTATION),
        input_data.get_value(InputType.SCENARIO),
        'percentile',
        input_data.get_value(InputType.VARIABLE),
        'v20170331')
    file_list = []

    for year in range(input_data.get_value(InputType.YEAR_MINIMUM),
                      (input_data.get_value(InputType.YEAR_MAXIMUM) + 1)):
        file_name = ('{variable}_{scenario}_ukcp18_{source}_'
                     '{spatial_representation}_{temporal_type}_{year}0101-'
                     '{year}1201.nc'.format(
                         variable=input_data.get_value(InputType.VARIABLE),
                         scenario=input_data.get_value(InputType.SCENARIO),
                         source=data_source,
                         spatial_representation=input_data.get_value(
                             InputType.SPATIAL_REPRESENTATION),
                         temporal_type=input_data.get_value(
                             InputType.TEMPORAL_AVERAGE_TYPE),
                         year=year))
        file_list.append(os.path.join(file_path, file_name))

    return file_list


def _get_file_list_type_2(input_data):
    """
    Get a list of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object

    @return a list of files, including their full paths
    """
    file_list = []
    for ensemble in get_ensemble_member_set(
            input_data.get_value(InputType.DATA_SOURCE)):
        file_list.append(_get_file_list_for_ensemble(input_data, ensemble))
    return file_list


def _get_file_list_for_ensemble(input_data, ensemble):
    file_name = ('{variable}_{scenario}_ukcp18-land-gcm-uk-river-monthly_'
                 '{ensemble}_{temporal_type}_19010101-'
                 '21001201.nc'.format(
                     variable=input_data.get_value(InputType.VARIABLE),
                     scenario=input_data.get_value(InputType.SCENARIO),
                     source=input_data.get_value(InputType.DATA_SOURCE),
                     ensemble=ensemble,
                     temporal_type=input_data.get_value(
                         InputType.TEMPORAL_AVERAGE_TYPE)))

    file_path = os.path.join(
        DATA_DIR,
        'land-sim',
        input_data.get_value(InputType.SPATIAL_REPRESENTATION),
        'uk',
        input_data.get_value(InputType.SCENARIO),
        ensemble,
        input_data.get_value(InputType.VARIABLE),
        input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
        'v20170331',
        file_name)

    return file_path
