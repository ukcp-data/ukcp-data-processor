import os

from ukcp_dp.constants import DATA_DIR, DATA_SOURCE_PROB, InputType

import logging
log = logging.getLogger(__name__)


# month and day
MONTH_START_DATE = '0101'
MONTH_END_DATE = '1201'
SEASON_START_DATE = '1201'
SEASON_END_DATE = '1101'

VERSION = 'v20170331'


def get_file_lists(input_data):
    """
    Get lists of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object

    @return a dict of lists of files, including their full paths
        key - 'main' or 'overlay'
        value - for main, a list of lists of file paths
              - for overlay, a list of file paths
    """
    log.info('get_file_lists')
    file_list = {}

    # the main file list
    if (input_data.get_value(InputType.DATA_SOURCE) == DATA_SOURCE_PROB):
        file_list['main'] = _get_land_prob_file_list(input_data)

    elif (input_data.get_value(InputType.DATA_SOURCE) in
            ['land-gcm', 'land-rcm']):
        file_list['main'] = _get_file_list_type_2(input_data)

    # the file list for an overlay of probability levels
    if input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is True:
        if input_data.get_value(InputType.DATA_SOURCE) == DATA_SOURCE_PROB:
            file_list_overlay = file_list['main']
        else:
            file_list_overlay = _get_land_prob_file_list(input_data)

        if len(file_list_overlay) == 1:
            file_list['overlay'] = file_list_overlay[0]
        # else: we do not currently deal with more than one scenario for an
        # overlay
    return file_list


def _get_land_prob_file_list(input_data):
    """
    Get a list of files based on the data provided in the input data. As this
    may be the file list for the overlay, some fields are not from the user
    input.

    @param input_data (InputData): an InputData object

    @return a list of lists of files, including their full paths
    """
    # TODO currently the path/file names do not include "Anom"
    variable = input_data.get_value(InputType.VARIABLE).split('Anom')[0]

    spatial_representation = _get_land_prob_spatial_representation(input_data)

    file_list = []

    dataset_id = ('ukcp18-{data_source}-uk-{spatial_representation}-'
                  '{temporal_type}'.format(
                      data_source=DATA_SOURCE_PROB,
                      spatial_representation=spatial_representation,
                      temporal_type=input_data.get_value(
                          InputType.TEMPORAL_AVERAGE_TYPE)))

    for scenario in input_data.get_value(InputType.SCENARIO):
        file_path = _get_land_prob_file_path(
            input_data, scenario, spatial_representation, variable)

        if input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) == 'ann':
            # current thinking is that there will only be one file, but I'm not
            # sure of the date format yet
            file_list.append([os.path.join(file_path, '*')])
            continue

        scenario_file_list = []

        for year in range(input_data.get_value(InputType.YEAR_MINIMUM),
                          (input_data.get_value(InputType.YEAR_MAXIMUM) + 1)):
            file_name = _get_land_prob_file_name(
                dataset_id, input_data, scenario, variable, year)
            scenario_file_list.append(os.path.join(file_path, file_name))

        file_list.append(scenario_file_list)

    return file_list


def _get_land_prob_spatial_representation(input_data):
    spatial_representation = input_data.get_value(
        InputType.SPATIAL_REPRESENTATION)

    if spatial_representation == 'river_basin':
        spatial_representation = 'river'
    elif spatial_representation == 'admin_region':
        spatial_representation = 'admin'
    elif spatial_representation == 'country':
        pass
    else:
        # we cannot rely on the input value as this file list may be for the
        # overlay
        spatial_representation = '25km'

    return spatial_representation


def _get_land_prob_file_path(input_data, scenario, spatial_representation,
                             variable):
    file_path = os.path.join(
        DATA_DIR,
        DATA_SOURCE_PROB,
        spatial_representation,
        'uk',
        scenario,
        'percentile',
        variable,
        input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
        VERSION)
    return file_path


def _get_land_prob_file_name(dataset_id, input_data, scenario, variable, year):
    if input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) == 'mon':
        start_date = '{year}{mon_day}'.format(
            year=year, mon_day=MONTH_START_DATE)
        end_date = '{year}{mon_day}'.format(
            year=year, mon_day=MONTH_END_DATE)
    else:  # 'seas'
        start_date = '{year}{mon_day}'.format(
            year=year - 1, mon_day=SEASON_START_DATE)
        end_date = '{year}{mon_day}'.format(
            year=year, mon_day=SEASON_END_DATE)

    file_name = ('{variable}_{scenario}_{dataset_id}_'
                 'percentile_{temporal_type}_{start_data}-'
                 '{end_date}.nc'.format(
                     variable=variable,
                     scenario=scenario,
                     dataset_id=dataset_id,
                     temporal_type=input_data.get_value(
                         InputType.TEMPORAL_AVERAGE_TYPE),
                     start_data=start_date,
                     end_date=end_date))
    return file_name


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

    # TODO there should be one list per scenario
    return [file_list]


def _get_file_list_for_ensemble(input_data, ensemble):
    spatial_representation = input_data.get_value(
        InputType.SPATIAL_REPRESENTATION)
    if spatial_representation == 'river_basin':
        spatial_representation = 'river'
    elif spatial_representation == 'admin_region':
        spatial_representation = 'admin'

    dataset_id = ('ukcp18-{data_source}-uk-{spatial_representation}-'
                  '{temporal_type}'.format(
                      data_source=input_data.get_value(InputType.DATA_SOURCE),
                      spatial_representation=spatial_representation,
                      temporal_type=input_data.get_value(
                          InputType.TEMPORAL_AVERAGE_TYPE)))

    # TODO
    scenario = input_data.get_value(InputType.SCENARIO)[0]

    # we need to use the variable root and calculate the anomaly later
    variable = input_data.get_value(InputType.VARIABLE).split('Anom')[0]
    file_name = ('{variable}_{scenario}_{dataset_id}_{ensemble}_'
                 '{temporal_type}_*'.format(
                     variable=variable,
                     scenario=scenario,
                     dataset_id=dataset_id,
                     source=input_data.get_value(InputType.DATA_SOURCE),
                     ensemble=ensemble,
                     temporal_type=input_data.get_value(
                         InputType.TEMPORAL_AVERAGE_TYPE)))

    file_path = os.path.join(
        DATA_DIR,
        input_data.get_value(InputType.DATA_SOURCE),
        input_data.get_value(InputType.SPATIAL_REPRESENTATION),
        'uk',
        scenario,
        ensemble,
        variable,
        input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
        VERSION,
        file_name)

    return file_path
