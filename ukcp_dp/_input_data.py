from constants import InputType, INPUT_TYPES, INPUT_TYPES_SINGLE_VALUE, \
    INPUT_TYPES_MULTI_VALUE, FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, \
    FONT_SIZE_LARGE, AreaType


class InputData(object):
    """
    This class is designed to validate and store user inputs.
    In most cases validation is done against a set of facet values. Access
    methods are provided for the values as well as the labels of the values.

    """

    def __init__(self, vocab):
        """
        Initialise the class.

        @param vocab (Vocab): an instance of the ukcp_dp Vocab class
        """
        self.vocab = vocab
        self.validated_inputs = {}
        self.allowed_values = {}

    def __str__(self):
        x = ('validated_inputs:{validated_inputs}, allowed_values:'
             '{allowed_values}'.format(validated_inputs=self.validated_inputs,
                                       allowed_values=self.allowed_values))
        return x

    def get_user_inputs(self):
        """
        Get a dictionary representing the labels of the values set by the user.

        @return dict
            key(str) - the label of the collection
            value(str) - the label of the value
        """
        input_labels = {}
        for key in self.validated_inputs:
            key_label = self.vocab.get_collection_label(key)
            value = self.validated_inputs[key][1]
            if (len(value) == 0):
                continue
            if isinstance(value, list):
                value = ','.join(value)
            input_labels[key_label] = value.encode('utf-8')

        # remove extra year values
        if ((self.validated_inputs.get(InputType.YEAR) ==
                self.validated_inputs.get(InputType.YEAR_MINIMUM)) and
                (self.validated_inputs.get(InputType.YEAR) ==
                 self.validated_inputs.get(InputType.YEAR_MAXIMUM))):
            try:
                input_labels.pop(self.vocab.get_collection_label(
                    InputType.YEAR_MINIMUM))
                input_labels.pop(self.vocab.get_collection_label(
                    InputType.YEAR_MAXIMUM))
            except KeyError:
                pass
        else:
            try:
                input_labels.pop(InputType.YEAR)
            except KeyError:
                pass
        return input_labels

    def set_inputs(self, inputs, allowed_values=None):
        """
        Set the input values.

        An optional list of allowed values can be used to make additional
        checks when validating the input. They should define a subset of the
        facet values to use.

        @param inputs (dict):
            key(InputType) - this should match a value from the INPUT_TYPES
                list
            value(list or string or int) - the value(s) to set. These should
                match value(s) in the vocabulary as well as any constraints set
                by 'allowed_values'

        @param allowed_values (dict):
            key(InputType) - this should match a value from the INPUT_TYPES
                list
            value(list or string or int) - these are the values that the input
                are validated against
        """
        if allowed_values is not None:
            self._set_allowed_values(allowed_values)

        for input_type in INPUT_TYPES:
            try:
                if input_type in INPUT_TYPES_SINGLE_VALUE:
                    self.set_value(input_type, inputs[input_type])
                elif input_type in INPUT_TYPES_MULTI_VALUE:
                    self.set_values(input_type, inputs[input_type])
                elif input_type == InputType.AREA:
                    self._set_area(inputs[InputType.AREA])
            except KeyError:
                # looks like this 'type' was not set
                pass

    def set_value(self, value_type, value):
        """
        Set the value for the given type.

        @param value_type (InputType): the type of the value to set.
        @param value (str): the value to set

        @throws Exception
        """
        user_set_value = False
        # first lets check if the user has set any values
        if value_type in self.allowed_values.keys():
            # the user has set value(s)
            if value not in self.allowed_values[value_type]:

                raise Exception("Unknown {value_type}: {value}.".format(
                    value_type=value_type, value=value))

            user_set_value = True

        label = self.vocab.get_collection_term_label(value_type, value)
        if label is None:
            if user_set_value is True:
                # we do not insist that the value is in the vocabulary if it is
                # a user defined value
                self.validated_inputs[value_type] = [value, None]
            else:

                raise Exception("Unknown {value_type}: {value}.".format(
                    value_type=value_type, value=value))

        self.validated_inputs[value_type] = [value, label]

    def set_values(self, value_type, values):
        """
        Set the value for the given type.

        @param value_type (InputType): the type of the values to set.
        @param values (str or list): the value(s) to set

        @throws Exception
        """
        if values is None:
            raise Exception("Unknown {value_type}: None.".format(
                value_type=value_type))

        if not isinstance(values, list):
            values = [values]
        if value_type in self.allowed_values.keys():
            for value in values:

                if value not in self.allowed_values[value_type]:
                    raise Exception("Unknown {value_type}: {value}.".format(
                        value_type=value_type, value=value))

        labels = []
        for value in values:
            label = self.vocab.get_collection_term_label(value_type, value)

            if label is None:
                raise Exception("Unknown {value_type}: {value}.".format(
                    value_type=value_type, value=value))

            labels.append(label)
        self.validated_inputs[value_type] = [values, labels]

    def get_value(self, value_type):
        """
        Get the value for the given value type.

        @param value_type (InputType): the type of the value to get.

        @return the value for the value_type

        """
        value = self.validated_inputs.get(value_type)
        if isinstance(value, list):
            return value[0]
        return value

    def get_value_label(self, value_type):
        """
        Get the label for the data given value type.

        @param value_type (InputType): the type of the value to get.

        @return the value label for the value_type
        """
        return(self.validated_inputs[value_type][1])

    # Area
    def _set_area(self, area):
        """
        Set the geographical area, this may be a point, bbox or a spatially
        aggregated area.

        Having called set_area it is possible to retrieve the area type:
            'point', 'bbox', 'coast_point', 'gauge_point', 'country',
            'admin_region' or 'river_basin'
        The area type label:
            'Country', 'Administrative Region' or 'River Basin'
        The areas
            [x,y] or 'wales' etc.
        And the area labels
            'Wales' etc.

        @param area (list or str): For a point, coast_point, gauge_point and
            bbox the data should be provided as a list:
                ['point',x,y]
                ['coast_point',lat,long]
                ['gauge_point',lat,long]
                ['bbox',southern boundary, eastern boundary, northern boundary,
                western boundary]
            For a spatially aggregated area the data should be provided as a
            string:
                'country|Wales'

        @throws Exception

        """
        if type(area) is list:
            # this will be a bbox or point, i.e.
            # ['point',430311.27,253673.63]
            area_type = area.pop(0)

            if (area_type not in
                    [AreaType.BBOX, AreaType.POINT, AreaType.COAST_POINT,
                     AreaType.GAUGE_POINT]):
                raise Exception("Unknown area: {}.".format(area))

            area_type_label = self.vocab.get_collection_term_label(
                InputType.AREA, area_type)
            self.validated_inputs[InputType.AREA] = [
                area_type, area_type_label, area, area]
        else:
            # this will be a predefined region, i.e.
            # country|Scotland
            area_type, area_name = area.split('|', 1)

            # check the area type
            area_type_label = self.vocab.get_collection_term_label(
                InputType.AREA, area_type)
            if area_type_label is None:
                raise Exception("Unknown area type: {}.".format(area_type))

            # check the area name
            area_label = self.vocab.get_collection_term_label(
                area_type, area_name)
            if (area_label is None):

                # currently the names are stored as 'labels' in the shape files
                # so need to convert the label to the value
                area_label = area_name
                area_name = self.vocab.get_collection_term_value(
                    area_type, area_name)
                if area_name is None:
                    raise Exception("Unknown area name: {}.".format(area_name))

            self.validated_inputs[InputType.AREA] = [area_type,
                                                     area_type_label,
                                                     area_name,
                                                     area_label]

    def get_area_type(self):
        """
        Get the value for the area type.

        @return a str containing the area type

        """
        return(self.validated_inputs[InputType.AREA][0])

    def get_area_type_label(self):
        """
        Get the label for the area type.

        @return a str containing the area type label

        """
        return(self.validated_inputs[InputType.AREA][1])

    def get_area(self):
        """
        Get the value of the area.

        @return a str or list dependent on the area type. It will be a list of
            2 or 4 floats for a point or bbox or a string for a region.

        """
        return(self.validated_inputs[InputType.AREA][2])

    def get_area_label(self):
        """
        Get the name of the area.

        @return a str containing the area label

        """
        return(self.validated_inputs[InputType.AREA][3])

    def get_font_size(self):
        """
        Get the font size.

        @return an int representing the font size
        """
        if self.get_value(InputType.FONT_SIZE) == 's':
            return FONT_SIZE_SMALL
        elif self.get_value(InputType.FONT_SIZE) == 'm':
            return FONT_SIZE_MEDIUM
        elif self.get_value(InputType.FONT_SIZE) == 'l':
            return FONT_SIZE_LARGE

    def _set_allowed_values(self, allowed_values):
        for key in allowed_values.keys():
            if key in INPUT_TYPES:
                if type(allowed_values[key]) == list:
                    self.allowed_values[key] = allowed_values[key]
                else:
                    self.allowed_values[key] = [allowed_values[key]]
