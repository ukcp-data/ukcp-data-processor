import json
from os import path

from ukcp_dp.constants import ROOT_DIR


class Vocab(object):

    VOCAB = {'data_source': {
        'land-prob': 'Land probabilistic projections',
        'probabilistic': 'Probabilistic projections',
        'land-gcm': 'Global simulations',
        'land-rcm': 'Regional simulations',
        'hires_uk': 'High-resolution simulations',
        'marine-sim': 'Marine simulations',
        'observations': 'Observations'
    },
        'area_type': {
        'bbox': 'Bounding box',
        'point': ' Point',
        'country': 'Country',
        'admin_region': 'Administrative Region',
        'river_basin': 'River Basin',
        'coast': 'Coast',
        'marine_gauge': 'Marine Gauge'
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
        'river_basin': 'River Basin',
        'coast': 'Coast'
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
        '1961-2100': '1961-2100',
        '2007-2100': '2007-2100'
    },
        'data_type': {
        'percentile': 'percentile',
        'sample': 'sample'
    },
        'ensemble': {
        'r001i1p00000': '00000',
        'r001i1p00090': '00090',
        'r001i1p00605': '00605',
        'r001i1p00834': '00834',
        'r001i1p01113': '01113',
        'r001i1p01554': '01554',
        'r001i1p01649': '01649',
        'r001i1p01843': '01843',
        'r001i1p01935': '01935',
        'r001i1p02089': '02089',
        'r001i1p02123': '02123',
        'r001i1p02242': '02242',
        'r001i1p02305': '02305',
        'r001i1p02335': '02335',
        'r001i1p02491': '02491',
        'r001i1p02753': '02753',
        'r001i1p02832': '02832',
        'r001i1p02868': '02868',
        'r001i1p02884': '02884',
        'r001i1p02914': '02914'
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
        'england_and_wales': 'England and Wales',
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
        'solway': 'Solway',
        'north_highland': 'North Highland',
        'north_west_england': 'North West England',
        'argyll': 'Argyll',
        'thames': 'Thames',
        'north_western_ireland': 'North Western Ireland',
        'severn': 'Severn',
        'dee': 'Dee',
        'west_highland': 'West Highland',
        'south_west_england': 'South West England',
        'neagh_bann': 'Neagh Bann',
        'western_wales': 'Western Wales',
        'north_east_scotland': 'North East Scotland',
        'anglian': 'Anglian'
    },

        'spatial_representation_group': {
        '60km': '60km grid',
        '25km': '25km grid',
        '12km': '12km grid',
        '2km': '2.2km grid',
        'aggregated_areas': 'Spatially Aggregated Areas'
    },
        'variable_group': {
        'temp': 'Temperature',
        'rain': 'Rainfall',
        'press': 'Pressure',
        'hum': 'Humidity',
        'sea': 'Sea level',
        'wind': 'Wind speed',
    },
        'output': {
        'graphs': 'Graphs',
        'maps': 'Maps',
        'data': 'Data only',
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
        5: '5',
        6: '6',
        7: '7',
        8: '8',
        9: '9',
        10: '10'
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
        self.vocab['year_minimum'] = _get_range(1900, 2101)
        self.vocab['year_maximum'] = _get_range(1900, 2101)
        self.vocab['sampling_id'] = _get_range(1, 4001)
        self.vocab['random_sampling_count'] = _get_range(100, 4001)
        self.vocab['highlighted_ensemble_members'] = self.vocab['ensemble']
        self.vocab['sampling_percentile_2'] = self.vocab[
            'sampling_percentile_1']
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
    'land-gcm': ['r001i1p00000', 'r001i1p00090', 'r001i1p00605',
                 'r001i1p00834', 'r001i1p01113', 'r001i1p01554',
                 'r001i1p01649', 'r001i1p01843', 'r001i1p01935',
                 'r001i1p02089', 'r001i1p02123', 'r001i1p02242',
                 'r001i1p02305', 'r001i1p02335', 'r001i1p02491',
                 'r001i1p02753', 'r001i1p02832', 'r001i1p02868',
                 'r001i1p02884', 'r001i1p02914'],
    'land-rcm': ['r001i1p00000', 'r001i1p00090', 'r001i1p01113',
                 'r001i1p01554', 'r001i1p01649', 'r001i1p01843',
                 'r001i1p01935', 'r001i1p02123', 'r001i1p02242',
                 'r001i1p02305', 'r001i1p02335', 'r001i1p02491',
                 'r001i1p02753', 'r001i1p02868', 'r001i1p02914'],
    'cpm': ['r001i1p00000', 'r001i1p00090', 'r001i1p01554', 'r001i1p01935',
            'r001i1p02123', 'r001i1p02242', 'r001i1p02305', 'r001i1p02335',
            'r001i1p02491', 'r001i1p02914']
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
