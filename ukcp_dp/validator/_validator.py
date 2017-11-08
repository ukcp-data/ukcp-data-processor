from ukcp_dp.constants import InputType


class Validator():
    def validate(self, input_data):
        self.input_data = input_data
        self._validate_spatial_rep()
        self._validate_show_probability_levels()
        self._validate_time_slice()

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
                        'global_realisations'):
                    self.input_data.set_value(
                        InputType.SPATIAL_REPRESENTATION, '60km')
                elif (self.input_data.get_value(InputType.DATA_SOURCE) ==
                        'regional_realisations'):
                    self.input_data.set_value(
                        InputType.SPATIAL_REPRESENTATION, '12km')
                elif (self.input_data.get_value(InputType.DATA_SOURCE) ==
                        'land_probabilistic'):
                    self.input_data.set_value(
                        InputType.SPATIAL_REPRESENTATION, '25km')
            else:
                self.input_data.set_value(
                    InputType.SPATIAL_REPRESENTATION,
                    self.input_data.get_area_type())

    def _validate_show_probability_levels(self):
        try:
            show_probability_levels = self.input_data.get_value(
                InputType.SHOW_PROBABILITY_LEVELS)
            if not isinstance(show_probability_levels, bool):
                raise Exception("Invalid {value_type}: {value}.".format(
                    value_type=InputType.SHOW_PROBABILITY_LEVELS,
                    value=show_probability_levels))

        except KeyError:
            # Not set, lets be kind and set it to False
            self.input_data.set_value(InputType.SHOW_PROBABILITY_LEVELS, False)

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
            raise Exception("{min} must be provided when {max} is set".format(
                min=InputType.YEAR_MINIMUM, max=InputType.YEAR_MAXIMUM))

        if (year_min is not None and year_max is None):
            raise Exception("{max} must be provided when {min} is set".format(
                min=InputType.YEAR_MINIMUM, max=InputType.YEAR_MAXIMUM))

        if (year is not None and year_max is not None):
            raise Exception("{year} cannot be set at the same time as {min} "
                            "and {max}".format(year=InputType.YEAR,
                                               min=InputType.YEAR_MINIMUM,
                                               max=InputType.YEAR_MAXIMUM))
