from os import path


def enum(**named_values):
    return type('Enum', (), named_values)


InputType = enum(
    AREA='area_type',
    BASELINE='baseline',
    COLOUR_MODE='colour_mode',
    CONVERT_TO_PERCENTILES='convert_to_percentiles',
    DATA_FORMAT='data_format',
    DATA_SOURCE='data_source',
    DATA_TYPE='data_type',
    ENSEMBLE='ensemble',
    FONT_SIZE='font_size',
    HIGHLIGHTED_ENSEMBLE_MEMBERS='highlighted_ensemble_members',
    IMAGE_FORMAT='image_format',
    IMAGE_SIZE='image_size',
    LEGEND_POSITION='legend_position',
    METHOD='method',
    ORDER_BY_MEAN='order_by_mean',
    OVERLAY_PROBABILITY_LEVELS='overlay_probability_levels',
    RANDOM_SAMPLING_COUNT='random_sampling_count',
    SAMPLING_METHOD='sampling_method',
    SAMPLING_ID='sampling_id',
    SAMPLING_SUBSET_COUNT='sampling_subset_count',
    SAMPLING_PERCENTILE_1='sampling_percentile_1',
    SAMPLING_PERCENTILE_2='sampling_percentile_2',
    SAMPLING_TEMPORAL_AVERAGE_1='sampling_temporal_average_1',
    SAMPLING_TEMPORAL_AVERAGE_2='sampling_temporal_average_2',
    SAMPLING_VARIABLE_1='sampling_variable_1',
    SAMPLING_VARIABLE_2='sampling_variable_2',
    SCENARIO='scenario',
    SHOW_BOUNDARIES='show_boundaries',
    SPATIAL_REPRESENTATION='spatial_representation',
    TEMPORAL_AVERAGE_TYPE='temporal_average_type',
    TIME_PERIOD='time_period',
    VARIABLE='variable',
    YEAR='year',
    YEAR_MINIMUM='year_minimum',
    YEAR_MAXIMUM='year_maximum'
)

INPUT_TYPES_SINGLE_VALUE = [InputType.BASELINE,
                            InputType.COLOUR_MODE,
                            InputType.CONVERT_TO_PERCENTILES,
                            InputType.DATA_FORMAT,
                            InputType.DATA_SOURCE,
                            InputType.FONT_SIZE,
                            InputType.IMAGE_FORMAT,
                            InputType.IMAGE_SIZE,
                            InputType.LEGEND_POSITION,
                            InputType.METHOD,
                            InputType.ORDER_BY_MEAN,
                            InputType.OVERLAY_PROBABILITY_LEVELS,
                            InputType.RANDOM_SAMPLING_COUNT,
                            InputType.SAMPLING_METHOD,
                            InputType.SAMPLING_SUBSET_COUNT,
                            InputType.SAMPLING_PERCENTILE_1,
                            InputType.SAMPLING_PERCENTILE_2,
                            InputType.SAMPLING_TEMPORAL_AVERAGE_1,
                            InputType.SAMPLING_TEMPORAL_AVERAGE_2,
                            InputType.SAMPLING_VARIABLE_1,
                            InputType.SAMPLING_VARIABLE_2,
                            InputType.SHOW_BOUNDARIES,
                            InputType.SPATIAL_REPRESENTATION,
                            InputType.TEMPORAL_AVERAGE_TYPE,
                            InputType.TIME_PERIOD,
                            InputType.YEAR,
                            InputType.YEAR_MINIMUM,
                            InputType.YEAR_MAXIMUM]

INPUT_TYPES_MULTI_VALUE = [InputType.DATA_TYPE,
                           InputType.ENSEMBLE,
                           InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS,
                           InputType.SAMPLING_ID,
                           InputType.SCENARIO,
                           InputType.VARIABLE
                           ]

INPUT_TYPES = INPUT_TYPES_SINGLE_VALUE + INPUT_TYPES_MULTI_VALUE
INPUT_TYPES.append(InputType.AREA)

DATA_SELECTION_TYPES = [InputType.BASELINE,
                        InputType.DATA_SOURCE,
                        InputType.DATA_TYPE,
                        InputType.ENSEMBLE,
                        InputType.METHOD,
                        InputType.OVERLAY_PROBABILITY_LEVELS,
                        InputType.SCENARIO,
                        InputType.SPATIAL_REPRESENTATION,
                        InputType.TEMPORAL_AVERAGE_TYPE,
                        InputType.TIME_PERIOD,
                        InputType.VARIABLE,
                        InputType.YEAR,
                        InputType.YEAR_MINIMUM,
                        InputType.YEAR_MAXIMUM
                        ]

FONT_SIZE_SMALL = 6
FONT_SIZE_MEDIUM = 9
FONT_SIZE_LARGE = 14

# colours

