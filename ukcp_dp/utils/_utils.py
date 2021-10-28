"""
This module provides common functions.

"""
from ukcp_dp.constants import InputType
from ukcp_dp.utils import _standards_class as stds


def get_plot_settings(vocab, cmsize, fsize, var_id, extreme):
    """
    Get the plot settings based on the variable being plotted.

    @return a StandardMap object containing plot settings

    """
    # tas, tasmax, tasmin
    if "tas" in var_id:
        # Mean air temperature at 1.5m (C)
        # Maximum air temperature at 1.5m (C)
        # Minimum air temperature at 1.5m (C)
        if extreme is True:
            plot_settings = stds.UKCP_TEMP_EXTREME.copy()
        elif "Anom" in var_id:
            plot_settings = stds.UKCP_TEMP_ANOM.copy()
        else:
            plot_settings = stds.UKCP_TEMP.copy()

    elif "prsn" in var_id:
        # Snowfall Flux anomaly (%)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_SNOW_FLUX_ANOM.copy()
        else:
            plot_settings = stds.UKCP_SNOW_FLUX.copy()

    elif "snw" in var_id:
        # Surface snow amount anomaly (mm)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_SNOW_ANOM.copy()
        else:
            plot_settings = stds.UKCP_SNOW.copy()

    elif "pr1day" in var_id:
        # 1-day total precipitation (mm)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_1DAY_PRECIP_ANOM.copy()
        else:
            plot_settings = stds.UKCP_1DAY_PRECIP.copy()

    elif "pr5day" in var_id:
        # 5-day total precipitation (mm)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_5DAY_PRECIP_ANOM.copy()
        else:
            plot_settings = stds.UKCP_5DAY_PRECIP.copy()

    elif "pr" in var_id:
        # Precipitation rate (mm/day)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_PRECIP_ANOM.copy()
        else:
            plot_settings = stds.UKCP_PRECIP.copy()

    elif "sfcWind" in var_id or "wsgmax10m" in var_id:
        # Wind speed at 10m (m s-1)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_WIND_ANOM.copy()
        else:
            plot_settings = stds.UKCP_WIND.copy()

    elif "uas" in var_id:
        # Eastward wind at 10m (m s-1)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_WIND_EASTWARD_ANOM.copy()
        else:
            plot_settings = stds.UKCP_WIND_EASTWARD.copy()

    elif "vas" in var_id:
        # Northward wind at 10m (m s-1)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_WIND_NORTHWARD_ANOM.copy()
        else:
            plot_settings = stds.UKCP_WIND_NORTHWARD.copy()

    elif "clt" in var_id:
        # Total cloud (%)
        if "Anom" in var_id:
            # TODO check BIAS is the correct thing to use
            plot_settings = stds.UKCP_CLOUDFRAC_MONTHLY_BIAS.copy()
        else:
            plot_settings = stds.UKCP_CLOUDFRAC_MONTHLY.copy()

    elif "hurs" in var_id:
        # Relative humidity at 1.5m (%)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_RELATIVE_HUMIDITY_ANOM.copy()
        else:
            plot_settings = stds.UKCP_RELATIVE_HUMIDITY.copy()

    elif "huss" in var_id:
        # Specific humidity at 1.5m (1)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_SPECIFIC_HUMIDITY_ANOM.copy()
        else:
            plot_settings = stds.UKCP_SPECIFIC_HUMIDITY.copy()

    elif "psl" in var_id:
        # Sea level pressure (hPa)
        if "Anom" in var_id:
            plot_settings = stds.UKCP_PMSL_ANOM.copy()
        else:
            # TODO do we need a non-ANOM version?
            plot_settings = stds.UKCP_PMSL_ANOM.copy()

    elif "rainfall" in var_id:
        # Maximum 5-day accumulative rainfall (mm)
        plot_settings = stds.UKCP_RAINFALL.copy()

    elif "rls" in var_id:
        # Net Surface long wave flux (W m-2)
        if "Anom" in var_id:
            # TODO check BIAS is the correct thing to use
            plot_settings = stds.UKCP_LWRAD_NET_MONTHLY_BIAS.copy()
        else:
            plot_settings = stds.UKCP_LWRAD_NET_MONTHLY.copy()

    elif "rsds" in var_id:
        # Total downward shortwave flux anomaly (W m-2)
        if "Anom" in var_id:
            # TODO check BIAS is the correct thing to use
            plot_settings = stds.UKCP_SWRAD_DOWN_MONTHLY_BIAS.copy()
        else:
            plot_settings = stds.UKCP_SWRAD_DOWN_MONTHLY.copy()

    elif "rss" in var_id:
        # Net Surface short wave flux (W m-2)
        if "Anom" in var_id:
            # TODO check BIAS is the correct thing to use
            plot_settings = stds.UKCP_SWRAD_NET_MONTHLY_BIAS.copy()
        else:
            plot_settings = stds.UKCP_SWRAD_NET_MONTHLY.copy()

    else:
        plot_settings = stds.UKCPNEAT.copy()

    plot_settings.bar_orientation = "horizontal"

    plot_settings.default_barlabel = vocab.get_collection_term_label(
        InputType.VARIABLE, var_id
    )

    # remove coast line, it is added back later with any over layers
    plot_settings.coastlw = 0

    # remove country boarders, we may put them back later
    plot_settings.countrylcol = None

    # 100 dots per cm
    plot_settings.dpi = 100
    plot_settings.dpi_display = 100

    if cmsize == 900:
        # using 100 dpi set size to 900x600
        plot_settings.cmsize = [22.86, 15.24]
    elif cmsize == 1200:
        # using 100 dpi set size to 1200x800
        plot_settings.cmsize = [30.48, 20.32]
    elif cmsize == 2400:
        # using 100 dpi set size to 2400x1600
        plot_settings.cmsize = [60.96, 40.64]

    plot_settings.fsize = fsize

    return plot_settings


def get_baseline_range(baseline):
    """
    Get the start and end year for a baseline.

    @param baseline (str): the name of a baseline

    @return a tuple containing two ints representing the start and end years

    """
    if baseline == "b6190":
        return 1961, 1990
    if baseline == "b8100":
        return 1981, 2000
    if baseline == "b8110":
        return 1981, 2010
    return None


def get_spatial_resolution_m(cube):
    """
    Get the spatial resolution of the cube data in metres.

    For the model data we can get this from an attribute.
    For the land-obs we need to calculate it from the bounds.

    @param cube (Cube): an iris cube

    @return the spatial resolution of the cube data in metres

    """
    try:
        resolution = cube.attributes["resolution"]
        resolution = int(resolution.split("km")[0]) * 1000
    except KeyError:
        # work out the resolution from the bounds
        resolution = int(
            cube.coords("projection_y_coordinate")[0].bounds[1][0]
            - cube.coords("projection_y_coordinate")[0].bounds[0][0]
        )
    return resolution
