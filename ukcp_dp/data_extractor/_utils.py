# -*- coding: utf-8 -*-
import logging

import cf_units
import iris
import iris.coord_categorisation


log = logging.getLogger(__name__)


def make_anomaly(datacube, reference_cube, preferred_unit=None,
                 name_tag="anomaly"):
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


    The name_tag will be appended to the existing long/standard name
    in the long_name of the new cube.
    You probably want it to be "anomaly" or "bias".
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
    anomaly.long_name += " " + name_tag

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


def make_climatology(acube, timecoordname='time', year_range=None,
                     seasonyear_range=None,
                     climtype="annual", operation=iris.analysis.MEAN):
    """
    Make a "climatology", i.e. a statistic calculated over a long period of
    time.

    The obvious example is the long-term mean over many years,
    but you can provide any iris.analysis function as the "operation" argument,
    http://scitools.org.uk/iris/docs/latest/iris/iris/analysis.html

    You can also do monthly or seasonal climatologies:
    climtype ("climatology type")  must be one of 'annual', 'seasonal',
    'monthly'. (acutally, just starting with seas* or month* will do)

    Seasons and month categorical AuxCoords will be added if necessary
    (so if you want special season definitions, e.g. NDJ instead of DJF,
     you should add them yourself first!)

    In the case of seasonal/monthly climatologies,
    the resulting cube has an anonymous leading dimension (DimCoord),
    which is linked to time, year, and season or month & month_number
    AuxCoords.

    The climatology will be calculated over all timesteps in acube by default.
    Alternatively, you can provide a 2-element tuple/list to year_range,
    specifying the subset of years to include;
    an intermediate cube will be extracted covering that range.
    Note that the years selected will go from year_range[0] to year_range[1]
    INCLUSIVE.

    Alternatively, you can do the same thing to a season_year coordinate,
    by giving that 2-element tuple/list to the seasonyear_range argument
    instead. This means that Decembers will be kept with the subsequent year
    (e.g. Dec 1980 is in season_year 1981),
    which is what we usually want to do for UKCP18...

    """

    if year_range is not None:
        try:
            iris.coord_categorisation.add_year(
                acube, timecoordname, name="year")
        except ValueError:
            pass
        # Now extract the subset of years:
        year_constraint = iris.Constraint(
            year=lambda cell: year_range[0] <= cell <= year_range[1])
        thiscube = acube.extract(year_constraint)
    else:
        thiscube = acube

    if seasonyear_range is not None:
        try:
            iris.coord_categorisation.add_season_year(
                acube, timecoordname, name="season_year")
        except ValueError:
            pass
        # Now extract the subset of years:
        seasyear_constraint = iris.Constraint(
            season_year=lambda cell:
                seasonyear_range[0] <= cell <= seasonyear_range[1])
        thiscube = acube.extract(seasyear_constraint)
    else:
        thiscube = acube

    climtype = climtype.lower()
    if climtype.startswith("seas"):
        theseasons = ('djf', 'mam', 'jja', 'son')
        try:
            iris.coord_categorisation.add_season(thiscube, timecoordname,
                                                 name='season',
                                                 seasons=theseasons)
        except ValueError:
            pass

        # Because the mean of a mean is a mean, there isn't an issue if we've
        # requested means.
        # But if we've requested standard deviations for example,
        # we need to make sure we start with a seasonal-mean time series.
        if operation is not iris.analysis.MEAN:
            # The more general case: get the seasonal means first,
            # then perform the requested interannual aggregation for the
            # seasonal means.
            if not _is_seasonal(thiscube, timecoordname=timecoordname):
                log.debug("Calculating seasonal means prior to applying {} "
                          "interannually".format(operation.name()))
                seascube = _get_seasmean_timeseries(
                    thiscube, timecoordname=timecoordname,
                    theseasons=theseasons)
            else:
                seascube = thiscube
        else:
            seascube = thiscube

        # Now we are safe to aggregate:
        climatol = seascube.aggregated_by('season', operation)
        # This is likely to result in an anonymous dimension
        # with time, season and season_year (and possibly other) aux coords.

        # It might be nice to have an option to automatically remove these,
        # and promote the season aux coord to the dim coord.
        # Promoting is easy
        # (http://scitools.org.uk/iris/docs/v1.9.0/html/iris/iris/util.html#iris.util.promote_aux_coord_to_dim_coord)
        # but it's probably a pain to get the list of other aux coords in that
        # dimension and remove them in a loop.
        # So, the user will have to do this themselves if required.

    elif climtype.startswith("month"):
        try:
            iris.coord_categorisation.add_month(
                thiscube, timecoordname, name='month')
        except ValueError:
            pass
        try:
            iris.coord_categorisation.add_month_number(
                thiscube, timecoordname, name='month_number')
        except ValueError:
            pass

        # Because the mean of a mean is a mean, there isn't an issue if we've
        # requested means. But if we've requested standard deviations for
        # example,we need to make sure we start with a monthly-mean time
        # series.
        if operation is not iris.analysis.MEAN:
            # The more general case: get the monthly means first if necessary,
            # then perform the requested interannual aggregation for the
            # monthly means.
            if not _is_monthly(thiscube, timecoordname=timecoordname):
                log.debug("Calculating monthly means prior to applying  {} "
                          "interannually".format(operation.name()))
                moncube = _get_monthlymean_timeseries(
                    thiscube, timecoordname=timecoordname)
            else:
                log.debug("it's ok, data is already monthly")
                moncube = thiscube
        else:
            moncube = thiscube

        # Now we are safe to aggregate:
        climatol = moncube.aggregated_by('month_number', operation)
        # As with seasonal, this will result in an anonymous dim coord
        # covering time, month, month_number etc,
        # but in this case we'd want to retain BOTH month and month_number.
        # So it's even less clear how to automaticaly tidy in this case.

    elif climtype == "annual":
        # Because the mean of a mean is a mean, there isn't an issue if we've
        # requested means. But if we've requested standard deviations for
        # example, we need to make sure we start with an annual-mean time
        # series.
        if operation is not iris.analysis.MEAN:
            # The more general case: get the annual means first if necessary,
            # then perform the requested interannual aggregation for the annual
            # means.
            annlcube = _get_annlmean_timeseries(
                thiscube, timecoordname=timecoordname)
        else:
            annlcube = thiscube

        # Now we are safe to aggregate -- actually, we want to COLLAPSE
        # over all time in this case!
        climatol = annlcube.collapsed('time', operation)

    else:
        raise UserWarning("Climate type (" + climtype +
                          ") not recognised! \n" +
                          "Use annual, sesonal or monthly.")

    return climatol


