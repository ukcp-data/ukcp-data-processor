import os

from ukcp_dp.constants import DATA_DIR, InputType


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
        file_list['main'] = _get_file_list_type_1(input_data)
    elif (input_data.get_value(InputType.DATA_SOURCE) in
            ['global_realisations', 'regional_realisations']):
        file_list['main'] = _get_file_list_type_2(input_data)
    if input_data.get_value(InputType.SHOW_PROBABILITY_LEVELS) is True:
        if (input_data.get_value(InputType.DATA_SOURCE) ==
                'land_probabilistic'):
            file_list['overlay'] = file_list['main']
        else:
            file_list['overlay'] = _get_file_list_type_1(input_data)

    return file_list


def _get_file_list_type_1(input_data):
    """
    Get a list of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object

    @return a list of files, including their full paths
    """
    # TODO currently the path/file names do not include "Anom"
    variable = input_data.get_value(InputType.VARIABLE).split('Anom')[0]

    file_path = os.path.join(
        DATA_DIR,
        'land-prob',
        input_data.get_value(InputType.SPATIAL_REPRESENTATION),
        input_data.get_value(InputType.SCENARIO),
        'percentile',
        variable,
        input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
        'v20170331')

    file_list = []

    dataset_id = 'ukcp18-land-prob-{}'.format(
        input_data.get_value(InputType.SPATIAL_REPRESENTATION))

    for year in range(input_data.get_value(InputType.YEAR_MINIMUM),
                      (input_data.get_value(InputType.YEAR_MAXIMUM) + 1)):
        file_name = ('{variable}_{scenario}_{dataset_id}_'
                     'percentile_{temporal_type}_{year}0101-'
                     '{year}1201.nc'.format(
                         variable=variable,
                         scenario=input_data.get_value(InputType.SCENARIO),
                         dataset_id=dataset_id,
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

    ensemble_set = input_data.get_value(InputType.ENSEMBLE)

    for ensemble in ensemble_set:
        file_list.append(_get_file_list_for_ensemble(input_data, ensemble))
    return file_list


def _get_file_list_for_ensemble(input_data, ensemble):
    if input_data.get_value(InputType.SPATIAL_REPRESENTATION) == 'river_basin':
        spatial_representation = '-river'
    else:
        spatial_representation = ''

    dataset_id = ('ukcp18-land-gcm-uk{spatial_representation}-'
                  '{temporal_type}'.format(
                      input_data.get_value(InputType.SPATIAL_REPRESENTATION),
                      spatial_representation=spatial_representation,
                      temporal_type=input_data.get_value_label(
                          InputType.TEMPORAL_AVERAGE_TYPE).lower()))

    # we need to use the variable root and calculate the anomaly later
    variable = input_data.get_value(InputType.VARIABLE).split('Anom')[0]
    file_name = ('{variable}_{scenario}_{dataset_id}_{ensemble}_'
                 '{temporal_type}_19010101-21001201.nc'.format(
                     variable=variable,
                     scenario=input_data.get_value(InputType.SCENARIO),
                     dataset_id=dataset_id,
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
        variable,
        input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
        'v20170331',
        file_name)

    return file_path
