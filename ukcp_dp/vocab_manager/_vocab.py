def _get_range(min_value, max_value):
    values = {}
    for i in range(min_value, max_value):
        values[i] = str(i)
    return values


COLLECTION_LABELS = {
    'area_type': 'Area',
    'baseline': 'Baseline',
    'data_format': 'Data Format',
    'ensemble': 'Ensemble',
    'data_source': 'Data Source',
    'data_type': 'Data Type',
    'font_size': 'Font Size',
    'image_format': 'Image Format',
    'image_size': 'Image Size',
    'legend_position': 'Legend Position',
    'overlay_probability_levels': 'Overlay Probability Levels',
    'scenario': 'Scenario',
    'show_boundaries': 'Show Boundaries',
    'spatial_representation': 'Spatial Representation',
    'temporal_average_type': 'Temporal Average Type',
    'time_period': 'Time Period',
    'variable': 'Variable',
    'year': 'Year',
    'year_minimum': 'Year Minimum',
    'year_maximum': 'Year Maximum'
    }

VOCAB = {'data_source': {
            'land-prob': 'Land probabilistic projections',
            'probabilistic': 'Probabilistic projections',
            'land-gcm': 'Global simulations',
            'land-rcm': 'Regional simulations',
            'hires_uk': 'High-resolution simulations',
            'marine': 'Marine projections',
            'observations': 'Observations'
            },
         'area_type': {
            'bbox': 'Bounding box',
            'point': ' Point',
            'country': 'Country',
            'admin_region': 'Administrative Region',
            'river_basin': 'River Basin'
            },
         'baseline': {
             '1961-1990': '1961 - 1990',
             '1981-2000': '1981 - 2000',
             '1981-2010': '1981 - 2010',
             },
         'climate_change_type': {
            'anomalies': 'Anomalies',
            'absolute': 'Absolute values'
            },
         'scenario': {
            'a1b': 'SRES A1B',
            'rcp26': 'RCP 2.6',
            'rcp45': 'RCP 4.5',
            'rcp60': 'RCP 6.0',
            'rcp85': 'RCP 8.5'
            },
         'variable': {
            'tasmax': 'Maximum surface air temperature',
            'tasmaxAnom': 'Maximum surface air temperature anomaly',
            'tasmin': 'Minimum surface air temperature',
            'tasminAnom': 'Minimum surface air temperature anomaly',
            'tas': 'Surface air temperature',
            'tasAnom': 'Surface air temperature anomaly',
            'pr': 'Precipitation',
            'prAnom': 'Precipitation anomaly'
            },
         'temporal_average_type': {
            'ann': 'Annual',
            'seas': 'Seasonal',
            'mon': 'Monthly'
            },
         'spatial_representation': {
            '60km': '60km grid',
            '25km': '25km grid',
            '12km': '12km grid',
            '2km': '2.2km grid',
            'country': 'Country',
            'admin_region': 'Administrative Region',
            'river_basin': 'River Basin'
            },
         'mon': {
            'jan': 'January',
            'feb': 'February',
            'mar': 'March',
            'apr': 'April',
            'may': 'May',
            'jun': 'June',
            'jul': 'July',
            'aug': 'August',
            'sep': 'September',
            'oct': 'October',
            'nov': 'November',
            'dec': 'December'
            },
         'seas': {
            'djf': 'December January February',
            'mam': 'March April May',
            'jja': 'June July August',
            'son': 'September October November'
            },
         'ann': {
            'ann': 'annual'
            },
         'time_period': {
            'jan': 'January',
            'feb': 'February',
            'mar': 'March',
            'apr': 'April',
            'may': 'May',
            'jun': 'June',
            'jul': 'July',
            'aug': 'August',
            'sep': 'September',
            'oct': 'October',
            'nov': 'November',
            'dec': 'December',
            'djf': 'December January February',
            'mam': 'March April May',
            'jja': 'June July August',
            'son': 'September October November',
            'ann': 'annual',
            'all': 'all'
            },
         'period': {
            '1900-2100': '1900-2100',
            '1961-2100': '1961-2100'
            },
         'data_format': {
            'none': "Don't save the data",
            'csv': 'CSV',
            'netcdf': 'CF-netCDF'
            },
         'data_type': {
             'percentile': 'percentile',
             'sample': 'sample'
            },
         'ensemble': {
            'r1i1p1': 'r1i1p1',
            'r1i1p2': 'r1i1p2',
            'r1i1p3': 'r1i1p3',
            'r1i1p4': 'r1i1p4',
            'r1i1p5': 'r1i1p5',
            'r1i1p6': 'r1i1p6',
            'r1i1p7': 'r1i1p7',
            'r1i1p8': 'r1i1p8',
            'r1i1p9': 'r1i1p9',
            'r1i1p10': 'r1i1p10',
            'r1i1p11': 'r1i1p11',
            'r1i1p12': 'r1i1p12',
            'r1i1p13': 'r1i1p13',
            'r1i1p14': 'r1i1p14',
            'r1i1p15': 'r1i1p15',
            'r1i1p16': 'r1i1p16',
            'r1i1p17': 'r1i1p17',
            'r1i1p18': 'r1i1p18',
            'r1i1p19': 'r1i1p19',
            'r1i1p20': 'r1i1p20'
            },
         'admin_region': {
            'all': 'All administrative regions',
            'north_east_england': 'North East England',
            'north_west_england': 'North West England',
            'yorkshire_and_Humber': 'Yorkshire and Humber',
            'east_midlands': 'East Midlands',
            'west_midlands': 'West Midlands',
            'east_of_england': 'East of England',
            'london': 'London',
            'south_east_england': 'South East England',
            'south_west_england': 'South West England',
            'wales': 'Wales',
            'east_scotland': 'East Scotland',
            'west_scotland': 'West Scotland',
            'north_scotland': 'North Scotland',
            'northern_ireland': 'Northern Ireland',
            'channel_islands': 'Channel Islands',
            'isle_of_man': 'Isle of Man'
            },
         'country': {
            'all': 'All countries',
            'channel_islands': 'Channel Islands',
            'england': 'England',
            'ireland': 'Republic of  Ireland',
            'isle_of_man': 'Isle of Man',
            'northern_ireland': 'Northern Ireland',
            'scotland': 'Scotland',
            'uk': 'United Kingdom',
            'wales': 'Wales',
            },
         'river_basin': {
            'all': 'All river basins',
            'tay': 'Tay',
            'orkney_and_shetlands': 'Orkney and Shetlands',
            'clyde': 'Clyde',
            'south_east_england': 'South East England',
            'north_eastern_ireland': 'North Eastern Ireland',
            'northumbria': 'Northumbria',
            'tweed': 'Tweed',
            'forth': 'Forth',
            'humber': 'Humber',
            'channel_islands': 'Channel Islands',
            'republic_of_ireland': 'Republic of Ireland',
            'solway': 'Solway',
            'north_highland': 'North Highland',
            'north_west_england': 'North West England',
            'argyll': 'Argyll',
            'thames': 'Thames',
            'north_western_ireland': 'North Western Ireland',
            'severn': 'Severn',
            'dee': 'Dee',
            'west_highland': 'West Highland',
            'isle_of_man': 'Isle of Man',
            'south_west_england': 'South West England',
            'neagh_bann': 'Neagh Bann',
            'west_wales': 'West Wales',
            'north_east_scotland': 'North East Scotland',
            'anglian': 'Anglian'
            },
         'convert_to_percentiles': {
            True: 'True',
            False: 'False'
            },
         'colour_mode': {
            'c': 'colour',
            'g': 'grey scale'
            },
         'show_boundaries': {
            'none': 'None',
            'country': 'Country',
            'admin_region': 'Administrative Region',
            'river_basin': 'River Basin'
             },
         'font_size': {
            's': 'small',
            'm': 'medium',
            'l': 'large'
            },
         'image_format': {
            'jpg': 'jpg',
            'pdf': 'pdf',
            'png': 'png'
            },
         'image_size': {
            900: '900 x 600',
            1200: '1200 x 800'
            },
         'legend_position': {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10'
            },
         'year': _get_range(1900, 2101),
         'year_minimum': _get_range(1900, 2101),
         'year_maximum': _get_range(1900, 2101),
         'overlay_probability_levels': {
            True: 'True',
            False: 'False'
            },
         }

