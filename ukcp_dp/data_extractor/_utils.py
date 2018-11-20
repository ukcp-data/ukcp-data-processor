# -*- coding: utf-8 -*-
import logging

import cf_units
import iris
import iris.coord_categorisation
from iris.exceptions import CoordinateNotFoundError
from ukcp_dp.constants import TemporalAverageType
from ukcp_dp.vocab_manager import get_months, get_seasons


log = logging.getLogger(__name__)


def get_anomaly(cube_baseline, cube_absoute, baseline, preferred_unit,
                temporal_average_type, time_period):
    """
    Generate a cube containing the anomaly values.

    @param cube_baseline (iris.cube): a cube containing the baseline data
    @param cube_absoute (iris.cube): a cube containing the absolute data to be
        changed into anomalies
    @param baseline (str): the value to be used added as the baseline
        attribute to the resultant cube
    @param preferred_unit(str):
    @param temporal_average_type (TemporalAverageType): the temporal average
        type
    @param time_period(str): the name of a month or season or 'all'
    """
    cube_climatology = _make_climatology(
        cube_baseline, temporal_average_type)

    if temporal_average_type == TemporalAverageType.MONTHLY:
        periods = _get_selected_month_numbers(time_period)
    elif temporal_average_type == TemporalAverageType.SEASONAL:
        periods = _get_selected_season_numbers(time_period)
    else:
        # TODO annual
        pass

    # generate the anomaly for each time period, i.e. month or season
    anomaly_cubes = iris.cube.CubeList()
    for period in periods:
        if temporal_average_type == TemporalAverageType.MONTHLY:
            constraint = iris.Constraint(month_number=period)

        elif temporal_average_type == TemporalAverageType.SEASONAL:
            constraint = iris.Constraint(season_number=period)

        else:
            # TODO annual
            pass

        cube_absoute_period = cube_absoute.extract(constraint)
        cube_climatology_period = cube_climatology.extract(constraint)

        cube_anomaly_period = _make_anomaly(
            cube_absoute_period, cube_climatology_period, preferred_unit)

        # we need to remove these so that we can concatenate the cubes
        for coord in ['month_number', 'yyyymm', 'year']:
            try:
                cube_anomaly_period.remove_coord(coord)
            except iris.exceptions.CoordinateNotFoundError:
                pass

        if time_period == 'all':
            # At this point the cube will contain all of the values for a
            # specific month/season for the entire time range. We cannot
            # concatenate cubes of this type together so we have to split them
            # up so they can be concatenated later on.
            # At the same time we are promoting 'time' back to a coordinate
            for anomaly_slice in cube_anomaly_period.slices_over('time'):
                anomaly_cubes.append(
                    iris.util.new_axis(anomaly_slice, 'time'))
        else:
            anomaly_cubes.append(cube_anomaly_period)

    cube_anomaly = anomaly_cubes.concatenate_cube()

    if time_period == 'all':
        # Put 'time' back in the correct place
        cube_anomaly.transpose()

    # add the aux coords back
    if temporal_average_type == TemporalAverageType.MONTHLY:
        try:
            iris.coord_categorisation.add_month_number(
                cube_anomaly, 'time', name='month_number')
        except CoordinateNotFoundError:
            pass
    elif temporal_average_type == TemporalAverageType.SEASONAL:
        # TODO
        try:
            iris.coord_categorisation.add_month_number(
                cube_anomaly, 'time', name='month_number')
        except CoordinateNotFoundError:
            pass
    else:
        pass
        # TODO annual ?

    try:
        iris.coord_categorisation.add_year(
            cube_anomaly, 'time', name='year')
    except CoordinateNotFoundError:
        pass

    # add the attributes back in and add info about the baseline and
    # anomaly
    cube_anomaly.attributes = cube_absoute.attributes
    cube_anomaly.attributes['baseline_period'] = baseline
    cube_anomaly.attributes['anomaly_type'] = 'relative_change'

    return cube_anomaly


