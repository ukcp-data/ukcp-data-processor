import os

from ukcp_dp.constants import DATA_DIR, DATA_SOURCE_PROB, \
    DATA_SOURCE_PROB_MIN_YEAR, InputType

import logging
log = logging.getLogger(__name__)


# month and day
MONTH_START_DATE = '0101'
MONTH_END_DATE = '1201'
SEASON_START_DATE = '1201'
SEASON_END_DATE = '1130'

VERSION = 'v20170331'


def get_file_lists(input_data):
    """
    Get lists of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object

    @return a dict of lists of files, including their full paths
        key - 'main' or 'overlay'
        value - a dict where
            key: (str) variable name
            value: list of lists where:
                each list is a list of files per scenario, per variable,
                including their full paths
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
    if (input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is not None
            and
            input_data.get_value(
                InputType.OVERLAY_PROBABILITY_LEVELS) is True):
        if input_data.get_value(InputType.DATA_SOURCE) == DATA_SOURCE_PROB:
            file_list_overlay = file_list['main']
        else:
            file_list_overlay = _get_land_prob_file_list(input_data)

        if len(file_list_overlay) == 1:
            file_list['overlay'] = file_list_overlay
        # else: we do not currently deal with more than one scenario for an
        # overlay
    return file_list


def _get_land_prob_file_list(input_data):
    """
    Get a list of files based on the data provided in the input data. As this
    may be the file list for the overlay, some fields are not from the user
    input.

    @param input_data (InputData): an InputData object

    @return a dict where
        key: (str) variable name
        value: list of lists where:
            each list is a list of files per scenario, per variable, including
            their full paths
    """
    variables = input_data.get_value(InputType.VARIABLE)

    spatial_representation = _get_land_prob_spatial_representation(input_data)

    file_lists_per_variable = {}

    # if this is a selection for on overlay then the dates will not have been
    # validated against this dataset. Check the dates and adjust the minimum if
    # needed
    year_maximum = input_data.get_value(InputType.YEAR_MAXIMUM)
    year_minimum = input_data.get_value(InputType.YEAR_MINIMUM)
    if year_maximum < DATA_SOURCE_PROB_MIN_YEAR:
        return {}
    elif year_minimum < DATA_SOURCE_PROB_MIN_YEAR:
        year_minimum = DATA_SOURCE_PROB_MIN_YEAR

    dataset_id = ('ukcp18-{data_source}-uk-{spatial_representation}-'
                  '{temporal_type}'.format(
                      data_source=DATA_SOURCE_PROB,
                      spatial_representation=spatial_representation,
                      temporal_type=input_data.get_value(
                          InputType.TEMPORAL_AVERAGE_TYPE)))

    for variable in variables:
        # generate a list of files for each variable

        file_list_per_scenario = []
        for scenario in input_data.get_value(InputType.SCENARIO):
            # generate a list of files for each scenario
            file_path = _get_land_prob_file_path(
                input_data, scenario, spatial_representation, variable)

            if input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) == 'ann':
                # current thinking is that there will only be one file, but
                # I'm not sure of the date format yet
                file_list_per_scenario.append([os.path.join(file_path, '*')])
                continue

            scenario_file_list = []

            for year in range(year_minimum, (year_maximum + 1)):
                file_name = _get_land_prob_file_name(
                    dataset_id, input_data, scenario, variable, year)
                scenario_file_list.append(os.path.join(file_path, file_name))

            file_list_per_scenario.append(scenario_file_list)

        file_lists_per_variable[variable] = file_list_per_scenario

    return file_lists_per_variable


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
        input_data.get_value(InputType.DATA_TYPE),
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
                 '{data_type}_{temporal_type}_{start_data}-'
                 '{end_date}.nc'.format(
                     variable=variable,
                     scenario=scenario,
                     dataset_id=dataset_id,
                     data_type=input_data.get_value(InputType.DATA_TYPE),
                     temporal_type=input_data.get_value(
                         InputType.TEMPORAL_AVERAGE_TYPE),
                     start_data=start_date,
                     end_date=end_date))
    return file_name


def _get_file_list_type_2(input_data):
    """
    Get a list of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object

    @return a dict where
        key: (str) variable name
        value: list of lists where:
            each list is a list of files per scenario, per variable, including
            their full paths
    """
    variables = input_data.get_value(InputType.VARIABLE)

    file_lists_per_variable = {}

    for variable in variables:
        # generate a list of files for each variable

        file_list_per_scenario = []
        for scenario in input_data.get_value(InputType.SCENARIO):
            # generate a list of files for each scenario

            ensemble_file_list = []
            for ensemble in input_data.get_value(InputType.ENSEMBLE):
                # generate a list of files for each ensemble
                ensemble_file_list.append(_get_file_list_for_ensemble(
                    input_data, variable, scenario, ensemble))

            file_list_per_scenario.append(ensemble_file_list)

        file_lists_per_variable[variable] = file_list_per_scenario

    return file_lists_per_variable


def _get_file_list_for_ensemble(input_data, variable, scenario, ensemble):
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

    # we need to use the variable root and calculate the anomaly later
    variable = variable.split('Anom')[0]
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
