"""
This package provides a means to compare netCDF headers with reference headers.

"""

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import difflib
import glob
import subprocess
import sys


PRODUCTION = "/badc"
PRE_PROD = "/gws/pw/j07/ukcp18/pre-archive"

CPM_TEMPLATE = "/land-cpm/uk/{area}/**/{ensemble}/{variable}/{period}/{version}/*.nc"

PRE_PRODUCTION_PATH_TEMPLATE = f"{PRE_PROD}/ukcp18/data{CPM_TEMPLATE}"
PRODUCTION_PATH_TEMPLATE = f"{PRODUCTION}/ukcp18/data{CPM_TEMPLATE}"

CPM_AREAS = ["5km", "country", "region", "river"]

VARIABLES = [
    "tas",
    "pr",
    "tasmax",
    "tasmin",
    "sfcWind",
    "wsgmax10m",
    #     "hurs",
    #     "huss",
    #     "uas",
    #     "vas",
    #     "prsn",
    #     "snw",
    #     "psl",
    #     "rls",
    #     "rss",
    #     "clt",
]

PERIODS = ["day"]

ENSEMBLES = ["01", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "15"]
ENSEMBLES_INC_CMIP = ENSEMBLES + ["23", "25", "27", "29"]

NCDUMP = "/usr/local/miniforge/envs/ukcp18/bin/ncdump"
IGNORE_HEADERS = [
    "netcdf",
    ":_Format",
    ":_IsNetcdf4",
    "_NCProperties",
    "_SuperblockVersion",
    ":contact",
    ":creation_date",
    ":source",
    ":title",
    ":version",
]

