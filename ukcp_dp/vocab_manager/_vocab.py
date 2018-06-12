import json
from os import path

from ukcp_dp.constants import ROOT_DIR


class Vocab(object):

    VOCAB = {'admin_region': {
        # includes 'all', not in UKCP18_admin_region
        'all': 'All administrative regions',
        'channel_islands': 'Channel Islands',
        'east_midlands': 'East Midlands',
        'east_of_england': 'East of England',
        'east_scotland': 'East Scotland',
        'isle_of_man': 'Isle of Man',
        'london': 'London',
        'north_east_england': 'North East England',
        'north_scotland': 'North Scotland',
        'north_west_england': 'North West England',
        'northern_ireland': 'Northern Ireland',
        'south_east_england': 'South East England',
        'south_west_england': 'South West England',
        'wales': 'Wales',
        'west_midlands': 'West Midlands',
        'west_scotland': 'West Scotland',
        'yorkshire_and_Humber': 'Yorkshire and Humber'
    },
        'country': {
        # includes 'all', not in UKCP18_country
        'all': 'All countries',
        'channel_islands': 'Channel Islands',
        'england': 'England',
        'england_and_wales': 'England and Wales',
        'isle_of_man': 'Isle of Man',
        'northern_ireland': 'Northern Ireland',
        'scotland': 'Scotland',
        'uk': 'United Kingdom',
        'wales': 'Wales'
    },
        'data_source': {
        # equivalent to UKCP18_collection
        'land-gcm': 'Global simulations',
        'land-prob': 'Land probabilistic projections',
        'land-rcm': 'Regional simulations',
        'marine-sim': 'Marine simulations'
    },

        'ensemble': {
        # equivalent to UKCP18_ensemble_member
        # UKCP18 values are full values
        '01': '00000',
        '02': '00605',
        '03': '00834',
        '04': '01113',
        '05': '01554',
        '06': '01649',
        '07': '01843',
        '08': '01935',
        '09': '02123',
        '10': '02242',
        '11': '02305',
        '12': '02335',
        '13': '02491',
        '14': '02832',
        '15': '02868',
        '16': 'bcc-csm1-1',
        '17': 'CCSM4',
        '18': 'CESM1-BGC',
        '19': 'CanESM2',
        '20': 'CMCC-CM',
        '21': 'CNRM-CM5',
        '22': 'EC-EARTH',
        '23': 'ACCESS1-3',
        '24': 'HadGEM2-ES',
        '25': 'IPSL-CM5A-MR',
        '26': 'MPI-ESM-MR',
        '27': 'MRI-CGCM3',
        '28': 'GFDL-ESM2G'
    },
        'spatial_representation': {
        # equivalent to UKCP18_resolution
        # no grid in UKCP18_resolution
        # labels are plural in UKCP18_resolution
        # admin_region is just region in UKCP18_resolution
        '12km': '12km grid',
        '2km': '2.2km grid',
        '25km': '25km grid',
        '60km': '60km grid',
        'admin_region': 'Administrative Region',
        'country': 'Country',
        'river_basin': 'River Basin'
    },
        'river_basin': {
        # includes 'all', not in UKCP18_country
        'all': 'All river basins',
        'anglian': 'Anglian',
        'argyll': 'Argyll',
        'clyde': 'Clyde',
        'dee': 'Dee',
        'forth': 'Forth',
        'humber': 'Humber',
        'neagh_bann': 'Neagh Bann',
        'north_east_scotland': 'North East Scotland',
        'north_eastern_ireland': 'North Eastern Ireland',
        'north_highland': 'North Highland',
        'north_west_england': 'North West England',
        'north_western_ireland': 'North Western Ireland',
        'northumbria': 'Northumbria',
        'orkney_and_shetlands': 'Orkney and Shetlands',
        'severn': 'Severn',
        'solway': 'Solway',
        'south_east_england': 'South East England',
        'south_west_england': 'South West England',
        'tay': 'Tay',
        'thames': 'Thames',
        'tweed': 'Tweed',
        'west_highland': 'West Highland',
        'western_wales': 'Western Wales'
    },
        'scenario': {
        'sres-a1b': 'SRES A1B',
        'rcp26': 'RCP 2.6',
        'rcp45': 'RCP 4.5',
        'rcp60': 'RCP 6.0',
        'rcp85': 'RCP 8.5'
    },
        'temporal_average_type': {
        # frequency in UKCP18_CVs
        'ann': 'Annual',
        'seas': 'Seasonal',
        'mon': 'Monthly'
    },

        # the following are not currently in UKCP18
        'baseline': {
        '1961-1990': '1961 - 1990',
        '1981-2000': '1981 - 2000',
        '1981-2010': '1981 - 2010',
    },
        'climate_change_type': {
        'anomalies': 'Anomalies',
        'absolute': 'Absolute values'
    },
        'data_type': {
        'cdf': 'cdf',
        'pdf': 'pdf',
        'percentile': 'percentile',
        'sample': 'sample'
    },
        'ann': {
        'ann': 'annual'
    },
        'seas': {
        'djf': 'December January February',
        'mam': 'March April May',
        'jja': 'June July August',
        'son': 'September October November'
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
        'area_type': {
        'bbox': 'Bounding box',
        'point': ' Point',
        'country': 'Country',
        'admin_region': 'Administrative Region',
        'river_basin': 'River Basin',
        'coast_point': 'Coastal Location',
        'gauge_point': 'Tide Gauge Point'
    },
        'convert_to_percentiles': {
        True: 'True',
        False: 'False'
    },
        'colour_mode': {
        'c': 'colour',
        'g': 'grey scale'
    },
        'data_format': {
        'none': "Don't save the data",
        'csv': 'CSV',
        'netcdf': 'CF-netCDF'
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
        1200: '1200 x 800',
        2400: '2400 x 1600'
    },
        'legend_position': {
        1: '1',
        2: '2',
        3: '3',
        4: '4',
        6: '6',
        7: '7',
        8: '8',
        9: '9',
        10: '10'
    },
        'method': {
        'exploratory': 'exploratory'
    },
        'order_by_mean': {
        True: 'True',
        False: 'False'
    },
        'overlay_probability_levels': {
        True: 'True',
        False: 'False'
    },
        'sampling_method': {
        'all': 'all',
        'id': 'id',
        'random': 'random',
        'subset': 'subset',
    },
        'sampling_subset_count': {
        '1': '1',
        '2': '2'
    },
        'sampling_percentile_1': {
        10: '10',
        15: '15',
        20: '20',
        25: '25',
        30: '30',
        35: '35',
        40: '40',
        45: '45',
        50: '50',
        55: '55',
        60: '60',
        65: '65',
        70: '70',
        75: '75',
        80: '80',
        85: '85',
        90: '90',
    },

        # vocabs just for facets
        'period': {
        '1900-2100': '1900-2100',
        '1961-2100': '1961-2100',
        '1980-2080': '1980-2080',
        '2007-2100': '2007-2100',
        '2007-2300': '2007-2300'
    },
        'output': {
        'graphs': 'Graphs',
        'maps': 'Maps',
        'data': 'Data only',
    },
        'spatial_representation_group': {
        '60km': '60km grid',
        '25km': '25km grid',
        '12km': '12km grid',
        '2km': '2.2km grid',
        'aggregated_areas': 'Spatially Aggregated Areas',
        'coastal': 'Coastal'
    },
        'variable_group': {
        'temp': 'Temperature',
        'rain': 'Rainfall',
        'press': 'Pressure',
        'hum': 'Humidity',
        'sea': 'Sea level',
        'wind': 'Wind speed'
    },
    }

    COLLECTION_LABELS = {
        'area_type': 'Area',
        'baseline': 'Baseline',
        'climate_change_type': 'Climate Change Type',
        'colour_mode': 'Colour Mode',
        'convert_to_percentiles': 'Convert To Percentiles',
        'data_format': 'Data Format',
        'data_source': 'Data Source',
        'data_type': 'Data Type',
        'ensemble': 'Ensemble Members',
        'font_size': 'Font Size',
        'highlighted_ensemble_members': 'Highlighted Ensemble Members',
        'image_format': 'Image Format',
        'image_size': 'Image Size',
        'legend_position': 'Legend Position',
        'method': 'Method',
        'output': 'Output',
        'overlay_probability_levels': 'Overlay Probability Levels',
        'period': 'Date Range',
        'random_sampling_count': 'Random Sampling Count',
        'sampling_id': 'Sampling IDs',
        'sampling_method': 'Sampling Method',
        'sampling_percentile_1': 'Sampling Percentile 1',
        'sampling_percentile_2': 'Sampling Percentile 2',
        'sampling_subset_count': 'Sampling Subset Count',
        'sampling_temporal_average_1': 'Sampling Temporal Average 1',
        'sampling_temporal_average_2': 'Sampling Temporal Average 2',
        'sampling_variable_1': 'Sampling Variable 1',
        'sampling_variable_2': 'Sampling Variable 2',
        'scenario': 'Scenario',
        'show_boundaries': 'Show Boundaries',
        'spatial_representation': 'Spatial Representation',
        'spatial_representation_group': 'Spatial Representation',
        'temporal_average_type': 'Temporal Average Type',
        'time_period': 'Time Period',
        'variable': 'Variable',
        'variable_group': 'Variable',
        'year': 'Year',
        'year_minimum': 'Year Minimum',
        'year_maximum': 'Year Maximum'
    }

    def __init__(self):
        self.vocab = self.VOCAB
        self.vocab['year'] = _get_range(1900, 2101)
        self.vocab['year_minimum'] = _get_range(1900, 2301)
        self.vocab['year_maximum'] = _get_range(1900, 2301)
        self.vocab['sampling_id'] = _get_range(1, 4001)
        self.vocab['random_sampling_count'] = _get_range(100, 4001)
        self.vocab['highlighted_ensemble_members'] = self.vocab['ensemble']
        self.vocab['sampling_percentile_2'] = self.vocab[
            'sampling_percentile_1']
        time_period = {'all': 'all'}
        time_period.update(self.vocab['ann'])
        time_period.update(self.vocab['seas'])
        time_period.update(self.vocab['mon'])
        self.vocab['time_period'] = time_period
        self.vocab['sampling_temporal_average_1'] = self.vocab['time_period']
        self.vocab['sampling_temporal_average_2'] = self.vocab['time_period']

        self.variables = self._load_json_variables()
        self.vocab['sampling_variable_1'] = self.vocab['variable']
        self.vocab['sampling_variable_2'] = self.vocab['variable']

    def _load_json_variables(self):
        # TODO quick hack to get UKCP18_CVs
        var_file = path.join(
            ROOT_DIR, 'ukcp_dp/vocab_manager/UKCP18_variable.json')
        with open(var_file) as json_data:
            variables = json.load(json_data)['variable']
        self.vocab['variable'] = {}
        for key in variables.keys():
            try:
                self.vocab['variable'][key] = variables[key]['plot_label']
            except KeyError:
                pass

    def get_collection_terms(self, collection):
        """
        Get a list of terms for the given collection.

        @param collection (str): the name of the collection

        @return a list of str containing the collection terms
        """
        try:
            return self.vocab[collection].keys()
        except KeyError:
            return

    def get_collection_term_label(self, collection, term):
        """
        Get the label of a given collection term.

        @param collection (str): the name of the collection
        @param term (str): the term from the collection

        @return a str containing the label of the collection term
        """
        try:
            label_dict = self.vocab[collection]
        except KeyError:
            return
        try:
            return label_dict[term]
        except KeyError:
            return

    def get_collection_term_value(self, collection, label):
        """
        Get the value associated with a given collection term label.

        @param collection (str): the name of the collection
        @param label (str): the label off a term from the collection

        @return a str containing the value associated with the collection term
            label
        """
        try:
            label_dict = self.vocab[collection]
        except KeyError:
            return
        for key in label_dict.keys():
            if label_dict[key] == label:
                return key
        return

    def get_collection_label(self, collection):
        """
        Get the label for a collection

        @param collection (str): the name of the collection

        @return a str containing the collection label
        """
        try:
            return self.COLLECTION_LABELS[collection]
        except KeyError:
            return collection


def _get_range(min_value, max_value):
    values = {}
    for i in range(min_value, max_value):
        values[i] = str(i)
    return values


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
    'land-gcm': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                 '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                 '21', '22', '23', '24', '25', '26', '27', '28'],
    'land-rcm': ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12',
                 '13', '15'],
    'cpm': ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13',
            '15']
}


def get_months():
    """
    Get an ordered list of months.
    The values are the same as those used in the vocab, 'jan', 'feb' etc.

    @return a list of strings representing the months
    """
    return MONTHS


def get_ensemble_member_set(data_source):
    return ENSEMBLE_MEMBER_SET.get(data_source)