def _get_annlmean_timeseries(acube, timecoordname="time"):
    """
    Handy function to get annual means each year.
    Note that a 'year' categorical AuxCoord will be added if necessary.
    """
    try:
        iris.coord_categorisation.add_year(acube, timecoordname, name="year")
    except ValueError:
        pass
    annlmeans = acube.aggregated_by('year', operation)
    return annlmeans


def _get_monthlymean_timeseries(acube, timecoordname="time"):
    """
    Handy function to get monthly means each year.

    Note that 'year' and 'month_number' categorical AuxCoords will be added if
    necessary.
    """
    try:
        iris.coord_categorisation.add_year(acube, timecoordname, name="year")
    except ValueError:
        pass

    try:
        iris.coord_categorisation.add_month_number(
            acube, timecoordname, name='month_number')
    except ValueError:
        pass

    moncube = acube.aggregated_by(['month_number', 'year'], iris.analysis.MEAN)
    return moncube


def _get_seasmean_timeseries(acube, timecoordname="time",
                             theseasons=('djf', 'mam', 'jja', 'son')):
    """
    Handy function to get seasonal means each year.
    Note that 'season' and 'season_year' categorical AuxCoords will be added if
    necessary.

    theseasons is an iterable giving a complete list of season names
    (see http://scitools.org.uk/iris/docs/latest/iris/iris/
        coord_categorisation.html#iris.coord_categorisation.add_season)
    """
    try:
        iris.coord_categorisation.add_season(acube, timecoordname,
                                             name='season',
                                             seasons=theseasons)
    except ValueError:
        pass

    try:
        iris.coord_categorisation.add_season_year(acube, timecoordname,
                                                  name='season_year',
                                                  seasons=theseasons)
    except ValueError:
        pass

    seascube = acube.aggregated_by(
        ["season", "season_year"], iris.analysis.MEAN)
    return seascube


def _is_n_monthly(acube, nmonths, timecoordname="time"):
    """
    Test if the time-resolution of acube's time coord
    is nmonths (e.g. monthly for nmonths=1, seasonal for nmonths=3)

    This will work for 360-day calendars,
    and really should work for real-world calendars.
    (but that hasn't been properly tested yet)
    """
    tcoord = acube.coord(timecoordname)

    # Get the time coord data as a date/datetime/mysterious object:
    # (if it's a 360-day calendar, then it's not a standard python
    #  date/datetime, but a mysterious "instance" object, although it behaves
    # like normal dates;
    #  I think this is a netcdftime.datetime object)
    t = cf_units.num2date(tcoord.points,
                          tcoord.units.name,
                          tcoord.units.calendar)
    t_first = t[0]
    t_next = t[1]

    oldmonth = t_first.month

    new_day = t_first.day
    new_month = ((oldmonth + nmonths) - 1) % 12 + 1
    new_year = t_first.year + (((oldmonth + nmonths) - 1) / 12)

    # Create a new object using the class constructor
    # of t_first's class
    # (could be a datetime.date, datetime.datetime, netcdftime.datetime, ...)
    newdate = t_first.__class__(new_year, new_month, new_day)

    # With netcdftime.datetime objects, you can't change the components:
    # newdate       = copy.copy(t_first)
    # newdate.month = ((oldmonth+nmonths)-1) % 12 +1
    # newdate.year  = t_first.year+( ((oldmonth+nmonths)-1) /12 )
    # newdate.day  = t_first.day    (don't need to change this)

    # After adding n months, is the result the same as the next date?
    is_nmonthly = t_next == newdate

    return is_nmonthly


def _is_monthly(acube, timecoordname="time"):
    """
    Convenience wrapper to is_n_monthly() for n=1,
    i.e. testing if acube contains monthly data.
    """
    return _is_n_monthly(acube, 1, timecoordname=timecoordname)


def _is_seasonal(acube, timecoordname="time"):
    """
    Convenience wrapper to is_n_monthly() for n=3,
    i.e. testing if acube contains seasonal data.
    """
    return _is_n_monthly(acube, 3, timecoordname=timecoordname)
