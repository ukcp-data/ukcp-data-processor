from decimal import Decimal


TWO_PLACES = Decimal(10) ** -2
THREE_PLACES = Decimal(10) ** -3
FOUR_PLACES = Decimal(10) ** -4


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