VARIABLE_HEADERS = {
    "pr": [
        "\tfloat pr(ensemble_member, time, region) ;",
        "\t\tpr:_FillValue = 1.e+20f ;",
        '\t\tpr:standard_name = "lwe_precipitation_rate" ;',
        '\t\tpr:long_name = "Precipitation rate" ;',
        '\t\tpr:units = "mm/day" ;',
        '\t\tpr:description = "Precipitation rate" ;',
        '\t\tpr:label_units = "mm/day" ;',
        '\t\tpr:plot_label = "Precipitation rate (mm/day)" ;',
        '\t\tpr:cell_methods = "time: mean" ;',
        '\t\tpr:coordinates = "ensemble_member_id geo_region month_number year yyyymmdd" ;',
        '\t\tpr:_Storage = "contiguous" ;',
        '\t\tpr:_Endianness = "little" ;',
    ],
    "sfcWind": [
        "\tfloat sfcWind(ensemble_member, time, region) ;",
        "\t\tsfcWind:_FillValue = 1.e+20f ;",
        '\t\tsfcWind:standard_name = "wind_speed" ;',
        '\t\tsfcWind:long_name = "Wind speed at 10m" ;',
        '\t\tsfcWind:units = "m s-1" ;',
        '\t\tsfcWind:description = "Wind speed" ;',
        '\t\tsfcWind:label_units = "m s-1" ;',
        '\t\tsfcWind:plot_label = "Wind speed at 10m (m s-1)" ;',
        '\t\tsfcWind:cell_methods = "time: mean" ;',
        '\t\tsfcWind:coordinates = "ensemble_member_id geo_region month_number year yyyymmdd" ;',
        '\t\tsfcWind:_Storage = "contiguous" ;',
        '\t\tsfcWind:_Endianness = "little" ;',
    ],
    "tas": [
        "\tfloat tas(ensemble_member, time, region) ;",
        "\t\ttas:_FillValue = 1.e+20f ;",
        '\t\ttas:standard_name = "air_temperature" ;',
        '\t\ttas:long_name = "Mean air temperature" ;',
        '\t\ttas:units = "degC" ;',
        '\t\ttas:description = "Mean air temperature" ;',
        '\t\ttas:label_units = "°C" ;',
        '\t\ttas:plot_label = "Mean air temperature at 1.5m (°C)" ;',
        '\t\ttas:cell_methods = "time: mean" ;',
        '\t\ttas:coordinates = "ensemble_member_id geo_region month_number year yyyymmdd" ;',
        '\t\ttas:_Storage = "contiguous" ;',
        '\t\ttas:_Endianness = "little" ;',
    ],
    "tasmax": [
        "\tfloat tasmax(ensemble_member, time, region) ;",
        "\t\ttasmax:_FillValue = 1.e+20f ;",
        '\t\ttasmax:standard_name = "air_temperature" ;',
        '\t\ttasmax:long_name = "Maximum air temperature" ;',
        '\t\ttasmax:units = "degC" ;',
        '\t\ttasmax:description = "Maximum air temperature" ;',
        '\t\ttasmax:label_units = "°C" ;',
        '\t\ttasmax:plot_label = "Maximum air temperature at 1.5m (°C)" ;',
        '\t\ttasmax:cell_methods = "time: mean" ;',
        '\t\ttasmax:coordinates = "ensemble_member_id geo_region month_number year yyyymmdd" ;',
        '\t\ttasmax:_Storage = "contiguous" ;',
        '\t\ttasmax:_Endianness = "little" ;',
    ],
    "tasmin": [
        "\tfloat tasmin(ensemble_member, time, region) ;",
        "\t\ttasmin:_FillValue = 1.e+20f ;",
        '\t\ttasmin:standard_name = "air_temperature" ;',
        '\t\ttasmin:long_name = "Minimum air temperature" ;',
        '\t\ttasmin:units = "degC" ;',
        '\t\ttasmin:description = "Minimum air temperature" ;',
        '\t\ttasmin:label_units = "°C" ;',
        '\t\ttasmin:plot_label = "Minimum air temperature at 1.5m (°C)" ;',
        '\t\ttasmin:cell_methods = "time: mean" ;',
        '\t\ttasmin:coordinates = "ensemble_member_id geo_region month_number year yyyymmdd" ;',
        '\t\ttasmin:_Storage = "contiguous" ;',
        '\t\ttasmin:_Endianness = "little" ;',
    ],
    "wsgmax10m": [
        "\tdouble wsgmax10m(ensemble_member, time, region) ;",
        # "\t\twsgmax10m:_FillValue = 1.e+20f ;",
        "\t\twsgmax10m:_FillValue = 1.e+20 ;",
        '\t\twsgmax10m:standard_name = "wind_speed_of_gust" ;',
        '\t\twsgmax10m:long_name = "Maximum Wind Speed of Gust at 10m" ;',
        '\t\twsgmax10m:units = "m s-1" ;',
        '\t\twsgmax10m:description = "Wind speed gust maximum" ;',
        '\t\twsgmax10m:label_units = "m s-1" ;',
        '\t\twsgmax10m:plot_label = "Wind speed gust maximum at 10m (m s-1)" ;',
        '\t\twsgmax10m:cell_methods = "time: mean" ;',
        '\t\twsgmax10m:coordinates = "ensemble_member_id geo_region month_number year yyyymmdd" ;',
        '\t\twsgmax10m:_Storage = "contiguous" ;',
        '\t\twsgmax10m:_Endianness = "little" ;',
    ],
}
VARIABLE_HEADERS_GRID = {
    "pr": [
        "\tfloat pr(ensemble_member, time, projection_y_coordinate, projection_x_coordinate) ;",
        "\t\tpr:_FillValue = 1.e+20f ;",
        '\t\tpr:standard_name = "lwe_precipitation_rate" ;',
        '\t\tpr:long_name = "Precipitation rate" ;',
        '\t\tpr:units = "mm/day" ;',
        '\t\tpr:description = "Precipitation rate" ;',
        '\t\tpr:label_units = "mm/day" ;',
        '\t\tpr:plot_label = "Precipitation rate (mm/day)" ;',
        '\t\tpr:cell_methods = "time: mean" ;',
        '\t\tpr:grid_mapping = "transverse_mercator" ;',
        '\t\tpr:coordinates = "ensemble_member_id latitude longitude month_number year yyyymmdd" ;',
        '\t\tpr:_Storage = "contiguous" ;',
        '\t\tpr:_Endianness = "little" ;',
    ],
    "sfcWind": [
        "\tfloat sfcWind(ensemble_member, time, projection_y_coordinate, projection_x_coordinate) ;",
        "\t\tsfcWind:_FillValue = 1.e+20f ;",
        '\t\tsfcWind:standard_name = "wind_speed" ;',
        '\t\tsfcWind:long_name = "Wind speed at 10m" ;',
        '\t\tsfcWind:units = "m s-1" ;',
        '\t\tsfcWind:description = "Wind speed" ;',
        '\t\tsfcWind:label_units = "m s-1" ;',
        '\t\tsfcWind:plot_label = "Wind speed at 10m (m s-1)" ;',
        '\t\tsfcWind:cell_methods = "time: mean" ;',
        '\t\tsfcWind:grid_mapping = "transverse_mercator" ;',
        '\t\tsfcWind:coordinates = "ensemble_member_id latitude longitude month_number year yyyymmdd" ;',
        '\t\tsfcWind:_Storage = "contiguous" ;',
        '\t\tsfcWind:_Endianness = "little" ;',
    ],
    "tas": [
        "\tfloat tas(ensemble_member, time, projection_y_coordinate, projection_x_coordinate) ;",
        "\t\ttas:_FillValue = 1.e+20f ;",
        '\t\ttas:standard_name = "air_temperature" ;',
        '\t\ttas:long_name = "Mean air temperature" ;',
        '\t\ttas:units = "degC" ;',
        '\t\ttas:description = "Mean air temperature" ;',
        '\t\ttas:label_units = "°C" ;',
        '\t\ttas:plot_label = "Mean air temperature at 1.5m (°C)" ;',
        '\t\ttas:cell_methods = "time: mean" ;',
        '\t\ttas:grid_mapping = "transverse_mercator" ;',
        '\t\ttas:coordinates = "ensemble_member_id latitude longitude month_number year yyyymmdd" ;',
        '\t\ttas:_Storage = "contiguous" ;',
        '\t\ttas:_Endianness = "little" ;',
    ],
    "tasmax": [
        "\tfloat tasmax(ensemble_member, time, projection_y_coordinate, projection_x_coordinate) ;",
        "\t\ttasmax:_FillValue = 1.e+20f ;",
        '\t\ttasmax:standard_name = "air_temperature" ;',
        '\t\ttasmax:long_name = "Maximum air temperature" ;',
        '\t\ttasmax:units = "degC" ;',
        '\t\ttasmax:description = "Maximum air temperature" ;',
        '\t\ttasmax:label_units = "°C" ;',
        '\t\ttasmax:plot_label = "Maximum air temperature at 1.5m (°C)" ;',
        '\t\ttasmax:cell_methods = "time: mean" ;',
        '\t\ttasmax:grid_mapping = "transverse_mercator" ;',
        '\t\ttasmax:coordinates = "ensemble_member_id latitude longitude month_number year yyyymmdd" ;',
        '\t\ttasmax:_Storage = "contiguous" ;',
        '\t\ttasmax:_Endianness = "little" ;',
    ],
    "tasmin": [
        "\tfloat tasmin(ensemble_member, time, projection_y_coordinate, projection_x_coordinate) ;",
        "\t\ttasmin:_FillValue = 1.e+20f ;",
        '\t\ttasmin:standard_name = "air_temperature" ;',
        '\t\ttasmin:long_name = "Minimum air temperature" ;',
        '\t\ttasmin:units = "degC" ;',
        '\t\ttasmin:description = "Minimum air temperature" ;',
        '\t\ttasmin:label_units = "°C" ;',
        '\t\ttasmin:plot_label = "Minimum air temperature at 1.5m (°C)" ;',
        '\t\ttasmin:cell_methods = "time: mean" ;',
        '\t\ttasmin:grid_mapping = "transverse_mercator" ;',
        '\t\ttasmin:coordinates = "ensemble_member_id latitude longitude month_number year yyyymmdd" ;',
        '\t\ttasmin:_Storage = "contiguous" ;',
        '\t\ttasmin:_Endianness = "little" ;',
    ],
    "wsgmax10m": [
        "\tfloat wsgmax10m(ensemble_member, time, projection_y_coordinate, projection_x_coordinate) ;",
        # "\t\twsgmax10m:_FillValue = 1.e+20f ;",
        "\t\twsgmax10m:_FillValue = 1.e+20 ;",
        '\t\twsgmax10m:standard_name = "wind_speed_of_gust" ;',
        '\t\twsgmax10m:long_name = "Maximum Wind Speed of Gust at 10m" ;',
        '\t\twsgmax10m:units = "m s-1" ;',
        '\t\twsgmax10m:description = "Wind speed gust maximum" ;',
        '\t\twsgmax10m:label_units = "m s-1" ;',
        '\t\twsgmax10m:plot_label = "Wind speed gust maximum at 10m (m s-1)" ;',
        '\t\twsgmax10m:cell_methods = "time: mean" ;',
        '\t\twsgmax10m:grid_mapping = "transverse_mercator" ;',
        '\t\twsgmax10m:coordinates = "ensemble_member_id latitude longitude month_number year yyyymmdd" ;',
        '\t\twsgmax10m:_Storage = "contiguous" ;',
        '\t\twsgmax10m:_Endianness = "little" ;',
    ],
}
SAMPLE_HEADERS = {
    "5km": {
        "day": [
            "dimensions:",
            "\tensemble_member = 1 ;",
            "\ttime = 3600 ;",
            "\tprojection_y_coordinate = 244 ;",
            "\tprojection_x_coordinate = 180 ;",
            "\tbnds = 2 ;",
            "\tstring27 = 27 ;",
            "\tstring64 = 64 ;",
            "variables:",
            "\tint transverse_mercator ;",
            '\t\ttransverse_mercator:grid_mapping_name = "transverse_mercator" ;',
            "\t\ttransverse_mercator:longitude_of_prime_meridian = 0. ;",
            "\t\ttransverse_mercator:semi_major_axis = 6377563.396 ;",
            "\t\ttransverse_mercator:semi_minor_axis = 6356256.909 ;",
            "\t\ttransverse_mercator:longitude_of_central_meridian = -2. ;",
            "\t\ttransverse_mercator:latitude_of_projection_origin = 49. ;",
            "\t\ttransverse_mercator:false_easting = 400000. ;",
            "\t\ttransverse_mercator:false_northing = -100000. ;",
            "\t\ttransverse_mercator:scale_factor_at_central_meridian = 0.9996012717 ;",
            '\t\ttransverse_mercator:_Storage = "contiguous" ;',
            '\t\ttransverse_mercator:_Endianness = "little" ;',
            "\tint ensemble_member(ensemble_member) ;",
            '\t\tensemble_member:units = "1" ;',
            '\t\tensemble_member:long_name = "ensemble_member" ;',
            '\t\tensemble_member:_Storage = "contiguous" ;',
            '\t\tensemble_member:_Endianness = "little" ;',
            "\tdouble time(time) ;",
            '\t\ttime:axis = "T" ;',
            '\t\ttime:bounds = "time_bnds" ;',
            '\t\ttime:units = "hours since 1970-01-01 00:00:00" ;',
            '\t\ttime:standard_name = "time" ;',
            '\t\ttime:calendar = "360_day" ;',
            '\t\ttime:_Storage = "contiguous" ;',
            '\t\ttime:_Endianness = "little" ;',
            "\tdouble time_bnds(time, bnds) ;",
            '\t\ttime_bnds:_Storage = "contiguous" ;',
            '\t\ttime_bnds:_Endianness = "little" ;',
            "\tdouble projection_y_coordinate(projection_y_coordinate) ;",
            '\t\tprojection_y_coordinate:axis = "Y" ;',
            '\t\tprojection_y_coordinate:bounds = "projection_y_coordinate_bnds" ;',
            '\t\tprojection_y_coordinate:units = "m" ;',
            '\t\tprojection_y_coordinate:standard_name = "projection_y_coordinate" ;',
            '\t\tprojection_y_coordinate:_Storage = "contiguous" ;',
            '\t\tprojection_y_coordinate:_Endianness = "little" ;',
            "\tdouble projection_y_coordinate_bnds(projection_y_coordinate, bnds) ;",
            '\t\tprojection_y_coordinate_bnds:_Storage = "contiguous" ;',
            '\t\tprojection_y_coordinate_bnds:_Endianness = "little" ;',
            "\tdouble projection_x_coordinate(projection_x_coordinate) ;",
            '\t\tprojection_x_coordinate:axis = "X" ;',
            '\t\tprojection_x_coordinate:bounds = "projection_x_coordinate_bnds" ;',
            '\t\tprojection_x_coordinate:units = "m" ;',
            '\t\tprojection_x_coordinate:standard_name = "projection_x_coordinate" ;',
            '\t\tprojection_x_coordinate:_Storage = "contiguous" ;',
            '\t\tprojection_x_coordinate:_Endianness = "little" ;',
            "\tdouble projection_x_coordinate_bnds(projection_x_coordinate, bnds) ;",
            '\t\tprojection_x_coordinate_bnds:_Storage = "contiguous" ;',
            '\t\tprojection_x_coordinate_bnds:_Endianness = "little" ;',
            "\tchar ensemble_member_id(ensemble_member, string27) ;",
            '\t\tensemble_member_id:units = "1" ;',
            '\t\tensemble_member_id:long_name = "ensemble_member_id" ;',
            '\t\tensemble_member_id:_Storage = "contiguous" ;',
            "\tdouble latitude(projection_y_coordinate, projection_x_coordinate) ;",
            '\t\tlatitude:units = "degrees_north" ;',
            '\t\tlatitude:standard_name = "latitude" ;',
            '\t\tlatitude:_Storage = "contiguous" ;',
            '\t\tlatitude:_Endianness = "little" ;',
            "\tdouble longitude(projection_y_coordinate, projection_x_coordinate) ;",
            '\t\tlongitude:units = "degrees_east" ;',
            '\t\tlongitude:standard_name = "longitude" ;',
            '\t\tlongitude:_Storage = "contiguous" ;',
            '\t\tlongitude:_Endianness = "little" ;',
            "\tint month_number(time) ;",
            '\t\tmonth_number:units = "1" ;',
            '\t\tmonth_number:long_name = "month_number" ;',
            '\t\tmonth_number:_Storage = "contiguous" ;',
            '\t\tmonth_number:_Endianness = "little" ;',
            "\tint year(time) ;",
            '\t\tyear:units = "1" ;',
            '\t\tyear:long_name = "year" ;',
            '\t\tyear:_Storage = "contiguous" ;',
            '\t\tyear:_Endianness = "little" ;',
            "\tchar yyyymmdd(time, string64) ;",
            '\t\tyyyymmdd:units = "1" ;',
            '\t\tyyyymmdd:long_name = "yyyymmdd" ;',
            '\t\tyyyymmdd:_Storage = "contiguous" ;',
            "// global attributes:",
            '\t\t:collection = "land-cpm" ;',
            '\t\t:domain = "uk" ;',
            '\t\t:frequency = "day" ;',
            '\t\t:institution = "Met Office Hadley Centre (MOHC), FitzRoy Road, Exeter, Devon, '
            'EX1 3PB, UK." ;',
            '\t\t:institution_id = "MOHC" ;',
            '\t\t:project = "UKCP18" ;',
            '\t\t:references = "https://ukclimateprojections.metoffice.gov.uk" ;',
            '\t\t:resolution = "5km" ;',
            '\t\t:scenario = "rcp85" ;',
            '\t\t:Conventions = "CF-1.7" ;',
            "}",
        ]
    },
    "country": {
        "day": [
            "dimensions:",
            "\tensemble_member = 1 ;",
            "\ttime = 7200 ;",
            # "\ttime = 7305 ;",
            "\tregion = 8 ;",
            "\tbnds = 2 ;",
            "\tstring17 = 17 ;",
            "\tstring27 = 27 ;",
            "\tstring64 = 64 ;",
            "variables:",
            "\tint ensemble_member(ensemble_member) ;",
            '\t\tensemble_member:units = "1" ;',
            '\t\tensemble_member:long_name = "ensemble_member" ;',
            '\t\tensemble_member:_Storage = "contiguous" ;',
            '\t\tensemble_member:_Endianness = "little" ;',
            "\tdouble time(time) ;",
            '\t\ttime:axis = "T" ;',
            '\t\ttime:bounds = "time_bnds" ;',
            # '\t\ttime:units = "hours since 1970-01-01" ;',
            '\t\ttime:units = "hours since 1970-01-01 00:00:00" ;',
            '\t\ttime:standard_name = "time" ;',
            '\t\ttime:calendar = "360_day" ;',
            '\t\ttime:_Storage = "contiguous" ;',
            '\t\ttime:_Endianness = "little" ;',
            "\tdouble time_bnds(time, bnds) ;",
            '\t\ttime_bnds:_Storage = "contiguous" ;',
            '\t\ttime_bnds:_Endianness = "little" ;',
            "\tint region(region) ;",
            '\t\tregion:units = "1" ;',
            '\t\tregion:standard_name = "region" ;',
            '\t\tregion:_Storage = "contiguous" ;',
            '\t\tregion:_Endianness = "little" ;',
            "\tchar geo_region(region, string17) ;",
            '\t\tgeo_region:units = "1" ;',
            '\t\tgeo_region:long_name = "Country" ;',
            '\t\tgeo_region:_Storage = "contiguous" ;',
            "\tchar ensemble_member_id(ensemble_member, string27) ;",
            '\t\tensemble_member_id:units = "1" ;',
            '\t\tensemble_member_id:long_name = "ensemble_member_id" ;',
            '\t\tensemble_member_id:_Storage = "contiguous" ;',
            "\tint month_number(time) ;",
            '\t\tmonth_number:units = "1" ;',
            '\t\tmonth_number:long_name = "month_number" ;',
            '\t\tmonth_number:_Storage = "contiguous" ;',
            '\t\tmonth_number:_Endianness = "little" ;',
            "\tint year(time) ;",
            '\t\tyear:units = "1" ;',
            '\t\tyear:long_name = "year" ;',
            '\t\tyear:_Storage = "contiguous" ;',
            '\t\tyear:_Endianness = "little" ;',
            "\tchar yyyymmdd(time, string64) ;",
            '\t\tyyyymmdd:units = "1" ;',
            '\t\tyyyymmdd:long_name = "yyyymmdd" ;',
            '\t\tyyyymmdd:_Storage = "contiguous" ;',
            "// global attributes:",
            '\t\t:collection = "land-cpm" ;',
            '\t\t:domain = "uk" ;',
            '\t\t:frequency = "day" ;',
            '\t\t:institution = "Met Office Hadley Centre (MOHC), FitzRoy Road, Exeter, Devon, '
            'EX1 3PB, UK." ;',
            '\t\t:institution_id = "MOHC" ;',
            '\t\t:project = "UKCP18" ;',
            '\t\t:references = "https://ukclimateprojections.metoffice.gov.uk" ;',
            '\t\t:resolution = "country" ;',
            '\t\t:scenario = "rcp85" ;',
            '\t\t:Conventions = "CF-1.7" ;',
            "}",
        ]
    },
    "region": {
        "day": [
            "dimensions:",
            "\tensemble_member = 1 ;",
            # "\ttime = 7305 ;",
            "\ttime = 7200 ;",
            "\tregion = 16 ;",
            "\tbnds = 2 ;",
            "\tstring20 = 20 ;",
            "\tstring27 = 27 ;",
            "\tstring64 = 64 ;",
            "variables:",
            "\tint ensemble_member(ensemble_member) ;",
            '\t\tensemble_member:units = "1" ;',
            '\t\tensemble_member:long_name = "ensemble_member" ;',
            '\t\tensemble_member:_Storage = "contiguous" ;',
            '\t\tensemble_member:_Endianness = "little" ;',
            "\tdouble time(time) ;",
            '\t\ttime:axis = "T" ;',
            '\t\ttime:bounds = "time_bnds" ;',
            # '\t\ttime:units = "hours since 1970-01-01" ;',
            '\t\ttime:units = "hours since 1970-01-01 00:00:00" ;',
            '\t\ttime:standard_name = "time" ;',
            '\t\ttime:calendar = "360_day" ;',
            '\t\ttime:_Storage = "contiguous" ;',
            '\t\ttime:_Endianness = "little" ;',
            "\tdouble time_bnds(time, bnds) ;",
            '\t\ttime_bnds:_Storage = "contiguous" ;',
            '\t\ttime_bnds:_Endianness = "little" ;',
            "\tint region(region) ;",
            '\t\tregion:units = "1" ;',
            '\t\tregion:standard_name = "region" ;',
            '\t\tregion:_Storage = "contiguous" ;',
            '\t\tregion:_Endianness = "little" ;',
            "\tchar geo_region(region, string20) ;",
            '\t\tgeo_region:units = "1" ;',
            '\t\tgeo_region:long_name = "Region" ;',
            '\t\tgeo_region:_Storage = "contiguous" ;',
            "\tchar ensemble_member_id(ensemble_member, string27) ;",
            '\t\tensemble_member_id:units = "1" ;',
            '\t\tensemble_member_id:long_name = "ensemble_member_id" ;',
            '\t\tensemble_member_id:_Storage = "contiguous" ;',
            "\tint month_number(time) ;",
            '\t\tmonth_number:units = "1" ;',
            '\t\tmonth_number:long_name = "month_number" ;',
            '\t\tmonth_number:_Storage = "contiguous" ;',
            '\t\tmonth_number:_Endianness = "little" ;',
            "\tint year(time) ;",
            '\t\tyear:units = "1" ;',
            '\t\tyear:long_name = "year" ;',
            '\t\tyear:_Storage = "contiguous" ;',
            '\t\tyear:_Endianness = "little" ;',
            "\tchar yyyymmdd(time, string64) ;",
            '\t\tyyyymmdd:units = "1" ;',
            '\t\tyyyymmdd:long_name = "yyyymmdd" ;',
            '\t\tyyyymmdd:_Storage = "contiguous" ;',
            "// global attributes:",
            '\t\t:collection = "land-cpm" ;',
            '\t\t:domain = "uk" ;',
            '\t\t:frequency = "day" ;',
            '\t\t:institution = "Met Office Hadley Centre (MOHC), FitzRoy Road, Exeter, Devon, '
            'EX1 3PB, UK." ;',
            '\t\t:institution_id = "MOHC" ;',
            '\t\t:project = "UKCP18" ;',
            '\t\t:references = "https://ukclimateprojections.metoffice.gov.uk" ;',
            '\t\t:resolution = "region" ;',
            '\t\t:scenario = "rcp85" ;',
            '\t\t:Conventions = "CF-1.7" ;',
            "}",
        ]
    },
    "river": {
        "day": [
            "dimensions:",
            "\tensemble_member = 1 ;",
            # "\ttime = 7305 ;",
            "\ttime = 7200 ;",
            "\tregion = 23 ;",
            "\tbnds = 2 ;",
            "\tstring21 = 21 ;",
            "\tstring27 = 27 ;",
            "\tstring64 = 64 ;",
            "variables:",
            "\tint ensemble_member(ensemble_member) ;",
            '\t\tensemble_member:units = "1" ;',
            '\t\tensemble_member:long_name = "ensemble_member" ;',
            '\t\tensemble_member:_Storage = "contiguous" ;',
            '\t\tensemble_member:_Endianness = "little" ;',
            "\tdouble time(time) ;",
            '\t\ttime:axis = "T" ;',
            '\t\ttime:bounds = "time_bnds" ;',
            # '\t\ttime:units = "hours since 1970-01-01" ;',
            '\t\ttime:units = "hours since 1970-01-01 00:00:00" ;',
            '\t\ttime:standard_name = "time" ;',
            # '\t\ttime:calendar = "standard" ;',
            '\t\ttime:calendar = "360_day" ;',
            '\t\ttime:_Storage = "contiguous" ;',
            '\t\ttime:_Endianness = "little" ;',
            "\tdouble time_bnds(time, bnds) ;",
            '\t\ttime_bnds:_Storage = "contiguous" ;',
            '\t\ttime_bnds:_Endianness = "little" ;',
            "\tint region(region) ;",
            '\t\tregion:units = "1" ;',
            '\t\tregion:standard_name = "region" ;',
            '\t\tregion:_Storage = "contiguous" ;',
            '\t\tregion:_Endianness = "little" ;',
            "\tchar geo_region(region, string21) ;",
            '\t\tgeo_region:units = "1" ;',
            '\t\tgeo_region:long_name = "River" ;',
            '\t\tgeo_region:_Storage = "contiguous" ;',
            "\tchar ensemble_member_id(ensemble_member, string27) ;",
            '\t\tensemble_member_id:units = "1" ;',
            '\t\tensemble_member_id:long_name = "ensemble_member_id" ;',
            '\t\tensemble_member_id:_Storage = "contiguous" ;',
            "\tint month_number(time) ;",
            '\t\tmonth_number:units = "1" ;',
            '\t\tmonth_number:long_name = "month_number" ;',
            '\t\tmonth_number:_Storage = "contiguous" ;',
            '\t\tmonth_number:_Endianness = "little" ;',
            "\tint year(time) ;",
            '\t\tyear:units = "1" ;',
            '\t\tyear:long_name = "year" ;',
            '\t\tyear:_Storage = "contiguous" ;',
            '\t\tyear:_Endianness = "little" ;',
            "\tchar yyyymmdd(time, string64) ;",
            '\t\tyyyymmdd:units = "1" ;',
            '\t\tyyyymmdd:long_name = "yyyymmdd" ;',
            '\t\tyyyymmdd:_Storage = "contiguous" ;',
            "// global attributes:",
            '\t\t:collection = "land-cpm" ;',
            '\t\t:domain = "uk" ;',
            '\t\t:frequency = "day" ;',
            '\t\t:institution = "Met Office Hadley Centre (MOHC), FitzRoy Road, Exeter, Devon, '
            'EX1 3PB, UK." ;',
            '\t\t:institution_id = "MOHC" ;',
            '\t\t:project = "UKCP18" ;',
            '\t\t:references = "https://ukclimateprojections.metoffice.gov.uk" ;',
            '\t\t:resolution = "river" ;',
            '\t\t:scenario = "rcp85" ;',
            '\t\t:Conventions = "CF-1.7" ;',
            "}",
        ]
    },
}


