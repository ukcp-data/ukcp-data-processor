def _get_range(min_value, max_value):
    values = {}
    for i in range(min_value, max_value):
        values[i] = str(i)
    return values


VOCAB = {'data_source': {
            'land_probabilistic': 'Land probabilistic projections',
            'probabilistic': 'Probabilistic projections',
            'global_realisations': 'Global simulations',
            'regional_realisations': 'Regional simulations',
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
             '1961-1990': '1961-1990',
             '1981-2000': '1981-2000',
             '1981-2010': '1981-2010',
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
            'tasmin': 'Minimum surface air temperature',
            'tas': 'Surface air temperature',
            'pr': 'Precipitation'
            },
         'temporal_average_type': {
            'annual': 'Annual',
            'seasonal': 'Seasonal',
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
         'seasonal': {
            'djf': 'December January February',
            'mam': 'March April May',
            'jja': 'June July August',
            'son': 'September October November'
            },
         'annual': {
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
         'ensemble_member_set': {
            'global_realisations': ['r1i1p1', 'r1i1p2', 'r1i1p3', 'r1i1p4',
                                    'r1i1p5', 'r1i1p6', 'r1i1p7', 'r1i1p8',
                                    'r1i1p9', 'r1i1p10', 'r1i1p11', 'r1i1p12',
                                    'r1i1p13', 'r1i1p14', 'r1i1p15', 'r1i1p16',
                                    'r1i1p17', 'r1i1p18', 'r1i1p19',
                                    'r1i1p20'],
            'regional_realisations': ['r1i1p1', 'r1i1p2', 'r1i1p3', 'r1i1p4',
                                      'r1i1p5', 'r1i1p6', 'r1i1p7', 'r1i1p8',
                                      'r1i1p9', 'r1i1p10', 'r1i1p11',
                                      'r1i1p12', 'r1i1p13', 'r1i1p14',
                                      'r1i1p15'],
            'cpm': []  # TODO
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
         'show_boundaries': {
             True: 'True',
             False: 'False'
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
            600: '600 x 400',
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
         'show_probability_levels': {
            True: 'True',
            False: 'False'
            },
         }


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


def validate_collection_label(collection, label):
    """
    Validate the label of a given collection term.

    @param collection (str): the name of the collection
    @param label (str): the label to validate

    @return True if label is valid
    """
    try:
        label_dict = VOCAB[collection]
    except KeyError:
        return False
    if label in label_dict.values():
        return True
    return False