VOCAB['highlighted_ensemble_members'] = VOCAB['ensemble']

# an ordered list of months
MONTHS = [
    'jan',
    'feb',
    'mar',
    'apr',
    'may',
    'jun',
    'jul',
    'aug',
    'sep',
    'oct',
    'nov',
    'dec'
]

ENSEMBLE_MEMBER_SET = {
    'land-gcm': ['r1i1p1', 'r1i1p2', 'r1i1p3', 'r1i1p4', 'r1i1p5', 'r1i1p6',
                 'r1i1p7', 'r1i1p8', 'r1i1p9', 'r1i1p10', 'r1i1p11', 'r1i1p12',
                 'r1i1p13', 'r1i1p14', 'r1i1p15', 'r1i1p16', 'r1i1p17',
                 'r1i1p18', 'r1i1p19', 'r1i1p20'],
    'land-rcm': ['r1i1p1', 'r1i1p2', 'r1i1p3', 'r1i1p4', 'r1i1p5', 'r1i1p6',
                 'r1i1p7', 'r1i1p8', 'r1i1p9', 'r1i1p10', 'r1i1p11', 'r1i1p12',
                 'r1i1p13', 'r1i1p14', 'r1i1p15'],
    'cpm': []  # TODO
}

# Labels for use on plot axes
VAR_LABELS = {
    'tas': 'Temperature, $^\circ$C',
    'tasAnom': 'Temperature anomaly, $^\circ$C',
    'pr': 'Precipitation rate, mm/day',
    'prAnom': 'Precipitation rate anomaly, %'}


