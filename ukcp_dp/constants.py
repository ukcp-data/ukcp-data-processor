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
    OVERLAY_PROBABILITY_LEVELS='overlay_probability_levels',
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
                            InputType.DATA_TYPE,
                            InputType.FONT_SIZE,
                            InputType.IMAGE_FORMAT,
                            InputType.IMAGE_SIZE,
                            InputType.LEGEND_POSITION,
                            InputType.OVERLAY_PROBABILITY_LEVELS,
                            InputType.SHOW_BOUNDARIES,
                            InputType.SPATIAL_REPRESENTATION,
                            InputType.TEMPORAL_AVERAGE_TYPE,
                            InputType.TIME_PERIOD,
                            InputType.YEAR,
                            InputType.YEAR_MINIMUM,
                            InputType.YEAR_MAXIMUM]

INPUT_TYPES_MULTI_VALUE = [InputType.ENSEMBLE,
                           InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS,
                           InputType.SCENARIO,
                           InputType.VARIABLE
                           ]

INPUT_TYPES = INPUT_TYPES_SINGLE_VALUE + INPUT_TYPES_MULTI_VALUE
INPUT_TYPES.append(InputType.AREA)

DATA_SELECTION_TYPES = [InputType.BASELINE,
                        InputType.DATA_SOURCE,
                        InputType.DATA_TYPE,
                        InputType.ENSEMBLE,
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

FONT_SIZE_SMALL = 4
FONT_SIZE_MEDIUM = 7
FONT_SIZE_LARGE = 10

# colours

ENSEMBLE_COLOURS = ['#000000', '#0032A0', '#C80000', '#00B478', '#E1C800']
ENSEMBLE_GREYSCALES = ['#000000', '#000000', '#000000', '#8C8C8C', '#8C8C8C']
ENSEMBLE_LOWLIGHT = '#8C8C8C'

PERCENTILE_LINE_COLOUR = '#000000'
PERCENTILE_FILL = '#DCDCDC'

SCENARIO_COLOURS = ['#000000', '#0032A0', '#C80000', '#00B478', '#E1C800']
SCENARIO_GREYSCALES = ['#000000', '#000000', '#000000', '#8C8C8C', '#8C8C8C']

CONTOUR_LINE = '#000000'
CONTOUR_FILL = ['#D3D3D3', '#9E9E9E', '#6C6C6C']

OVERLAY_COLOUR = 'black'
OVERLAY_LINE_WIDTH = 0.3

OVERLAY_ADMIN = ('/usr/local/cows_venv_py27/local_dists/ukcp-data-processor'
                 '/public/shapefiles/UK_Admin')
OVERLAY_COUNTRY = ('/usr/local/cows_venv_py27/local_dists/ukcp-data-processor'
                   '/public/shapefiles/BritishIsles')
OVERLAY_RIVER = ('/usr/local/cows_venv_py27/local_dists/ukcp-data-processor'
                 '/public/shapefiles/BritishIsles')

TEMP_ANOMS = ['tasAnom', 'tasmaxAnom', 'tasminAnom']

MONTHLY = 'mon'
SEASONAL = 'seas'
ANNUAL = 'ann'

DATA_SOURCE_PROB = 'land-prob'
DATA_SOURCE_PROB_MIN_YEAR = 1961
DATA_SOURCE_RCM = 'land-rcm'
DATA_SOURCE_RCM_MIN_YEAR = 1980

DATA_DIR = '/group_workspaces/jasmin2/ukcp18/sandpit/example_data/ukcp18/data'

# Plot types
PlotType = enum(CDF_PLOT='CDF_PLOT',
                JP_PLOT='JP_PLOT',
                PDF_PLOT='PDF_PLOT',
                PLUME_PLOT='PLUME_PLOT',
                POSTAGE_STAMP_MAPS='POSTAGE_STAMP_MAPS',
                THREE_MAPS='THREE_MAPS')