def _make_anomaly(datacube, reference_cube, preferred_unit=None):
    """
    Calculate the anomaly (or bias) of acube with respect to a reference_cube.
    These must be compatible shapes, or it will fail.

    Not only that: they also can't have AuxCoords that differ in values
    (e.g. when using seasonal data, the time coord gets smooshed into an
     anonymous dimcoord along with things like season, season_year,
     forecast_period...
     If the data cover different time periods, then you'll need to do
     cube.remove_coord for time,season_year and forecast_period so that
     you've just got the season coord left)

    We might want to add some automatic processing to try
    to smooth over these sort of issues automatically in future...


    If the user sets the preferred_unit to be dimensionless
    (i.e.  preferred_unit.is_convertable(1) )
    then we take that to imply a request for RELATIVE anomalies,
    i.e. (x-μ)/μ instead of just x-μ   (where μ is the mean of x)
    This might be the case for precip, where we want anomalies in %.
    """
    # Actually calculating the anomalies is trivial:
    anomaly = datacube - reference_cube

    if preferred_unit is not None:
        if preferred_unit == cf_units.Unit("Celsius"):
            # Manually switch temperature anomaly units to °C,
            # to avoid errors later:
            # ΔT in K is the same as ΔT in °C,
            # so subtracting 273.15K when converting units would be very wrong!
            if anomaly.units == cf_units.Unit("Kelvin"):
                anomaly.units = cf_units.Unit("Celsius")

        if preferred_unit.is_convertible(1):

            # We've asked for RELATIVE anomalies,
            # i.e. (x-μ)/μ instead of just x-μ (where μ is the mean of x)
            # This might be the case for precip where we want anomalies in %.
            anomaly = anomaly / reference_cube

        # Now apply the unit change:
        anomaly.convert_units(preferred_unit)

    # The cube's names have been lost.
    # We copy over the standard name, and make a new long name.
    anomaly.standard_name = datacube.standard_name
    if datacube.long_name is not None:
        anomaly.long_name = datacube.long_name
    else:
        anomaly.long_name = datacube.standard_name

    # Append the name_tag to the long_name
    # (we'll do something different later probably!)
    anomaly.long_name += " anomaly"

    # We will want to include a new attribute 'climatology_baselne'
    # that describes the dates of the climatology in the reference_cube,
    # as a string like "yyyy-mm-dd yyyy-mm-dd"
    # Ideally we could just take this from the reference_cube,
    # so it should be made by a function called by make_climatology()...

    # We DON'T copy across the other attributes,
    # because we could be mixing data from different models/obs here.

    # We MIGHT want to copy across the cell_methods from the
    # original datacube though.

    return anomaly


def _make_climatology(acube, climtype):
    """
    Make a "climatology", i.e. a mean calculated over a long period of
    time.

    You can also do monthly or seasonal climatologies:
    climtype ("climatology type")  must be one of 'annual', 'seasonal',
    'monthly'. (actually, just starting with seas* or month* will do)

    Seasons and month categorical AuxCoords will be added if necessary

    In the case of seasonal/monthly climatologies,
    the resulting cube has an anonymous leading dimension (DimCoord),
    which is linked to time, year, and season or month & month_number
    AuxCoords.

    The climatology will be calculated over all timesteps in acube.

    """

    thiscube = acube
    operation = iris.analysis.MEAN

    if climtype == TemporalAverageType.SEASONAL:
        theseasons = ('djf', 'mam', 'jja', 'son')
        try:
            iris.coord_categorisation.add_season(thiscube, 'time',
                                                 name='season',
                                                 seasons=theseasons)
        except ValueError:
            pass

        # Now we are safe to aggregate:
        climatol = acube.aggregated_by('season', operation)
        # This is likely to result in an anonymous dimension
        # with time, season and season_year (and possibly other) aux coords.

        # It might be nice to have an option to automatically remove these,
        # and promote the season aux coord to the dim coord.
        # Promoting is easy
        # (http://scitools.org.uk/iris/docs/v1.9.0/html/iris/iris/util.html#iris.util.promote_aux_coord_to_dim_coord)
        # but it's probably a pain to get the list of other aux coords in that
        # dimension and remove them in a loop.
        # So, the user will have to do this themselves if required.

    elif climtype == TemporalAverageType.MONTHLY:
        try:
            iris.coord_categorisation.add_month_number(
                thiscube, 'time', name='month_number')
        except ValueError:
            pass

        # Now we are safe to aggregate:
        climatol = acube.aggregated_by('month_number', operation)
        # As with seasonal, this will result in an anonymous dim coord
        # covering time, month, month_number etc,
        # but in this case we'd want to retain BOTH month and month_number.
        # So it's even less clear how to automatically tidy in this case.

    elif climtype == TemporalAverageType.ANNUAL:
        # Now we are safe to aggregate -- actually, we want to COLLAPSE
        # over all time in this case!
        climatol = acube.collapsed('time', operation)

    else:
        raise UserWarning("Climate type (" + climtype +
                          ") not recognised! \n" +
                          "Use annual, seasonal or monthly.")

    return climatol


def _get_selected_month_numbers(time_period):
    if time_period == 'all':
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        return months
    for i, term in enumerate(get_months()):
        if term == time_period:
            # i is the index not the month number
            return [i + 1]


def _get_selected_season_numbers(time_period):
    if time_period == 'all':
        seasons = [1, 2, 3, 4]
        return seasons
    for i, term in enumerate(get_seasons()):
        if term == time_period:
            # i is the index not the season number
            return [i + 1]
