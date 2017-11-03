from ukcp_dp.constants import InputType


class Validator():
    def validate(self, input_data):
        self.input_data = input_data
        self._validate_spatial_rep()

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