def file_selector(
    areas_of_interest,
    ensembles_of_interest,
    file_path_template,
    variables_of_interest,
    version_no,
):
    """
    @param areas_of_interest[str], a list of areas to check
    @param ensembles_of_interest[str], a list of ensembles to check
    @param file_path_template str, a template to be used to find files
    @param variables_of_interest[str], a list of variables to check
    @param version_no str, the version number in the path

    """
    for area in areas_of_interest:
        for variable in variables_of_interest:
            for period in PERIODS:
                sample_headers = SAMPLE_HEADERS[area][period]
                index = 9
                try:
                    if area == "5km":
                        headers = VARIABLE_HEADERS_GRID[variable]
                    else:
                        headers = VARIABLE_HEADERS[variable]
                except KeyError:
                    print(
                        f"Sorry we do not have data to compare against for {variable} {area} data "
                        "yet"
                    )
                    sys.exit(1)

                for item in headers:
                    sample_headers.insert(index, item)
                    index += 1

                for ensemble in ensembles_of_interest:
                    file_path = file_path_template.format(
                        area=area,
                        ensemble=ensemble,
                        variable=variable,
                        period=period,
                        version=version_no,
                    )
                    _process_file_path(file_path, sample_headers)


def _process_file_path(file_path, sample_headers):
    file_list = glob.glob(file_path, recursive=True)
    print(f"Checking {len(file_list)} files from {file_path}")

    count = 0
    for file in file_list:
        result = []
        file_header = (
            subprocess.run(
                [NCDUMP, "-hs", file],
                stdout=subprocess.PIPE,
                check=False,
            )
            .stdout.decode("utf-8")
            .split("\n")
        )

        # Get a list of headers from the file and remove any that are in IGNORE_HEADERS
        for line in file_header:
            ignore = False
            for term in IGNORE_HEADERS:
                if term in line:
                    ignore = True
                    break
            if line == "":
                ignore = True
            if ignore:
                # don't add this line
                continue

            result.append(line)

        if result != sample_headers:
            count += 1
            print()
            print(
                f"Difference found in: {file}\nSee below for difference to expected values"
            )

            diff = difflib.context_diff(result, sample_headers, n=1)
            for line in diff:
                print(line)

    print(
        f"Finished checking {len(file_list)} files from {file_path}, differences found in {count} "
        "files"
    )


