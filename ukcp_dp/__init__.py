# Must be run before importing numpy.
import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import matplotlib

matplotlib.use("agg")

from ukcp_dp.ukcp_data_processor import UKCPDataProcessor
from ukcp_dp.constants import DataFormat, ImageFormat, PlotType, InputType, VERSION


__version__ = VERSION


__all__ = ["UKCPDataProcessor", "DataFormat", "ImageFormat", "InputType", "PlotType"]
