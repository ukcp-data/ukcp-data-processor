import logging

from ukcp_dp.constants import (
    COLLECTION_DERIVED,
    COLLECTION_DERIVED_GWL_MAX_YEAR,
    COLLECTION_DERIVED_GWL_MIN_YEAR,
    COLLECTION_PROB,
    COLLECTION_PROB_MIN_YEAR,
    COLLECTION_MARINE,
    COLLECTION_MARINE_MIN_YEAR,
    COLLECTION_MARINE_MAX_YEAR,
    COLLECTION_CPM,
    COLLECTION_GCM,
    COLLECTION_OBS,
    COLLECTION_OBS_MIN_YEAR,
    COLLECTION_RCM,
    COLLECTION_RCM_MIN_YEAR,
    COLLECTION_RCM_GWL,
    EXTENDED_PROJECTIONS,
    GWL,
    InputType,
    OTHER_MAX_YEAR,
    AreaType,
    TemporalAverageType,
)
from ukcp_dp.vocab_manager import get_ensemble_member_set


LOG = logging.getLogger(__name__)


class Validator:
    def __init__(self, vocab):
        self.vocab = vocab
        self.input_data = None

    def validate(self, input_data):
        LOG.debug("validate")
        self.input_data = input_data
        self._validate_spatial_rep()
        self._validate_convert_to_percentiles()
        self._validate_overlay_probability_levels()
        self._validate_time_slice()
        self._validate_colour_mode()
        self._validate_ensemble_members()
        self._validate_highlighted_ensemble_members()
        self._validate_time_period()
        self._validate_baseline()
        self._validate_sampling()
        self._validate_data_type()

        return self.input_data

    def _validate_collection(self):
        # this must always be set
        if self.input_data.get_value(InputType.COLLECTION) is None:
            raise Exception("{} not set".format(InputType.COLLECTION))

    def _validate_spatial_rep(self):
        spatial_rep = self.input_data.get_value(InputType.SPATIAL_REPRESENTATION)
        # TODO
        #                 raise Exception("Invalid {value_type}: {value}.".format(
        # value_type=InputType.SPATIAL_REPRESENTATION, value=spatial_rep))
        if spatial_rep is None:
            # Not set, lets be kind and set it
            if self.input_data.get_area_type() in [AreaType.BBOX, AreaType.POINT]:
                if (
                    self.input_data.get_value(InputType.COLLECTION) == COLLECTION_GCM
                    or self.input_data.get_value(InputType.COLLECTION)
                    == COLLECTION_DERIVED
                ):
                    self.input_data.set_value(InputType.SPATIAL_REPRESENTATION, "60km")
                elif self.input_data.get_value(InputType.COLLECTION) == COLLECTION_CPM:
                    self.input_data.set_value(InputType.SPATIAL_REPRESENTATION, "5km")
                elif self.input_data.get_value(InputType.COLLECTION) in [
                    COLLECTION_OBS,
                    COLLECTION_RCM,
                    COLLECTION_RCM_GWL,
                ]:
                    self.input_data.set_value(InputType.SPATIAL_REPRESENTATION, "12km")
                elif self.input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB:
                    self.input_data.set_value(InputType.SPATIAL_REPRESENTATION, "25km")

            elif self.input_data.get_area_type() in [
                AreaType.COAST_POINT,
                AreaType.GAUGE_POINT,
            ]:
                # TODO What should this be?
                pass

            else:
                self.input_data.set_value(
                    InputType.SPATIAL_REPRESENTATION, self.input_data.get_area_type()
                )

    def _validate_colour_mode(self):
        if self.input_data.get_value(InputType.COLOUR_MODE) is None:
            # Not set, lets be kind and set it to 'c'
            self.input_data.set_value(InputType.COLOUR_MODE, "c")

    def _validate_convert_to_percentiles(self):
        convert_to_percentiles = self.input_data.get_value(
            InputType.CONVERT_TO_PERCENTILES
        )
        if (convert_to_percentiles is not None) and (
            not isinstance(convert_to_percentiles, bool)
        ):
            raise Exception(
                "Invalid {value_type}: {value}.".format(
                    value_type=InputType.CONVERT_TO_PERCENTILES,
                    value=convert_to_percentiles,
                )
            )

    def _validate_overlay_probability_levels(self):
        overlay_probability_levels = self.input_data.get_value(
            InputType.OVERLAY_PROBABILITY_LEVELS
        )
        if (overlay_probability_levels is not None) and (
            not isinstance(overlay_probability_levels, bool)
        ):
            raise Exception(
                "Invalid {value_type}: {value}.".format(
                    value_type=InputType.OVERLAY_PROBABILITY_LEVELS,
                    value=overlay_probability_levels,
                )
            )

    def _validate_time_slice(self):
        year = self.input_data.get_value(InputType.YEAR)
        year_min = self.input_data.get_value(InputType.YEAR_MINIMUM)
        year_max = self.input_data.get_value(InputType.YEAR_MAXIMUM)

        if year_max is not None and year_min is None:
            # if max is set then min must be set
            raise Exception(
                "{min} must be provided when {max} is set".format(
                    min=InputType.YEAR_MINIMUM, max=InputType.YEAR_MAXIMUM
                )
            )

        if year_min is not None and year_max is None:
            # if min is set then max must be set
            raise Exception(
                "{max} must be provided when {min} is set".format(
                    min=InputType.YEAR_MINIMUM, max=InputType.YEAR_MAXIMUM
                )
            )

        if year is not None and year_max is not None:
            # year and max should not be set at the same time
            raise Exception(
                "{year} cannot be set at the same time as {min} "
                "and {max}".format(
                    year=InputType.YEAR,
                    min=InputType.YEAR_MINIMUM,
                    max=InputType.YEAR_MAXIMUM,
                )
            )

        if year is not None:
            # if year is set then set min and max to equal year
            self.input_data.set_value(InputType.YEAR_MINIMUM, year)
            self.input_data.set_value(InputType.YEAR_MAXIMUM, year)

        if self.input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB:
            min_allowed_year = COLLECTION_PROB_MIN_YEAR
        elif self.input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE:
            min_allowed_year = COLLECTION_MARINE_MIN_YEAR
        elif self.input_data.get_value(InputType.COLLECTION) in [
            COLLECTION_CPM,
            COLLECTION_RCM,
            COLLECTION_RCM_GWL,
        ]:
            min_allowed_year = COLLECTION_RCM_MIN_YEAR
        elif (
            self.input_data.get_value(InputType.COLLECTION) == COLLECTION_DERIVED
            and self.input_data.get_value(InputType.SCENARIO)[0] in GWL
        ):
            min_allowed_year = COLLECTION_DERIVED_GWL_MIN_YEAR
        elif self.input_data.get_value(InputType.COLLECTION) == COLLECTION_OBS:
            min_allowed_year = COLLECTION_OBS_MIN_YEAR
        else:
            min_allowed_year = min(self.vocab.get_collection_terms("year_minimum"))

        if self.input_data.get_value(InputType.YEAR_MINIMUM) < min_allowed_year:
            raise Exception(
                "The minimum year must be equal or greater than {}".format(
                    min_allowed_year
                )
            )

        if (
            self.input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE
            and self.input_data.get_value(InputType.METHOD) in EXTENDED_PROJECTIONS
        ):
            max_allowed_year = COLLECTION_MARINE_MAX_YEAR
        elif (
            self.input_data.get_value(InputType.COLLECTION) == COLLECTION_DERIVED
            and self.input_data.get_value(InputType.SCENARIO)[0] in GWL
        ):
            max_allowed_year = COLLECTION_DERIVED_GWL_MAX_YEAR
        else:
            max_allowed_year = OTHER_MAX_YEAR

        if self.input_data.get_value(InputType.YEAR_MAXIMUM) > max_allowed_year:
            raise Exception(
                "The maximum year must be equal or less than {}".format(
                    max_allowed_year
                )
            )

    def _validate_ensemble_members(self):
        ensembles = self.input_data.get_value(InputType.ENSEMBLE)
        if ensembles is not None:
            self._validate_ensembles(ensembles, InputType.ENSEMBLE)

    def _validate_highlighted_ensemble_members(self):
        # if no value is set, then set as an empty list
        ensembles = self.input_data.get_value(InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS)
        if ensembles is None:
            self.input_data.set_values(InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS, [])
            return

        if len(ensembles) > 5:
            raise Exception("The maximum number of highlighted ensemble members is 5")

        self._validate_ensembles(ensembles, InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS)

    def _validate_ensembles(self, ensembles, input_type):
        allowed_ensembles = get_ensemble_member_set(
            self.input_data.get_value(InputType.COLLECTION)
        )
        if allowed_ensembles is None:
            raise Exception(
                "Unable to get list of valid ensembles for {}".format(
                    self.input_data.get_value(InputType.COLLECTION)
                )
            )

        for ensemble in ensembles:
            if ensemble not in allowed_ensembles:
                raise Exception(
                    "Invalid {value_type} for {collection}: {value}.".format(
                        value_type=input_type,
                        collection=self.input_data.get_value(InputType.COLLECTION),
                        value=ensemble,
                    )
                )

    def _validate_time_period(self):
        # if a temporal average type is set then check the time period is valid
        # for that type
        temporal_average_type = self.input_data.get_value(
            InputType.TEMPORAL_AVERAGE_TYPE
        )
        if temporal_average_type is None:
            return

        time_period = self.input_data.get_value(InputType.TIME_PERIOD)
        allowed_time_periods = self.vocab.get_collection_terms(temporal_average_type)

        # special case for all
        if (
            temporal_average_type
            in [
                TemporalAverageType.DAILY,
                TemporalAverageType.MONTHLY,
                TemporalAverageType.SEASONAL,
            ]
        ) and time_period == "all":
            return

        if time_period not in allowed_time_periods:
            type_label = self.vocab.get_collection_term_label(
                InputType.TEMPORAL_AVERAGE_TYPE, temporal_average_type
            )
            raise Exception(
                "{time_period} is not a {type_label} value".format(
                    time_period=time_period, type_label=type_label
                )
            )

    def _validate_baseline(self):
        # only a subset of values are allowed for CPM and RCM
        if self.input_data.get_value(InputType.COLLECTION) in [
            COLLECTION_CPM,
            COLLECTION_RCM,
            COLLECTION_RCM_GWL,
        ]:
            baseline = self.input_data.get_value(InputType.BASELINE)
            if baseline is None:
                return
            allowed_baselines = self.vocab.get_collection_terms(InputType.BASELINE)
            # the first one is not allowed for RCM
            allowed_baselines.pop(0)

            if baseline not in allowed_baselines:
                raise Exception(
                    "Invalid {value_type}: {value}.".format(
                        value_type=InputType.BASELINE, value=baseline
                    )
                )

    def _validate_sampling(self):
        # if a sampling method is set then check the dependencies are valid
        sampling_method = self.input_data.get_value(InputType.SAMPLING_METHOD)

        if sampling_method is None or sampling_method == "all":
            return

        if sampling_method == "id":
            sampling_id = self.input_data.get_value(InputType.SAMPLING_ID)
            if sampling_id is None:
                raise Exception("{} must be set".format(InputType.SAMPLING_ID))
            if len(sampling_id) != len(set(sampling_id)):
                raise Exception(
                    "{} must not contain duplicates".format(InputType.SAMPLING_ID)
                )
            if len(sampling_id) < 100 or len(sampling_id) > 4000:
                raise Exception(
                    "{} must contain between 100 and 4000 values".format(
                        InputType.SAMPLING_ID
                    )
                )

        if sampling_method == "random":
            random_sampling_count = self.input_data.get_value(
                InputType.RANDOM_SAMPLING_COUNT
            )
            if random_sampling_count is None:
                raise Exception(
                    "{} must be set".format(InputType.RANDOM_SAMPLING_COUNT)
                )

        if sampling_method == "subset":
            sampling_subset_count = self.input_data.get_value(
                InputType.SAMPLING_SUBSET_COUNT
            )
            if sampling_subset_count is None:
                raise Exception(
                    "{} must be set".format(InputType.SAMPLING_SUBSET_COUNT)
                )

            if self.input_data.get_value(InputType.SAMPLING_PERCENTILE_1) is None:
                raise Exception(
                    "{} must be set".format(InputType.SAMPLING_PERCENTILE_1)
                )
            if self.input_data.get_value(InputType.SAMPLING_TEMPORAL_AVERAGE_1) is None:
                raise Exception(
                    "{} must be set".format(InputType.SAMPLING_TEMPORAL_AVERAGE_1)
                )
            if self.input_data.get_value(InputType.SAMPLING_VARIABLE_1) is None:
                raise Exception("{} must be set".format(InputType.SAMPLING_VARIABLE_1))

            if self.input_data.get_value(InputType.SAMPLING_SUBSET_COUNT) == 2:
                if self.input_data.get_value(InputType.SAMPLING_PERCENTILE_2) is None:
                    raise Exception(
                        "{} must be set".format(InputType.SAMPLING_PERCENTILE_2)
                    )
                if (
                    self.input_data.get_value(InputType.SAMPLING_TEMPORAL_AVERAGE_2)
                    is None
                ):
                    raise Exception(
                        "{} must be set".format(InputType.SAMPLING_TEMPORAL_AVERAGE_2)
                    )
                if self.input_data.get_value(InputType.SAMPLING_VARIABLE_2) is None:
                    raise Exception(
                        "{} must be set".format(InputType.SAMPLING_VARIABLE_2)
                    )

    def _validate_data_type(self):
        if self.input_data.get_value(InputType.COLLECTION) != COLLECTION_PROB:
            return
        if self.input_data.get_value(InputType.DATA_TYPE) is None:
            raise Exception("{} must be set".format(InputType.DATA_TYPE))