ENSEMBLE_COLOURS = ['#000000', '#0032A0', '#C80000', '#00B478', '#E1C800']
ENSEMBLE_GREYSCALES = ['#000000', '#000000', '#000000', '#8C8C8C', '#8C8C8C']
ENSEMBLE_LOWLIGHT = '#8C8C8C'

PERCENTILE_LINE_COLOUR = '#000000'
PERCENTILE_FILL = '#DCDCDC'

SCENARIO_COLOURS = {'rcp26': ['#0032A0', 'solid'],
                    'rcp45': ['#00B478', 'solid'],
                    'rcp60': ['#E1C800', 'solid'],
                    'rcp85': ['#C80000', 'solid'],
                    'sres-a1b': ['#000000', 'solid']
                    }
SCENARIO_GREYSCALES = {'rcp26': ['#8C8C8C', 'dashed'],
                       'rcp45': ['#8C8C8C', 'solid'],
                       'rcp60': ['#000000', 'dotted'],
                       'rcp85': ['#000000', 'dashed'],
                       'sres-a1b': ['#000000', 'solid']
                       }
CONTOUR_LINE = '#000000'
CONTOUR_FILL = ['#D3D3D3', '#9E9E9E', '#6C6C6C']

OVERLAY_COLOUR = 'black'
OVERLAY_LINE_WIDTH = 0.3

ROOT_DIR = '/usr/local/cows_venv_py27/cows_venv/lib/python2.7/site-packages'

OVERLAY_ADMIN = path.join(ROOT_DIR, 'ukcp_dp/public/shapefiles/UK_Admin')
OVERLAY_COASTLINE = path.join(
    ROOT_DIR, 'ukcp_dp/public/shapefiles/UKCoastline')
OVERLAY_COASTLINE_SMALL = path.join(
    ROOT_DIR, 'ukcp_dp/public/shapefiles/UKCoastlineSmall')
OVERLAY_COUNTRY = path.join(ROOT_DIR, 'ukcp_dp/public/shapefiles/UK')
OVERLAY_RIVER = path.join(ROOT_DIR, 'ukcp_dp/public/shapefiles/river_basins')

LOGO_SMALL = path.join(
    ROOT_DIR,
    'ukcp_dp/public/img/MOHC_MASTER_black_mono_for_light_backg_RBG_100.jpg')
LOGO_MEDIUM = path.join(
    ROOT_DIR,
    'ukcp_dp/public/img/MOHC_MASTER_black_mono_for_light_backg_RBG_150.jpg')
LOGO_LARGE = path.join(
    ROOT_DIR,
    'ukcp_dp/public/img/MOHC_MASTER_black_mono_for_light_backg_RBG_300.jpg')

TEMP_ANOMS = ['tasAnom', 'tasmaxAnom', 'tasminAnom']

DATA_SOURCE_PROB = 'land-prob'
DATA_SOURCE_PROB_MIN_YEAR = 1961
DATA_SOURCE_GCM = 'land-gcm'
DATA_SOURCE_RCM = 'land-rcm'
DATA_SOURCE_RCM_MIN_YEAR = 1980
DATA_SOURCE_MARINE = 'marine-sim'
DATA_SOURCE_MARINE_MIN_YEAR = 2007
DATA_SOURCE_MARINE_MAX_YEAR = 2300
OTHER_MAX_YEAR = 2100

METHOD_EXPLORATORY = 'exploratory'

CDF_LABEL = 'Probability of being less than (%)'
PDF_LABEL = 'Relative probability'

DATA_DIR = '/group_workspaces/jasmin2/ukcp18/sandpit/example_data/ukcp18/data'

# A list of anomaly variables whose values are represented as percentages
PERCENTAGE_ANOMALIES = ['hussAnom', 'prAnom', 'rain5DayAccumMaxAnom',
                        'petAnom']

# Area types
AreaType = enum(ADMIN_REGION='admin_region',
                BBOX='bbox',
                COAST_POINT='coast_point',
                COUNTRY='country',
                GAUGE_POINT='gauge_point',
                POINT='point',
                RIVER_BASIN='river_basin')

# Plot types
PlotType = enum(CDF_PLOT='CDF_PLOT',
                JP_PLOT='JP_PLOT',
                PDF_PLOT='PDF_PLOT',
                PLUME_PLOT='PLUME_PLOT',
                POSTAGE_STAMP_MAPS='POSTAGE_STAMP_MAPS',
                THREE_MAPS='THREE_MAPS')

# Data formats
DataFormat = enum(CSV='csv',
                  NET_CDF='netcdf')

# Data types
DataType = enum(CDF='cdf',
                PDF='pdf')

# Image formats
ImageFormat = enum(JPG='jpg',
                   PDF='pdf',
                   PNG='png')

# Temporal average types
TemporalAverageType = enum(MONTHLY='mon',
                           SEASONAL='seas',
                           ANNUAL='ann')
