"""
UKCP Data Processor exceptions.

"""


class UKCPDataProcessorException(Exception):
    """
    Base class for UKCP Data Processor exceptions.

    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class UKCPDPDataNotFoundException(UKCPDataProcessorException):
    """
    UKCP Data Processor data not found exception.

    """

    def __init__(self, *args, **kwargs):
        UKCPDataProcessorException.__init__(self, *args, **kwargs)


class UKCPDPInvalidParameterException(UKCPDataProcessorException):
    """
    Base class for UKCP Data Processor invalid parameter exception.

    """

    def __init__(self, *args, **kwargs):
        UKCPDataProcessorException.__init__(self, *args, **kwargs)
