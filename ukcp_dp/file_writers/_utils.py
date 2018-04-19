from decimal import Decimal


TWO_PLACES = Decimal(10) ** -2


def convert_to_2dp(value):
    """
    Convert a value to string representation of a value to two decimal places.

    @param value: value to be converted

    @return a str containing the value to two decimal places
    """
    if str(value) == '--':
        return '--'
    return str(Decimal(float(value)).quantize(TWO_PLACES))