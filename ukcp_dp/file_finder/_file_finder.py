import os

from ukcp_dp.constants import DATA_DIR, DATA_SOURCE_PROB, \
    DATA_SOURCE_PROB_MIN_YEAR, DATA_SOURCE_GCM, DATA_SOURCE_RCM, \
    DATA_SOURCE_MARINE, DATA_SOURCE_MARINE_MIN_YEAR, \
    DATA_SOURCE_MARINE_MAX_YEAR, InputType, METHOD_EXPLORATORY, \
    OTHER_MAX_YEAR, AreaType, TemporalAverageType

import logging
log = logging.getLogger(__name__)


# month and day
START_MONTH_DAY = '1201'
END_MONTH_DAY = '1130'
START_MONTH_DAY_CM = '189912'
END_MONTH_DAY_CM = '209911'

VERSION = 'latest'

RIVER = 'river'
REGION = 'region'


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
    if (input_data.get_value(InputType.DATA_SOURCE) in
            [DATA_SOURCE_PROB, DATA_SOURCE_MARINE]):
        file_list['main'] = _get_prob_file_list(input_data)

    elif (input_data.get_value(InputType.DATA_SOURCE) in
            [DATA_SOURCE_GCM, DATA_SOURCE_RCM]):
        file_list['main'] = _get_cm_file_list(input_data)

        if input_data.get_value(InputType.BASELINE) is not None:
            file_list['baseline'] = _get_file_list_for_baseline(input_data)

    # the file list for an overlay of probability levels
    if (input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is not None
            and
            input_data.get_value(
                InputType.OVERLAY_PROBABILITY_LEVELS) is True):
        if input_data.get_value(InputType.DATA_SOURCE) == DATA_SOURCE_PROB:
            file_list_overlay = file_list['main']
        else:
            file_list_overlay = _get_prob_file_list(input_data)

        if len(file_list_overlay) == 1:
            file_list['overlay'] = file_list_overlay
        # else: we do not currently deal with more than one scenario for an
        # overlay
    return file_list


def _get_prob_file_list(input_data):
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

    spatial_representation = _get_prob_spatial_representation(input_data)

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

    # December's data is included with the next year so if a single year has
    # been selected
    if year_minimum == year_maximum:
        year_maximum = year_maximum + 1

    for variable in variables:
        # generate a list of files for each variable
        # NB the marine data are all annual

        file_list_per_scenario = []
        for scenario in input_data.get_value(InputType.SCENARIO):
            # generate a list of files for each scenario
            file_path = _get_prob_file_path(
                input_data, scenario, spatial_representation, variable)

            if (input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) ==
                    TemporalAverageType.ANNUAL
                    or spatial_representation != '25km'):
                if (input_data.get_value(InputType.DATA_SOURCE) ==
                        DATA_SOURCE_MARINE):
                    file_name = _get_marine_file_name(
                        input_data, scenario, variable)
                else:
                    # current thinking is that there will only be one file
                    file_name = '*'
                file_list_per_scenario.append(
                    [os.path.join(file_path, file_name)])
                continue

            scenario_file_list = []

            for year in range(year_minimum, (year_maximum + 1)):
                # We cannot check for DATA_SOURCE_PROB as this may be an
                # overlay
                if (input_data.get_value(InputType.DATA_SOURCE) !=
                        DATA_SOURCE_MARINE and year == OTHER_MAX_YEAR):
                    # there is not data for December of the last year
                    continue
                file_name = _get_prob_file_name(
                    input_data, scenario, spatial_representation, variable,
                    year)
                scenario_file_list.append(os.path.join(file_path, file_name))

            file_list_per_scenario.append(scenario_file_list)

        file_lists_per_variable[variable] = file_list_per_scenario

    return file_lists_per_variable


def _get_prob_spatial_representation(input_data):
    spatial_representation = input_data.get_value(
        InputType.SPATIAL_REPRESENTATION)

    if spatial_representation == AreaType.RIVER_BASIN:
        spatial_representation = RIVER
    elif spatial_representation == AreaType.ADMIN_REGION:
        spatial_representation = REGION
    elif spatial_representation == AreaType.COUNTRY:
        pass
    else:
        # we cannot rely on the input value as this file list may be for the
        # overlay
        spatial_representation = '25km'

    return spatial_representation


def _get_prob_file_path(input_data, scenario, spatial_representation,
                        variable):

    if (input_data.get_value(InputType.DATA_SOURCE) == DATA_SOURCE_MARINE):

        file_path = os.path.join(
            DATA_DIR,
            input_data.get_value(InputType.DATA_SOURCE),
            'msl-proj*',
            scenario,
            variable,
            VERSION)
    else:

        file_path = os.path.join(
            DATA_DIR,
            DATA_SOURCE_PROB,
            'uk',
            spatial_representation,
            scenario,
            input_data.get_value(InputType.DATA_TYPE),
            variable,
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
            VERSION)

    return file_path


def _get_prob_file_name(input_data, scenario, spatial_representation,
                        variable, year):
    # the year starts in December, so subtract 1 from the year
    start_date = '{year}{mon_day}'.format(
        year=year - 1, mon_day=START_MONTH_DAY)
    end_date = '{year}{mon_day}'.format(
        year=year, mon_day=END_MONTH_DAY)

    file_name = ('{variable}_{scenario}_{data_source}_uk_'
                 '{spatial_representation}_{data_type}_{temporal_type}_'
                 '{start_data}-{end_date}.nc'.format(
                     variable=variable,
                     scenario=scenario,
                     data_source=DATA_SOURCE_PROB,
                     spatial_representation=spatial_representation,
                     data_type=input_data.get_value(InputType.DATA_TYPE),
                     temporal_type=input_data.get_value(
                         InputType.TEMPORAL_AVERAGE_TYPE),
                     start_data=start_date,
                     end_date=end_date))
    return file_name


