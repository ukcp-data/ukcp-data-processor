import matplotlib

matplotlib.use("agg")

from ukcp_dp.ukcp_data_processor import UKCPDataProcessor
from ukcp_dp.constants import DataFormat, ImageFormat, PlotType, InputType, VERSION


__version__ = VERSION


__all__ = ["UKCPDataProcessor", "DataFormat", "ImageFormat", "InputType", "PlotType"]
