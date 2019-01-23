from decimal import Decimal

from ukcp_dp.constants import VARIABLES_0DP, VARIABLES_1DP, VARIABLES_2DP, \
    VARIABLES_3DP, VARIABLES_4DP


ZERO_PLACES = Decimal(10) ** 1
ONE_PLACES = Decimal(10) ** -1
TWO_PLACES = Decimal(10) ** -2
THREE_PLACES = Decimal(10) ** -3
FOUR_PLACES = Decimal(10) ** -4


def round_variable(variable, value):
    """
    Round the value for the variable.
    The rounding factor is defined for each variable in the constants.py

    @param variable (str): the name of the variable
    @param value (str): the value to round

    @return a str containing the rounded value
    """
    if variable in VARIABLES_0DP:
        return convert_to_0dp(value)
    elif variable in VARIABLES_1DP:
        return convert_to_1dp(value)
    elif variable in VARIABLES_2DP:
        return convert_to_2dp(value)
    elif variable in VARIABLES_3DP:
        return convert_to_3dp(value)
    elif variable in VARIABLES_4DP:
        return convert_to_4dp(value)
    else:
        return convert_to_2dp(value)


def convert_to_0dp(value):
    """
    Convert a value to string representation of a value to zero decimal places.

    @param value: value to be converted

    @return a str containing the value to zero decimal places
    """
    if str(value) == '--':
        return '--'
    return str(Decimal(float(value)).quantize(ZERO_PLACES))


def convert_to_1dp(value):
    """
    Convert a value to string representation of a value to one decimal place.

    @param value: value to be converted

    @return a str containing the value to one decimal place
    """
    if str(value) == '--':
        return '--'
    return str(Decimal(float(value)).quantize(ONE_PLACES))


def convert_to_2dp(value):
    """
    Convert a value to string representation of a value to two decimal places.

    @param value: value to be converted

    @return a str containing the value to two decimal places
    """
    if str(value) == '--':
        return '--'
    return str(Decimal(float(value)).quantize(TWO_PLACES))


def convert_to_3dp(value):
    """
    Convert a value to string representation of a value to tree decimal places.

    @param value: value to be converted

    @return a str containing the value to three decimal places
    """
    if str(value) == '--':
        return '--'
    return str(Decimal(float(value)).quantize(THREE_PLACES))


def convert_to_4dp(value):
    """
    Convert a value to string representation of a value to two decimal places.

    @param value: value to be converted

    @return a str containing the value to two decimal places
    """
    if str(value) == '--':
        return '--'
    return str(Decimal(float(value)).quantize(FOUR_PLACES))
