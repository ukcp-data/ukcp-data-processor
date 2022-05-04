import copy

from ukcp_cv import CV_Type, get_cv


class Vocab:

    VOCAB = {
        "ensemble": {
            # equivalent to UKCP18_ensemble_member
            # UKCP18 values are full values
            "01": "00000",
            "02": "00605",
            "03": "00834",
            "04": "01113",
            "05": "01554",
            "06": "01649",
            "07": "01843",
            "08": "01935",
            "09": "02123",
            "10": "02242",
            "11": "02305",
            "12": "02335",
            "13": "02491",
            "14": "02832",
            "15": "02868",
            "16": "bcc-csm1-1",
            "17": "CCSM4",
            "18": "CESM1-BGC",
            "19": "CanESM2",
            "20": "CMCC-CM",
            "21": "CNRM-CM5",
            "22": "EC-EARTH",
            "23": "ACCESS1-3",
            "24": "HadGEM2-ES",
            "25": "IPSL-CM5A-MR",
            "26": "MPI-ESM-MR",
            "27": "MRI-CGCM3",
            "28": "GFDL-ESM2G",
        },
        "spatial_representation": {
            # equivalent to UKCP18_resolution
            # no grid in UKCP18_resolution
            # labels are plural in UKCP18_resolution
            # admin_region is just region in UKCP18_resolution
            "1km": "1km grid",
            "12km": "12km grid",
            "2km": "2.2km grid",
            "5km": "5km grid",
            "25km": "25km grid",
            "60km": "60km grid",
            "admin_region": "Administrative Region",
            "country": "Country",
            "river_basin": "River Basin",
        },
        "temporal_average_type": {
            # frequency in UKCP18_CVs
            "ann": "Annual",
            "seas": "Seasonal",
            "mon": "Monthly",
            "day": "Daily",
            "3hr": "3-hourly",
            "1hr": "Hourly",
        },
        "data_type": {
            "cdf": "cdf",
            "pdf": "pdf",
            "percentile": "percentile",
            "sample": "sample",
        },
        "ann": {"ann": "annual"},
        "seas": {
            "djf": "December January February",
            "mam": "March April May",
            "jja": "June July August",
            "son": "September October November",
        },
        "mon": {
            "jan": "January",
            "feb": "February",
            "mar": "March",
            "apr": "April",
            "may": "May",
            "jun": "June",
            "jul": "July",
            "aug": "August",
            "sep": "September",
            "oct": "October",
            "nov": "November",
            "dec": "December",
        },
        "day": {"day": "Daily"},
        "3hr": {"3hr": "3-hourly"},
        "1hr": {"1hr": "Hourly"},
        "area_type": {
            "bbox": "Bounding box",
            "point": "Grid Cell",
            "country": "Country",
            "admin_region": "Administrative Region",
            "river_basin": "River Basin",
            "coast_point": "Coastal Location",
            "gauge_point": "Tide Gauge Point",
        },
        "convert_to_percentiles": {True: "True", False: "False"},
        "colour_mode": {"c": "colour", "g": "grey scale"},
        "data_format": {
            "none": "Don't save the data",
            "csv": "CSV",
            "netcdf": "CF-netCDF",
            "shp": "Shapefile",
        },
        "show_boundaries": {
            "none": "None",
            "country": "Country",
            "admin_region": "Administrative Region",
            "river_basin": "River Basin",
        },
        "font_size": {"s": "small", "m": "medium", "l": "large"},
        "image_format": {"jpg": "jpg", "pdf": "pdf", "png": "png"},
        "image_size": {900: "900 x 600", 1200: "1200 x 800", 2400: "2400 x 1600"},
        "legend_position": {
            1: "1",
            2: "2",
            3: "3",
            4: "4",
            6: "6",
            7: "7",
            8: "8",
            9: "9",
            10: "10",
        },
        "method": {
            "msl-proj": "21st century projections",
            "msl-proj-expl": "Extended projections",
            "return-periods": "21st century projections",
            "return-periods-ext": "Extended projections",
        },
        "order_by_mean": {True: "True", False: "False"},
        "overlay_probability_levels": {True: "True", False: "False"},
        "show_labels": {True: "True", False: "False"},
        "sampling_method": {
            "all": "all",
            "id": "id",
            "random": "random",
            "subset": "subset",
        },
        "sampling_subset_count": {"1": "1", "2": "2"},
        "sampling_percentile_1": {
            10: "10",
            15: "15",
            20: "20",
            25: "25",
            30: "30",
            35: "35",
            40: "40",
            45: "45",
            50: "50",
            55: "55",
            60: "60",
            65: "65",
            70: "70",
            75: "75",
            80: "80",
            85: "85",
            90: "90",
        },
        "return_period": {"rp20": "20 years", "rp50": "50 years", "rp100": "100 years"},
    }

    COLLECTION_LABELS = {
        "area_type": "Area",
        "baseline_period": "Baseline",
        "climate_change_type": "Climate Change Type",
        "colour_mode": "Colour Mode",
        "convert_to_percentiles": "Convert To Percentiles",
        "data_format": "Data Format",
        "collection": "Data Source",
        "data_type": "Data Type",
        "ensemble": "Members",
        "font_size": "Font Size",
        "highlighted_ensemble_members": "Highlighted Members",
        "image_format": "Image Format",
        "image_size": "Image Size",
        "legend_position": "Legend Position",
        "method": "Method",
        "overlay_probability_levels": "Overlay Probability Levels",
        "plot_title": "Plot Title",
        "random_sampling_count": "Random Sampling Count",
        "return_period": "Return Period",
        "sampling_id": "Sampling IDs",
        "sampling_method": "Sampling Method",
        "sampling_percentile_1": "Sampling Percentile 1",
        "sampling_percentile_2": "Sampling Percentile 2",
        "sampling_subset_count": "Sampling Subset Count",
        "sampling_temporal_average_1": "Sampling Temporal Average 1",
        "sampling_temporal_average_2": "Sampling Temporal Average 2",
        "sampling_variable_1": "Sampling Variable 1",
        "sampling_variable_2": "Sampling Variable 2",
        "scenario": "Scenario",
        "show_boundaries": "Show Boundaries",
        "show_labels": "Show Labels",
        "spatial_representation": "Spatial Representation",
        "temporal_average_type": "Temporal Average Type",
        "time_period": "Time Period",
        "time_slice_type": "Time Slice Type",
        "variable": "Variable",
        "year": "Year",
        "year_minimum": "Year Minimum",
        "year_maximum": "Year Maximum",
    }

    def __init__(self):
        self.vocab = self.VOCAB
        self.vocab["plot_title"] = None
        self.vocab["year"] = _get_range(1862, 2301)
        self.vocab["year"].update(_get_range(3001, 3051))
        self.vocab["year_minimum"] = _get_range(1862, 2302)
        self.vocab["year_minimum"].update(_get_range(3001, 3052))
        self.vocab["year_maximum"] = _get_range(1862, 2302)
        self.vocab["year_maximum"].update(_get_range(3001, 3052))
        self.vocab["sampling_id"] = _get_range(1, 4001)
        self.vocab["random_sampling_count"] = _get_range(100, 4001)
        self.vocab["highlighted_ensemble_members"] = self.vocab["ensemble"]
        self.vocab["sampling_percentile_2"] = self.vocab["sampling_percentile_1"]
        time_period = {"all": "all"}
        time_period.update(self.vocab["ann"])
        time_period.update(self.vocab["seas"])
        time_period.update(self.vocab["mon"])
        time_period.update(self.vocab["day"])
        time_period.update(self.vocab["3hr"])
        time_period.update(self.vocab["1hr"])
        self.vocab["time_period"] = time_period
        self.vocab["sampling_temporal_average_1"] = self.vocab["time_period"]
        self.vocab["sampling_temporal_average_2"] = self.vocab["time_period"]

        self._load_cv_variables(CV_Type.VARIABLE)
        self.vocab["sampling_variable_1"] = self.vocab["variable"]
        self.vocab["sampling_variable_2"] = self.vocab["variable"]

        self._load_cv(CV_Type.BASELINE_PERIOD)
        self._load_cv(CV_Type.CLIMATE_CHANGE_TYPE)
        self._load_cv(CV_Type.COLLECTION)
        self._load_cv(CV_Type.SCENARIO)
        self._load_cv(CV_Type.TIME_SLICE_TYPE)

        self._load_cv(CV_Type.ADMIN_REGION)
        self.vocab[CV_Type.ADMIN_REGION]["all"] = "All administrative regions"
        self._load_cv(CV_Type.COUNTRY)
        self.vocab[CV_Type.COUNTRY]["all"] = "All countries"
        self._load_cv(CV_Type.RIVER_BASIN)
        self.vocab[CV_Type.RIVER_BASIN]["all"] = "All river basins"

    def _load_cv(self, cv_type):
        """
        Load in UKCP18 vocab.

        @param cv_type (CV_Type): the vocabulary to load in
        """
        terms = get_cv(cv_type)[cv_type]
        self.vocab[cv_type] = {}
        for key in terms.keys():
            self.vocab[cv_type][key] = terms[key]

    def _load_cv_variables(self, cv_type):
        """
        Load in UKCP18 vocab for variables.

        @param cv_type (CV_Type): the vocabulary to load in
        """
        terms = get_cv(cv_type)[cv_type]
        self.vocab[cv_type] = {}
        for key in terms.keys():
            try:
                self.vocab[cv_type][key] = terms[key]["plot_label"]
            except KeyError:
                pass

    def get_collection_terms(self, collection):
        """
        Get a list of terms for the given collection.

        @param collection (str): the name of the collection

        @return a list of str containing the collection terms
        """
        try:
            return list(self.vocab[collection])
        except KeyError:
            return None

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
            return None
        try:
            return label_dict[term]
        except KeyError:
            return None

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
            return None
        for key in label_dict.keys():
            if label_dict[key] == label:
                return key
        return None

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
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]

