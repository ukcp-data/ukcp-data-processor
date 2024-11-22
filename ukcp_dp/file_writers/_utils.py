"""
A utils module for the file writers.

"""


def ensemble_to_string(ensemble_no):
    """
    Format the ensemble number.

    If the number is less than 0 add a leading 0

    @param ensemble_no(int): the ensemble number
    @return a string representation of 2 digits
    """
    if ensemble_no < 10:
        return f"0{ensemble_no}"
    return str(ensemble_no)
