from ukcp_dp.constants import DATA_SOURCE_PROB, DATA_SOURCE_PROB_MIN_YEAR, \
    DATA_SOURCE_RCM, DATA_SOURCE_RCM_MIN_YEAR, InputType, MONTHLY, SEASONAL
from ukcp_dp.vocab_manager import get_collection_terms, \
    get_collection_term_label, get_ensemble_member_set

import logging
log = logging.getLogger(__name__)


class Validator():
    def validate(self, input_data):
        log.debug('validate')
        self.input_data = input_data
        self._validate_spatial_rep()
        self._validate_convert_to_percentiles()
        self._validate_overlay_probability_levels()
        self._validate_time_slice()
        self._validate_boundary_overlay()
        self._validate_colour_mode()
        self._validate_highlighted_ensemble_members()
        self._validate_time_period()
        self._validate_baseline()

        return self.input_data

    def _validate_data_source(self):
        # this must always be set
        try:
            self.input_data.get_value(InputType.DATA_SOURCE)
        except KeyError:
            raise Exception('{} not set'.format(InputType.DATA_SOURCE))

    def _validate_spatial_rep(self):
        try:
            spatial_rep = self.input_data.get_value(
                InputType.SPATIAL_REPRESENTATION)
            # TODO
#                 raise Exception("Invalid {value_type}: {value}.".format(
# value_type=InputType.SPATIAL_REPRESENTATION, value=spatial_rep))
        except KeyError:
            # Not set, lets be kind and set it
            if self.input_data.get_area_type() in ['bbox', 'point']:
                if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                        'land-gcm'):
                    self.input_data.set_value(
                        InputType.SPATIAL_REPRESENTATION, '60km')
                elif (self.input_data.get_value(InputType.DATA_SOURCE) ==
                        'land-rcm'):
                    self.input_data.set_value(
                        InputType.SPATIAL_REPRESENTATION, '12km')
                elif (self.input_data.get_value(InputType.DATA_SOURCE) ==
                        DATA_SOURCE_PROB):
                    self.input_data.set_value(
                        InputType.SPATIAL_REPRESENTATION, '25km')
            else:
                self.input_data.set_value(
                    InputType.SPATIAL_REPRESENTATION,
                    self.input_data.get_area_type())

    def _validate_colour_mode(self):
        try:
            self.input_data.get_value(InputType.COLOUR_MODE)
        except KeyError():
            # Not set, lets be kind and set it to 'c'
            self.input_data.set_value(InputType.COLOUR_MODE, 'c')

    def _validate_convert_to_percentiles(self):
        try:
            convert_to_percentiles = self.input_data.get_value(
                InputType.CONVERT_TO_PERCENTILES)
            if not isinstance(convert_to_percentiles, bool):
                raise Exception("Invalid {value_type}: {value}.".format(
                    value_type=InputType.CONVERT_TO_PERCENTILES,
                    value=convert_to_percentiles))

        except KeyError:
            # Not set, lets be kind and set it to False
            self.input_data.set_value(InputType.CONVERT_TO_PERCENTILES, False)

    def _validate_overlay_probability_levels(self):
        try:
            overlay_probability_levels = self.input_data.get_value(
                InputType.OVERLAY_PROBABILITY_LEVELS)
            if not isinstance(overlay_probability_levels, bool):
                raise Exception("Invalid {value_type}: {value}.".format(
                    value_type=InputType.OVERLAY_PROBABILITY_LEVELS,
                    value=overlay_probability_levels))

        except KeyError:
            # Not set, lets be kind and set it to False
            self.input_data.set_value(
                InputType.OVERLAY_PROBABILITY_LEVELS, False)

    def _validate_time_slice(self):
        try:
            year = self.input_data.get_value(InputType.YEAR)
        except KeyError:
            year = None

        try:
            year_min = self.input_data.get_value(InputType.YEAR_MINIMUM)
        except KeyError:
            year_min = None

        try:
            year_max = self.input_data.get_value(InputType.YEAR_MAXIMUM)
        except KeyError:
            year_max = None

        if (year_max is not None and year_min is None):
            # if max is set then min must be set
            raise Exception("{min} must be provided when {max} is set".format(
                min=InputType.YEAR_MINIMUM, max=InputType.YEAR_MAXIMUM))

        if (year_min is not None and year_max is None):
            # if min is set then max must be set
            raise Exception("{max} must be provided when {min} is set".format(
                min=InputType.YEAR_MINIMUM, max=InputType.YEAR_MAXIMUM))

        if (year is not None and year_max is not None):
            # year and max should not be set at the same time
            raise Exception("{year} cannot be set at the same time as {min} "
                            "and {max}".format(year=InputType.YEAR,
                                               min=InputType.YEAR_MINIMUM,
                                               max=InputType.YEAR_MAXIMUM))

        if (year_max is not None and year_min is not None):
            # a minimum of 20 years must be selected
            # we include the year_min but not the year_max
            if year_max - year_min < 20:
                raise Exception("A minimum of 20 years must be selected")

        if (year is not None):
            # if year is set then set min and max to equal year
            self.input_data.set_value(InputType.YEAR_MINIMUM, year)
            self.input_data.set_value(InputType.YEAR_MAXIMUM, year)

        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_PROB):
            min_allowed_year = DATA_SOURCE_PROB_MIN_YEAR
        elif (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_RCM):
            min_allowed_year = DATA_SOURCE_RCM_MIN_YEAR
        else:
            min_allowed_year = min(get_collection_terms('year_minimum'))

        if (self.input_data.get_value(InputType.YEAR_MINIMUM) <
                min_allowed_year):
            raise Exception(
                "The minimum year must be equal or greater than {}".
                format(min_allowed_year))

        max_allowed_year = max(get_collection_terms('year_maximum'))
        if (self.input_data.get_value(InputType.YEAR_MAXIMUM) >
                max_allowed_year):
            raise Exception(
                "The maximum year must be equal or less than {}".
                format(max_allowed_year))

    def _validate_boundary_overlay(self):
        try:
            self.input_data.get_value(InputType.SHOW_BOUNDARIES)
        except KeyError:
            self.input_data.set_value(InputType.SHOW_BOUNDARIES, 'none')

    def _validate_highlighted_ensemble_members(self):
        # if no value is set, then set as an empty list
        try:
            self.input_data.get_value(InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS)
        except KeyError:
            self.input_data._set_values(InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS,
                                        [])

        allowed_ensembles = get_ensemble_member_set(
            self.input_data.get_value(InputType.DATA_SOURCE))
        if allowed_ensembles is None:
            return

        for ensemble in self.input_data.get_value(
                InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS):

            if ensemble not in allowed_ensembles:
                raise Exception("Invalid {value_type}: {value}.".format(
                    value_type=InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS,
                    value=ensemble))

    def _validate_time_period(self):
        # if a temporal average type is set then check the time period is valid
        # for that type
        try:
            temporal_average_type = self.input_data.get_value(
                InputType.TEMPORAL_AVERAGE_TYPE)
        except KeyError:
            return

        time_period = self.input_data.get_value(InputType.TIME_PERIOD)
        allowed_time_periods = get_collection_terms(temporal_average_type)

        # special case for all
        if ((temporal_average_type == MONTHLY or
                temporal_average_type == SEASONAL)
                and time_period == 'all'):
            return

        if time_period not in allowed_time_periods:
            type_label = get_collection_term_label(
                InputType.TEMPORAL_AVERAGE_TYPE, temporal_average_type)
            raise Exception("{time_period} is not a {type_label} value".format(
                time_period=time_period, type_label=type_label))

    def _validate_baseline(self):
        # only a subset of values are allowed for RCM
        if (self.input_data.get_value(InputType.DATA_SOURCE) ==
                DATA_SOURCE_RCM):
            try:
                baseline = self.input_data.get_value(InputType.BASELINE)
            except KeyError:
                return
            allowed_baselines = get_collection_terms(InputType.BASELINE)
            # the first one is not allowed for RCM
            allowed_baselines.pop(0)

            if (baseline not in allowed_baselines):
                raise Exception("Invalid {value_type}: {value}.".format(
                    value_type=InputType.BASELINE,
                    value=baseline))