SEASONS = ["djf", "mam", "jja", "son"]

ENSEMBLE_MEMBER_SET = {
    "land-derived": [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
    ],
    "land-gcm": [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
    ],
    "hadley-15": [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
    ],
    "land-rcm": [
        "01",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "15",
    ],
    "land-rcm-gwl": [
        "01",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "15",
    ],
    "land-cpm": [
        "01",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "15",
    ],
    "16": ["16"],
    "17": ["17"],
    "18": ["18"],
    "19": ["19"],
    "20": ["20"],
    "21": ["21"],
    "22": ["22"],
    "23": ["23"],
    "24": ["24"],
    "25": ["25"],
    "26": ["26"],
    "27": ["27"],
    "28": ["28"],
    "cordex": list(_get_range(100, 177).values()),
}


def get_months():
    """
    Get an ordered list of months.
    The values are the same as those used in the vocab, 'jan', 'feb' etc.

    @return a list of strings representing the months
    """
    return copy.deepcopy(MONTHS)


def get_seasons():
    """
    Get an ordered list of seasons.
    The values are the same as those used in the vocab, 'djf', 'mam' etc.

    @return a list of strings representing the seasons
    """
    return copy.deepcopy(SEASONS)


def get_ensemble_member_set(collection):
    return copy.deepcopy(ENSEMBLE_MEMBER_SET.get(collection))