def get_collection_label(collection):
    """
    Get the label for a collection

    @param collection (str): the name of the collection

    @return a str containing the collection label
    """
    try:
        return COLLECTION_LABELS[collection]
    except KeyError:
        return


def get_collection_terms(collection):
    """
    Get a list of terms for the given collection.

    @param collection (str): the name of the collection

    @return a list of str containing the collection terms
    """
    try:
        return VOCAB[collection].keys()
    except KeyError:
        return


def get_collection_term_label(collection, term):
    """
    Get the label of a given collection term.

    @param collection (str): the name of the collection
    @param term (str): the term from the collection

    @return a str containing the label of the collection term
    """
    try:
        label_dict = VOCAB[collection]
    except KeyError:
        return
    try:
        return label_dict[term]
    except KeyError:
        return


def get_collection_term_value(collection, label):
    """
    Get the value associated with a given collection term label.

    @param collection (str): the name of the collection
    @param label (str): the label off a term from the collection

    @return a str containing the value associated with the collection term
        label
    """
    try:
        label_dict = VOCAB[collection]
    except KeyError:
        return
    for key in label_dict.keys():
        if label_dict[key] == label:
            return key
    return


def get_months():
    """
    Get an ordered list of months.
    The values are the same as those used in the vocab, 'jan', 'feb' etc.

    @return a list of strings representing the months
    """
    return MONTHS


def get_ensemble_member_set(data_source):
    try:
        return ENSEMBLE_MEMBER_SET[data_source]
    except KeyError:
        return


def get_var_label(var_id):
    """
    Get a label that could be used on a plot, for the given var_id

    @param var_id (str): the variable id

    @return a str containing a label for the variable
    """
    try:
        return VAR_LABELS[var_id]
    except KeyError:
        return var_id
