def enum(**named_values):
    return type('Enum', (), named_values)


InputType = enum(
    AREA='area_type',
    BASELINE='baseline',
    DATA_FORMAT='data_format',
    ENSEMBLE='ensemble',
    EXTRACT_PERCENTILES='extract_percentiles',
    DATA_SOURCE='data_source',
    FONT_SIZE='font_size',
    HIGHLIGHTED_ENSEMBLE_MEMBERS='highlighted_ensemble_members',
    IMAGE_FORMAT='image_format',
    IMAGE_SIZE='image_size',
    LEGEND_POSITION='legend_position',
    SCENARIO='scenario',
    SHOW_BOUNDARIES='show_boundaries',
    SHOW_PROBABILITY_LEVELS='show_probability_levels',
    SPATIAL_REPRESENTATION='spatial_representation',
    TEMPORAL_AVERAGE_TYPE='temporal_average_type',
    TIME_PERIOD='time_period',
    VARIABLE='variable',
    YEAR='year',
    YEAR_MINIMUM='year_minimum',
    YEAR_MAXIMUM='year_maximum'
)

INPUT_TYPES_SINGLE_VALUE = [InputType.BASELINE,
                            InputType.DATA_FORMAT,
                            InputType.DATA_SOURCE,
                            InputType.EXTRACT_PERCENTILES,
                            InputType.FONT_SIZE,
                            InputType.IMAGE_FORMAT,
                            InputType.IMAGE_SIZE,
                            InputType.LEGEND_POSITION,
                            InputType.SHOW_BOUNDARIES,
                            InputType.SHOW_PROBABILITY_LEVELS,
                            InputType.SCENARIO,
                            InputType.SPATIAL_REPRESENTATION,
                            InputType.TEMPORAL_AVERAGE_TYPE,
                            InputType.TIME_PERIOD,
                            InputType.VARIABLE,
                            InputType.YEAR,
                            InputType.YEAR_MINIMUM,
                            InputType.YEAR_MAXIMUM]

INPUT_TYPES_MULTI_VALUE = [InputType.ENSEMBLE,
                           InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS]

INPUT_TYPES = INPUT_TYPES_SINGLE_VALUE + INPUT_TYPES_MULTI_VALUE
INPUT_TYPES.append(InputType.AREA)

DATA_SELECTION_TYPES = [InputType.BASELINE,
                        InputType.DATA_SOURCE,
                        InputType.ENSEMBLE,
                        InputType.SHOW_PROBABILITY_LEVELS,
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

TEMP_ANOMS = ['tasAnom', 'tasmaxAnom', 'tasminAnom']

MONTHLY = 'mon'
SEASONAL = 'seas'
ANNUAL = 'ann'

DATA_SOURCE_PROB = 'land-prob'

DATA_DIR = '/group_workspaces/jasmin2/ukcp18/sandpit/example_data/ukcp18/data'

# Plot types
PlotType = enum(CDF_PLOT='CDF_PLOT',
                PDF_PLOT='PDF_PLOT',
                PLUME_PLOT='PLUME_PLOT',
                POSTAGE_STAMP_MAPS='POSTAGE_STAMP_MAPS',
                THREE_MAPS='THREE_MAPS')
