from ukcp_dp.constants import DATA_SOURCE_PROB, InputType

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

        return self.input_data

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
        if self.input_data.get_value(InputType.COLOUR_MODE) is None:
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

        if (year is not None):
            # if year is set then set min and max to equal year
            self.input_data.set_value(InputType.YEAR_MINIMUM, year)
            self.input_data.set_value(InputType.YEAR_MAXIMUM, year)

    def _validate_boundary_overlay(self):
        try:
            self.input_data.get_value(InputType.SHOW_BOUNDARIES)
        except KeyError:
            self.input_data.set_value(InputType.SHOW_BOUNDARIES, 'none')

    def _validate_highlighted_ensemble_members(self):
        try:
            self.input_data.get_value(InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS)
        except KeyError:
            self.input_data._set_values(InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS,
                                        [])