def _get_marine_file_name(input_data, scenario, variable):
    start_date = DATA_SOURCE_MARINE_MIN_YEAR
    if (input_data.get_value(InputType.METHOD) == METHOD_EXPLORATORY):
        end_date = DATA_SOURCE_MARINE_MAX_YEAR
    else:
        end_date = OTHER_MAX_YEAR

    file_name = ('{variable}_{data_source}_{scenario}_ann_'
                 '{start_data}-{end_date}.nc'.format(
                     variable=variable,
                     scenario=scenario,
                     data_source=DATA_SOURCE_MARINE,
                     start_data=start_date,
                     end_date=end_date))
    return file_name


def _get_cm_file_list(input_data):
    """
    Get a list of files based on the data provided in the input data.

    @param input_data (InputData): an InputData object

    @return a dict where
        key: (str) variable name
        value: list of lists where:
            each list is a list of files per scenario, per variable, including
            their full paths
    """
    year_minimum = input_data.get_value(InputType.YEAR_MINIMUM)
    year_maximum = input_data.get_value(InputType.YEAR_MAXIMUM)
    return _get_cm_file_list_for_range(
        input_data, year_minimum, year_maximum)


def _get_file_list_for_baseline(input_data):
    """
    Get a list of files for the baseline based on the data provided in the
    input data.

    @param input_data (InputData): an InputData object

    @return a dict where
        key: (str) variable name
        value: list of lists where:
            each list is a list of files per scenario, per variable, including
            their full paths
    """
    baseline = input_data.get_value(InputType.BASELINE)
    year_minimum,  year_maximum = baseline.split('-')
    return _get_cm_file_list_for_range(input_data, int(year_minimum),
                                       int(year_maximum))


def _get_cm_file_list_for_range(input_data, year_minimum, year_maximum):
    variables = input_data.get_value(InputType.VARIABLE)

    spatial_representation = _get_cm_spatial_representation(input_data)

    file_lists_per_variable = {}

    for variable in variables:
        # generate a list of files for each variable
        # we need to use the variable root and calculate the anomaly later
        variable_prefix = variable.split('Anom')[0]

        file_list_per_scenario = []
        for scenario in input_data.get_value(InputType.SCENARIO):
            # generate a list of files for each scenario

            ensemble_file_list = []
            for ensemble in input_data.get_value(InputType.ENSEMBLE):
                file_path = _get_cm_file_path(
                    input_data, spatial_representation, variable_prefix,
                    scenario, ensemble)
                if (input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) ==
                        TemporalAverageType.ANNUAL
                        or spatial_representation != '12km'):
                    # current thinking is that there will only be one file
                    ensemble_file_list.append(os.path.join(file_path, '*'))
                    continue

                # generate a list of files for each ensemble
                for year in range(year_minimum, (year_maximum + 1)):
                    file_name = _get_cm_file_name(
                        input_data, spatial_representation, variable_prefix,
                        scenario, ensemble, year)
                    ensemble_file_list.append(
                        os.path.join(file_path, file_name))

            file_list_per_scenario.append(ensemble_file_list)

        file_lists_per_variable[variable] = file_list_per_scenario

    return file_lists_per_variable


def _get_cm_spatial_representation(input_data):
    spatial_representation = input_data.get_value(
        InputType.SPATIAL_REPRESENTATION)

    if spatial_representation == AreaType.RIVER_BASIN:
        spatial_representation = RIVER
    elif spatial_representation == AreaType.ADMIN_REGION:
        spatial_representation = REGION
    return spatial_representation


def _get_cm_file_path(input_data, spatial_representation, variable, scenario,
                      ensemble):
    file_path = os.path.join(
        DATA_DIR,
        input_data.get_value(InputType.DATA_SOURCE),
        'uk',
        spatial_representation,
        scenario,
        ensemble,
        variable,
        input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
        VERSION)

    return file_path


def _get_cm_file_name(input_data, spatial_representation, variable, scenario,
                      ensemble, year):

    # the year starts in December, so subtract 1 from the year
    if (input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) ==
            TemporalAverageType.MONTHLY):
        start_date = '{year}{mon_day}'.format(
            year=year - 1, mon_day=START_MONTH_DAY_CM)
        end_date = '{year}{mon_day}'.format(
            year=year, mon_day=END_MONTH_DAY_CM)
    else:  # seasonal
        start_date = '{year}{mon_day}'.format(
            year=year - 1, mon_day=START_MONTH_DAY)
        end_date = '{year}{mon_day}'.format(
            year=year, mon_day=END_MONTH_DAY)

    # we need to use the variable root and calculate the anomaly later
    variable = variable.split('Anom')[0]
    file_name = ('{variable}_{scenario}_{data_source}_uk_{spatial_'
                 'representation}_{ensemble}_{temporal_type}_{start_data}-'
                 '{end_date}.nc'.format(
                     variable=variable,
                     scenario=scenario,
                     data_source=input_data.get_value(InputType.DATA_SOURCE),
                     spatial_representation=spatial_representation,
                     source=input_data.get_value(InputType.DATA_SOURCE),
                     ensemble=ensemble,
                     temporal_type=input_data.get_value(
                         InputType.TEMPORAL_AVERAGE_TYPE),
                     start_data=start_date,
                     end_date=end_date))

    return file_name
