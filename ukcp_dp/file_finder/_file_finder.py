import os

from ukcp_dp.constants import DATA_DIR, DATA_SERVICE_URL, COLLECTION_PROB, \
    COLLECTION_PROB_MIN_YEAR, COLLECTION_GCM, COLLECTION_RCM, \
    COLLECTION_MARINE, InputType, OTHER_MAX_YEAR, AreaType, \
    TemporalAverageType
from ukcp_dp.utils import get_baseline_range

import logging
log = logging.getLogger(__name__)


# month and day
START_MONTH_DAY = '1201'
END_MONTH_DAY = '1130'

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
    if (input_data.get_value(InputType.COLLECTION) in
            [COLLECTION_PROB, COLLECTION_MARINE]):
        file_list['main'] = _get_prob_file_list(input_data)

    elif (input_data.get_value(InputType.COLLECTION) in
            [COLLECTION_GCM, COLLECTION_RCM]):
        file_list['main'] = _get_cm_file_list(input_data)

        if input_data.get_value(InputType.BASELINE) is not None:
            file_list['baseline'] = _get_file_list_for_baseline(input_data)

    # the file list for an overlay of probability levels
    if (input_data.get_value(InputType.OVERLAY_PROBABILITY_LEVELS) is not None
            and
            input_data.get_value(
                InputType.OVERLAY_PROBABILITY_LEVELS) is True):
        if input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB:
            file_list_overlay = file_list['main']
        else:
            file_list_overlay = _get_prob_file_list(input_data)

        if len(file_list_overlay) == 1:
            file_list['overlay'] = file_list_overlay
        # else: we do not currently deal with more than one scenario for an
        # overlay
    return file_list


def get_absolute_paths(file_lists):
    """Take an object returned from get_file_lists and returns a flattened list
    of absolute file paths.

    @param file_list (dict): a dictionary returned from a get_file_lists call

    @return a list of absolute file paths
    """
    absolute_paths = []
    for key in file_lists:
        for variable_files in file_lists[key]:
            for file_paths in file_lists[key][variable_files]:
                for file_path in file_paths:
                    absolute_paths.append(_get_absolute_path(file_path))
    absolute_paths.sort()
    return absolute_paths


def _get_absolute_path(file_path):
    if '*' in file_path:
        path = os.path.realpath(file_path.split('*')[0])
        path = os.path.join(path, '*')
    else:
        path = os.path.realpath(file_path)

    path = path.replace(DATA_DIR, DATA_SERVICE_URL)
    return path


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
    if year_maximum < COLLECTION_PROB_MIN_YEAR:
        return {}
    elif year_minimum < COLLECTION_PROB_MIN_YEAR:
        year_minimum = COLLECTION_PROB_MIN_YEAR

    # December's data is included with the next year so if a single year has
    # been selected
    if year_minimum == year_maximum:
        year_maximum = year_maximum + 1

    for variable in variables:
        # generate a list of files for each variable
        # NB the marine data are all annual

        file_list_per_scenario = []
        for scenario in input_data.get_value(InputType.SCENARIO):
            file_list_per_scenario.extend(_get_file_list_per_scenario(
                input_data, scenario, spatial_representation, variable,
                year_minimum, year_maximum))

        file_lists_per_variable[variable] = file_list_per_scenario

    return file_lists_per_variable


def _get_file_list_per_scenario(input_data, scenario, spatial_representation,
                                variable, year_minimum, year_maximum):
    # generate a list of files for each scenario
    file_list_per_data_type = []
    for data_type in input_data.get_value(InputType.DATA_TYPE):
        file_path = _get_prob_file_path(
            data_type, input_data, scenario, spatial_representation, variable)

        if ((input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE) ==
                TemporalAverageType.ANNUAL or spatial_representation != '25km')
                or
                (input_data.get_value(InputType.COLLECTION) ==
                 COLLECTION_MARINE)):
            # current thinking is that there will only be one file
            file_name = '*'
            file_list_per_data_type.append(
                [os.path.join(file_path, file_name)])
            continue

        scenario_file_list = []

        for year in range(year_minimum, (year_maximum + 1)):
            # We cannot check for COLLECTION_PROB as this may be an
            # overlay
            if (input_data.get_value(InputType.COLLECTION) !=
                    COLLECTION_MARINE and year == OTHER_MAX_YEAR):
                # there is not data for December of the last year
                continue
            file_name = _get_prob_file_name(
                data_type, input_data, scenario, spatial_representation,
                variable, year)
            scenario_file_list.append(os.path.join(file_path, file_name))

        file_list_per_data_type.append(scenario_file_list)

    return file_list_per_data_type


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


def _get_prob_file_path(data_type, input_data, scenario,
                        spatial_representation, variable):

    if (input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE):

        file_path = os.path.join(
            DATA_DIR,
            COLLECTION_MARINE,
            input_data.get_value(InputType.METHOD),
            scenario,
            variable,
            VERSION)
    else:

        file_path = os.path.join(
            DATA_DIR,
            COLLECTION_PROB,
            'uk',
            spatial_representation,
            scenario,
            data_type,
            input_data.get_value(InputType.BASELINE),
            input_data.get_value(InputType.TIME_SLICE_TYPE),
            variable,
            input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
            VERSION)

    return file_path


def _get_prob_file_name(data_type, input_data, scenario,
                        spatial_representation, variable, year):

    if input_data.get_value(InputType.TIME_SLICE_TYPE) == '1y':
        # the year starts in December, so subtract 1 from the year
        start_date = '{year}{mon_day}'.format(
            year=year - 1, mon_day=START_MONTH_DAY)
        end_date = '{year}{mon_day}'.format(
            year=year, mon_day=END_MONTH_DAY)
    else:  # 20y or 30y
        start_date = '20091201'
        end_date = '20991130'

    file_name = ('{variable}_{scenario}_{collection}_uk_'
                 '{spatial_representation}_{data_type}_{baseline}_'
                 '{time_slice_type}_{temporal_type}_{start_data}-'
                 '{end_date}.nc'.format(
                     variable=variable,
                     scenario=scenario,
                     collection=COLLECTION_PROB,
                     spatial_representation=spatial_representation,
                     data_type=data_type,
                     baseline=input_data.get_value(
                         InputType.BASELINE),
                     time_slice_type=input_data.get_value(
                         InputType.TIME_SLICE_TYPE),
                     temporal_type=input_data.get_value(
                         InputType.TEMPORAL_AVERAGE_TYPE),
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
    year_minimum,  year_maximum = get_baseline_range(baseline)
    return _get_cm_file_list_for_range(input_data, year_minimum,
                                       year_maximum)


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
                # there will only be one file
                ensemble_file_list.append(os.path.join(file_path, '*'))

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
        input_data.get_value(InputType.COLLECTION),
        'uk',
        spatial_representation,
        scenario,
        ensemble,
        variable,
        input_data.get_value(InputType.TEMPORAL_AVERAGE_TYPE),
        VERSION)

    return file_path