def _parse_command_line(argv):
    parser = ArgumentParser(
        description="Check the header information in NetCDF files for CPM data.",
        epilog="\n\nThe process checks the headers in NetCDF files. Currently this only works "
        "for only daily CPM data."
        f"\n\nThe following headers are not checked:\n{', '.join(IGNORE_HEADERS)}"
        "\n\nThe checks can be limited to an individual variable and/or area."
        "\n\nBy default the data is expected to be found under the directory "
        f"{PRE_PROD}/ukcp18/data. If it is in a different location then this can be overridden "
        "with the value provided by the --base_directory argument\n"
        "\n\nExample usage:"
        "\npython compare_cpm_netcdf_headers.py -a 5km -b /my/home/dir/ukcp -n wsgmax10m -v v20220131"
        "\n\n",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-a",
        "--area",
        help="If set then only check this area. "
        f"Valid values are: {', '.join(CPM_AREAS)}",
    )
    parser.add_argument(
        "-b",
        "--base_directory",
        help="If set then use this as the base directory. "
        f"This will have the path '{CPM_TEMPLATE}' appended to it",
    )
    parser.add_argument(
        "-n",
        "--variable_name",
        help="If set then only check this variable. "
        f"Valid values are: {', '.join(VARIABLES)}",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="If set then use this version number. the default value is 'latest'",
    )
    parser.add_argument(
        "-i",
        "--ignore_cmip",
        help="Ignore the CMIP data when testing",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--production",
        help="Check the data in the production directories. If used then any value set for "
        "--base_directory will be ignored",
        action="store_true",
    )

    return parser.parse_args(argv[1:])


