# Must be run before importing numpy.
import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

import matplotlib

matplotlib.use("agg")

import dask

from ukcp_dp.ukcp_data_processor import UKCPDataProcessor
from ukcp_dp.constants import (
    AreaType,
    DataFormat,
    ImageFormat,
    PlotType,
    InputType,
    VERSION,
)


# Set globally
dask.config.set(scheduler="synchronous")
dask.config.set({"array.chunk-size": "256 MiB"})

__version__ = VERSION


__all__ = [
    "UKCPDataProcessor",
    "AreaType",
    "DataFormat",
    "ImageFormat",
    "InputType",
    "PlotType",
]
