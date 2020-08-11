import logging

import cf_units
import iris
import iris.coord_categorisation
from iris.exceptions import CoordinateNotFoundError
from ukcp_dp.constants import (
    COLLECTION_CPM,
    TemporalAverageType,
    COLLECTION_DERIVED,
    GWL,
)
from ukcp_dp.vocab_manager import get_months


LOG = logging.getLogger(__name__)


def get_anomaly(
    cube_climatology,
    cube_absoute,
    baseline,
    preferred_unit,
    scenario,
    temporal_average_type,
    time_period,
    collection,
):
    """
    Generate a cube containing the anomaly values.

    @param cube_climatology (iris.cube): a cube containing the climatology data
    @param cube_absoute (iris.cube): a cube containing the absolute data to be
        changed into anomalies
    @param baseline (str): the value to be used added as the baseline
        attribute to the resultant cube
    @param preferred_unit(str):
    @param scenario(str): the scenario
    @param temporal_average_type (TemporalAverageType): the temporal average
        type
    @param time_period(str): the name of a month or season or 'all'
    @param collection(str): the collection
    """
    if temporal_average_type == TemporalAverageType.MONTHLY:
        periods = _get_selected_month_numbers(time_period)
    elif temporal_average_type == TemporalAverageType.SEASONAL:
        periods = _get_selected_seasons(time_period)
    else:
        # annual
        periods = ["ann"]

    # generate the anomaly for each time period, i.e. month or season
    anomaly_cubes = iris.cube.CubeList()
    for period in periods:
        if temporal_average_type == TemporalAverageType.MONTHLY:
            constraint = iris.Constraint(month_number=period)

        elif temporal_average_type == TemporalAverageType.SEASONAL:
            constraint = iris.Constraint(season=period)

        else:
            # annual
            constraint = None

        if constraint is None:
            cube_absoute_period = cube_absoute
            cube_climatology_period = cube_climatology
        else:
            cube_absoute_period = cube_absoute.extract(constraint)
            cube_climatology_period = cube_climatology.extract(constraint)

        # we need to remove these so that we can subtract the cubes
        if temporal_average_type == TemporalAverageType.MONTHLY:
            try:
                cube_absoute_period.remove_coord("year")
            except iris.exceptions.CoordinateNotFoundError:
                pass
            if collection == COLLECTION_CPM:
                try:
                    cube_absoute_period.remove_coord("yyyymm")
                except iris.exceptions.CoordinateNotFoundError:
                    pass
                try:
                    cube_climatology_period.remove_coord("year")
                except iris.exceptions.CoordinateNotFoundError:
                    pass

        elif temporal_average_type == TemporalAverageType.SEASONAL:
            try:
                cube_absoute_period.remove_coord("month_number")
            except iris.exceptions.CoordinateNotFoundError:
                pass
            if collection == COLLECTION_CPM:
                try:
                    cube_absoute_period.remove_coord("season_year")
                except iris.exceptions.CoordinateNotFoundError:
                    pass

        if scenario in GWL:
            # We are calculating the anomalies for the GWL data from the GCM baseline
            # data. Unfortunately the lat and log are ever so slightly different, a
            # floating point issue.
            for param in ["latitude", "longitude"]:
                cube_absoute_period.remove_coord(param)
                cube_climatology_period.remove_coord(param)

        # now generate the anomaly
        cube_anomaly_period = _make_anomaly(
            cube_absoute_period, cube_climatology_period, preferred_unit
        )

        # we need to remove these so that we can concatenate the cubes
        if temporal_average_type == TemporalAverageType.MONTHLY:
            for coord in ["yyyymm", "month_number"]:
                try:
                    cube_anomaly_period.remove_coord(coord)
                except iris.exceptions.CoordinateNotFoundError:
                    pass

        elif temporal_average_type == TemporalAverageType.SEASONAL:
            for coord in ["year", "season"]:
                try:
                    cube_anomaly_period.remove_coord(coord)
                except iris.exceptions.CoordinateNotFoundError:
                    pass

        if time_period == "all":
            # At this point the cube will contain all of the values for a
            # specific month/season for the entire time range. We cannot
            # concatenate cubes of this type together so we have to split them
            # up so they can be concatenated later on.
            # At the same time we are promoting 'time' back to a coordinate
            for anomaly_slice in cube_anomaly_period.slices_over("time"):
                # Flip the coordinates around so when they are transposed after
                # 'time' is added they will be the right way round
                anomaly_slice.transpose()
                anomaly_cubes.append(iris.util.new_axis(anomaly_slice, "time"))
        else:
            anomaly_cubes.append(cube_anomaly_period)

    cube_anomaly = anomaly_cubes.concatenate_cube()

    if time_period == "all":
        # Put 'time' back in the correct place
        cube_anomaly.transpose()

    # add the aux coords back
    if temporal_average_type == TemporalAverageType.MONTHLY:
        try:
            iris.coord_categorisation.add_year(cube_anomaly, "time", name="year")
        except CoordinateNotFoundError:
            pass
        try:
            iris.coord_categorisation.add_month_number(
                cube_anomaly, "time", name="month_number"
            )
        except CoordinateNotFoundError:
            pass

    elif temporal_average_type == TemporalAverageType.SEASONAL:
        try:
            iris.coord_categorisation.add_year(cube_anomaly, "time", name="year")
        except CoordinateNotFoundError:
            pass
        try:
            iris.coord_categorisation.add_season_year(
                cube_anomaly, "time", name="season_year"
            )
        except CoordinateNotFoundError:
            pass
        try:
            iris.coord_categorisation.add_season(cube_anomaly, "time", name="season")
        except CoordinateNotFoundError:
            pass
        try:
            iris.coord_categorisation.add_month_number(
                cube_anomaly, "time", name="month_number"
            )
        except CoordinateNotFoundError:
            pass

    # add the attributes back in and add info about the baseline and
    # anomaly
    cube_anomaly.attributes = cube_absoute.attributes
    cube_anomaly.attributes["baseline_period"] = baseline
    cube_anomaly.attributes["anomaly_type"] = "relative_change"

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
    try:
        anomaly = datacube - reference_cube
    except Exception as ex:
        LOG.error("datacube\n%s", datacube)
        LOG.error("reference_cube\n%s", reference_cube)
        raise ex

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


def _get_selected_month_numbers(time_period):
    if time_period == "all":
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        return months
    for i, term in enumerate(get_months()):
        if term == time_period:
            # i is the index not the month number
            return [i + 1]


def _get_selected_seasons(time_period):
    if time_period == "all":
        seasons = ["djf", "mam", "jja", "son"]
        return seasons
    return [time_period]