if __name__ == "__main__":
    args = _parse_command_line(sys.argv)

    # What areas are we checking?
    if args.area is not None:
        if args.area not in CPM_AREAS:
            print(f"{args.area} is not in {CPM_AREAS}")
            sys.exit(1)
        areas = [args.area]
    else:
        areas = CPM_AREAS

    # What is the file path template?
    if args.production:
        path_template = PRODUCTION_PATH_TEMPLATE
    elif args.base_directory is not None:
        base_directory = args.base_directory
        if base_directory.endswith("/"):
            base_directory = base_directory[:-1]
        path_template = base_directory + CPM_TEMPLATE
    else:
        path_template = PRE_PRODUCTION_PATH_TEMPLATE

    # What variables are we checking?
    if args.variable_name is not None:
        if args.variable_name not in VARIABLES:
            print(f"{args.variable} is not in {VARIABLES}")
            sys.exit(1)
        variables = [args.variable_name]
    else:
        variables = VARIABLES

    # What version are we checking
    if args.version is not None:
        version = args.version
    else:
        version = "latest"

    # What ensemble members are we checking
    if args.ignore_cmip:
        ensembles = ENSEMBLES
    else:
        ensembles = ENSEMBLES_INC_CMIP

    file_selector(areas, ensembles, path_template, variables, version)
