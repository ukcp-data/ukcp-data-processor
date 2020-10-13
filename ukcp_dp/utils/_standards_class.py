import copy

import cartopy.crs as ccrs
import cf_units
from ukcp_dp.constants import DPI_DISPLAY, DPI_SAVING, REG_BI_FULL, UKCP_OSGB


class StandardMap:
    """
    """

    def __init__(
        self,
        tag,
        cont=False,
        vrange=[-1, 1],
        vstep=0.2,
        vmid=None,
        cpal="RdBu_r",
        bar_orientation="horizontal",
        extendcolbar="both",
        bar_position=None,
        bar_tick_spacing=1,
        maskcol=(1, 1, 1, 1),
        undercol="magenta",
        overcol="yellow",
        figbackgroundcol=(1, 1, 1, 1),
        cmsize=[23, 18],
        dpi=DPI_SAVING,
        dpi_display=DPI_DISPLAY,
        fsize=12,
        fontfam="Arial",
        proj=ccrs.PlateCarree(),
        marlft=0.03,
        marrgt=0.97,
        martop=0.96,
        marbot=0.06,
        marwsp=0,
        marhsp=0,
        contlines=None,
        contlinealpha=1,
        contlinew=1,
        contlinecol="yellow",
        countrylw=1,
        countrylcol="grey",
        regionlw=1,
        regionlcol=None,
        riverslw=1,
        riverslcol=None,
        coastlw=1,
        coastlcol="black",
        gridlw=0.5,
        gridlcol="grey",
        gridlsty=":",
        default_barlabel="Unknown",
        preferred_unit=None,
        xlims=None,
        ylims=None,
        showglobal=False,
        xlims_for_grid=None,
        ylims_for_grid=None,
        dxgrid=5,
        dygrid=5,
        xgridax=[True, False],
        ygridax=[True, False],
    ):
        """
        tag could be used in filenames and printing to screen,
        so you'd usually set it to be the same as the object name,
        but as you can have different pointers to the same object
        it should have its own name stored here.

        Reasonable defaults are set for all options
        so that when making a new object
        you only have to change the things that are different.
        These aren't "recommended" options!
        They are just defaults that will allow it to run.
        """
        self.tag = tag  # Brief name of the object
        # plot as [filled] contours (True), or pixels (False)?
        self.cont = cont

        # value range: [min,max]
        self.vrange = vrange
        # value step
        self.vstep = vstep
        # value midpoint (for when using a diverging colour palette)
        self.vmid = vmid
        # colour palette name,
        self.cpal = cpal
        #                                           http://matplotlib.org/examples/color/colormaps_reference.html
        # Default colour-bar label string
        self.default_barlabel = default_barlabel
        # Colour-bar orientation: "horizontal","vertical", "none"
        self.bar_orientation = bar_orientation
        # Position of the colour-bar Axes: [left,bottom, width,height]
        self.bar_position = bar_position
        # spacing of labels in color bar
        self.bar_tick_spacing = bar_tick_spacing
        # Extend the colour bar? 'neither', 'min', 'max', 'both'
        self.extendcolbar = extendcolbar
        # Colour to use for masked areas
        self.maskcol = maskcol
        # Colour to use for values below the minimum
        self.undercol = undercol
        # Colour to use for values above the maximum
        self.overcol = overcol
        # Colour to use for the Figure object background
        self.figbackgroundcol = figbackgroundcol
        # Size in cm of the Figure, as a tuple/list: (width,height)
        self.cmsize = cmsize
        # Resolution of the Figure when displaying on screen, in dots per inch
        self.dpi_display = dpi_display
        # Resolution of the Figure when saving, in dots per inch
        self.dpi = dpi
        # Font size, in points
        self.fsize = fsize
        # Font family name
        self.fontfam = fontfam
        # Map projection: should be a Cartopy CRS object
        self.proj = proj

        # For the margins, if all 4 are set to None then tight_layout() is used
        # instead.
        # Left margin
        self.marlft = marlft
        # Right margin
        self.marrgt = marrgt
        # Top margin
        self.martop = martop
        # Bottom margin
        self.marbot = marbot
        # Width spacing between subplots
        self.marwsp = marwsp
        # Height spacing between subplots
        self.marhsp = marhsp

        # Grid line width
        self.gridlw = gridlw
        # Grid line colour
        self.gridlcol = gridlcol
        # Grid line style
        self.gridlsty = gridlsty

        # Values at which to plot additional contours
        self.contlines = contlines
        # Contour line width
        self.contlinew = contlinew
        # Contour line colour
        self.contlinecol = contlinecol
        # Contour line alpha (transparency)
        self.contlinealpha = contlinealpha

        # Country borders line width
        self.countrylw = countrylw
        # Country borders line colour (omit if None)
        self.countrylcol = countrylcol
        # This uses the international borders from Natural Earth.

        # Subnational region line width
        self.regionlw = regionlw
        # Subnational region line colour (omit if None)
        self.regionlcol = regionlcol
        # This uses subnational regions from Natural Earth, and probably
        # shouldn't be used.

        # The coastline and rivers are also from Natural Earth:
        # Coastline width
        self.coastlw = coastlw
        # Coastline colour (omit if None)
        self.coastlcol = coastlcol
        # Rivers line width
        self.riverslw = riverslw
        # Rivers line colour (omit if None)
        self.riverslcol = riverslcol

        # Preferred unit to convert the data into
        self.preferred_unit = preferred_unit

        # x-axis limits [min,max]  (often longitude)
        self.xlims = xlims
        # y-axis limits [min,max]  (often latitude)
        self.ylims = ylims
        # True/False to force showing the whole globe
        self.showglobal = showglobal
        # grid spacing in the x direction
        self.dxgrid = dxgrid
        # grid spacing in the y direction
        self.dygrid = dygrid
        # x-axis limits for plotting gridlines [min,max]
        self.xlims_for_grid = xlims_for_grid
        # y-axis limits for plotting gridlines [min,max]
        self.ylims_for_grid = ylims_for_grid
        # True/False switches for axis labels: [left-axis, right-axis]
        self.xgridax = xgridax
        # True/False switches for axis labels: [bottom-axis, top-axis]
        self.ygridax = ygridax

    # ==== METHODS =============================

    def copy(self):
        """
        Handy copy method.
        Use this to prevent accidentally
        editing an old/existing object!
        """
        return copy.copy(self)

    def set_xylims(self, reg_dict):
        """
        Convenience function to set xlims and ylims
        from a region dictionary (as used in ukcp_common_analysis.regions)
        """
        self.xlims = reg_dict["lons"]
        self.ylims = reg_dict["lats"]

    def set_margins(
        self, left=None, right=None, bottom=None, top=None, wspace=None, hspace=None
    ):
        """
        Convenience function to set margin components.
        Arguments are optional, so you can just set the one(s) you want.
        """
        if left is not None:
            self.marlft = left
        if right is not None:
            self.marrgt = right
        if bottom is not None:
            self.marbot = bottom
        if top is not None:
            self.martop = top
        if wspace is not None:
            self.marwsp = wspace
        if hspace is not None:
            self.marhsp = hspace

    def __str__(self):
        """
        Provide a descriptive string representation of the object:
        """
        thestr = ""
        thestr += "StandardMap object:" + self.tag + "\n"
        thestr += "  Plot as filled contours? cont = " + str(self.cont) + "\n"
        thestr += "  Value range:          vrange = " + str(self.vrange) + "\n"
        thestr += "  Value step:           vstep  = " + str(self.vstep) + "\n"
        thestr += "  Value divergence point  vmid = " + str(self.vmid) + "\n"
        thestr += "  Colour palette name:    cpal = " + self.cpal + "\n"
        thestr += (
            "  Default colour bar label: default_barlabel = "
            + str(self.default_barlabel)
            + "\n"
        )
        thestr += (
            "  Preferred unit for data: preferred_unit = "
            + str(self.preferred_unit)
            + "\n"
        )
        thestr += (
            "  Colour bar orientation: bar_orientation = "
            + str(self.bar_orientation)
            + "\n"
        )
        thestr += (
            "  Colour bar tick spacing: bar_tick_spacing  = "
            + str(self.bar_tick_spacing)
            + "\n"
        )
        thestr += (
            "  Colour bar explicit position [l,b,w,h]: = "
            + str(self.bar_position)
            + "\n"
        )
        thestr += (
            "  Extend the colour bar?     extendcolbar = " + self.extendcolbar + "\n"
        )
        thestr += (
            "  Colour for masked/blank areas: maskcol   = " + str(self.maskcol) + "\n"
        )
        thestr += "  Colour for underflow: undercol = " + str(self.undercol) + "\n"
        thestr += "  Colour for overflow:  overcol  = " + str(self.overcol) + "\n"
        thestr += (
            "  Colour for Figure background: figbackgroundcol = "
            + str(self.figbackgroundcol)
            + "\n"
        )
        thestr += (
            "  Figure size (cm):    cmsize      = ["
            + str(self.cmsize[0])
            + ","
            + str(self.cmsize[1])
            + "]\n"
        )
        thestr += "  Figure DPI:          dpi         = " + str(self.dpi) + "\n"
        thestr += "  Onscreen figure DPI: dpi_display = " + str(self.dpi_display) + "\n"
        thestr += "  Figure font size:    fsize       = " + str(self.fsize) + "\n"
        thestr += "  Figure font family:  fontfam     = " + self.fontfam + "\n"
        thestr += "  Map projection object: proj = " + str(self.proj) + "\n"
        thestr += (
            "  Margins l/r: [marlft,marrgt] = "
            + str(self.marlft)
            + ","
            + str(self.marrgt)
            + "\n"
        )
        thestr += (
            "  Margins t/b: [martop,marbot] = "
            + str(self.martop)
            + ","
            + str(self.marbot)
            + "\n"
        )
        thestr += (
            "  Spacing w/h: [marwsp,marhsp] = "
            + str(self.marwsp)
            + ","
            + str(self.marhsp)
            + "\n"
        )

        if self.gridlcol is not None:
            thestr += "Will plot grid lines:\n"
            thestr += "  Grid line width:   gridlw   = " + str(self.gridlw) + "\n"
            thestr += "  Grid line style:   gridlsty = " + str(self.gridlsty) + "\n"
            thestr += "  Grid line colour:  gridlcol = " + str(self.gridlcol) + "\n"
            thestr += (
                "  Lon. limits for grid: xlims_for_grid = "
                + str(self.xlims_for_grid)
                + "\n"
            )
            thestr += (
                "  Lat. limits for grid: ylims_for_grid = "
                + str(self.ylims_for_grid)
                + "\n"
            )
            thestr += (
                "  Longitude grid lines every: dxgrid = " + str(self.dxgrid) + "\n"
            )
            thestr += (
                "  Latitude  grid lines every: dygrid = " + str(self.dygrid) + "\n"
            )
            thestr += (
                "  Longitude grid labels on [bottom,top]? xgridax = "
                + str(self.xgridax)
                + "\n"
            )
            thestr += (
                "  Latitude  grid labels on [left,right]? ygridax = "
                + str(self.ygridax)
                + "\n"
            )

        if self.contlines is not None:
            thestr += (
                "  Additional contour lines at:    contlines    = "
                + str(self.contlines)
                + "\n"
            )
            thestr += (
                "  Additional contour line colour: contlinecol  = "
                + str(self.contlinecol)
                + "\n"
            )
            thestr += (
                "  Additional contour line width:  contlinew    = "
                + str(self.contlinew)
                + "\n"
            )
            thestr += (
                "  Additional contour line alpha:  conlinealpha = "
                + str(self.contlinealpha)
                + "\n"
            )

        if self.countrylcol is not None:
            thestr += "Will plot countries:\n"
            thestr += (
                "  cartopy.feature.NaturalEarthFeature('cultural',"
                "'admin_0_boundary_lines_land','10m')\n"
            )
            thestr += (
                "  Country border colour: countrylcol = " + str(self.countrylcol) + "\n"
            )
            thestr += (
                "  Country border width:  countrylw   = " + str(self.countrylw) + "\n"
            )
        else:
            thestr += (
                "(not plotting cartopy.feature.NaturalEarthFeature " "countries)\n"
            )

        if self.regionlcol is not None:
            thestr += "Will plot subnational regions:"
            thestr += (
                "  cartopy.feature.NaturalEarthFeature('cultural',"
                "'admin_1_states_provinces_lines','10m')\n"
            )
            thestr += (
                "  Region border colour: regionlcol = " + str(self.regionlcol) + "\n"
            )
            thestr += (
                "  Region border width:  regionlw   = " + str(self.regionlw) + "\n"
            )
        else:
            thestr += (
                "(not plotting cartopy.feature.NaturalEarthFeature "
                "subnational regions)\n"
            )

        if self.riverslcol is not None:
            thestr += "Will plot rivers:\n"
            thestr += (
                "  cartopy.feature.NaturalEarthFeature('physical',"
                "'rivers_lake_centerlines','50m')\n"
            )
            thestr += (
                "  Rivers line colour: riverslcol = " + str(self.riverslcol) + "\n"
            )
            thestr += "  Rivers line width:  riverslw   = " + str(self.riverslw) + "\n"
        else:
            thestr += "(not plotting cartopy.feature.NaturalEarthFeature " "rivers)\n"

        thestr += "  Coastline width:   coastlw    = " + str(self.coastlw) + "\n"
        thestr += "  Coastline colour:  coastlcol  = " + str(self.coastlcol) + "\n"

        thestr += "  Longitude limits: xlims = " + str(self.xlims) + "\n"
        thestr += "  Latitude  limits: ylims = " + str(self.ylims) + "\n"
        thestr += (
            "  Force showing whole globe? showglobal = " + str(self.showglobal) + "\n"
        )

        return thestr

    def __repr__(self):
        """
        Ideally this should be a string representation that
        we can give to eval() to reconstruct the object...

        ... but that would be complicated and we're just
        returning self.__str__() instead.
        """
        return self.__str__()


# This object forms the basis of all the variable-specific objects below,
# and provides the figure size/proportions and margins:
UKCPNEAT = StandardMap(
    "UKCPneat",
    cont=False,
    vrange=[276, 288],
    vstep=1,
    vmid=None,
    cpal="YlOrRd",
    bar_orientation="vertical",
    extendcolbar="both",
    maskcol=(1, 1, 1, 1),
    undercol="magenta",
    overcol="green",
    figbackgroundcol=(1, 1, 1, 1),
    cmsize=[15.5, 17],
    dpi=DPI_SAVING,
    fsize=12,
    fontfam="Arial",
    proj=UKCP_OSGB,
    marlft=0.01,
    marrgt=1.00,
    martop=0.99,
    marbot=0.02,
    countrylw=1,
    countrylcol="grey",
    regionlw=0.3,
    regionlcol="black",
    coastlw=1,
    coastlcol="black",
    dxgrid=1,
    dygrid=1,
    xlims=REG_BI_FULL["lons"],
    ylims=REG_BI_FULL["lats"],
)
# Note that with these proportions, setting
#     marlft=None,marrgt=None,martop=None,marbot=None,
# and thus triggering tight_layout(),
# is fine, but actually results in slightly smaller plots,
# so we'll stick to specifying the margins here.


# ----------------- VARIABLE-SPECIFIC OBJECTS ---------------------------
# We may want different value ranges for daily/monthly/seasonal data?


# Air temperatures.
UKCP_TEMP = UKCPNEAT.copy()
UKCP_TEMP.tag = "UKCP_temp"
UKCP_TEMP.default_barlabel = "Temperature, $^\circ$C"
UKCP_TEMP.preferred_unit = cf_units.Unit("Celsius")
UKCP_TEMP.cpal = "RdBu_r"
UKCP_TEMP.undercol = "#aabbff"
UKCP_TEMP.overcol = "#440000"
UKCP_TEMP.vrange = [-4.0, 14.0]
UKCP_TEMP.vmid = 0.0
UKCP_TEMP.vstep = 2.0


# Temperature anomalies.
# (some would prefer temperature differences/changes to always
#  be in Kelvin rather than °Celsius. Sticking to °C is clearer though)
# NOTE though, that if you already have a temperature difference in Kelvin,
#      you DO NOT want to do a Cube.convert_units on it (subtracting off
#      273.15!) but instead just manually override the Cube.units with this
#      unit. This is done automatically in
#      ukcp_common_analysis.common_analysis.make_anomaly()
#      if the preferred_unit is set to the preferred_unit here.
UKCP_TEMP_ANOM = UKCP_TEMP.copy()
UKCP_TEMP_ANOM.tag = "UKCP_temp_anom"
UKCP_TEMP_ANOM.default_barlabel = "Temperature anomaly, $^\circ$C"
UKCP_TEMP_ANOM.preferred_unit = cf_units.Unit("Celsius")
UKCP_TEMP_ANOM.vrange = [-1, 8.0]
UKCP_TEMP_ANOM.vmid = 0.0
UKCP_TEMP_ANOM.vstep = 1.0


# Air temperatures specifically for use with the probabilistic extremes.
UKCP_TEMP_EXTREME = UKCP_TEMP.copy()
UKCP_TEMP_EXTREME.tag = "UKCP_temp_extreme"
UKCP_TEMP_EXTREME.default_barlabel = "Temperature, $^\circ$C"
UKCP_TEMP_EXTREME.preferred_unit = cf_units.Unit("Celsius")
UKCP_TEMP_EXTREME.undercol = "#fcd9c4"
UKCP_TEMP_EXTREME.overcol = "#440000"
UKCP_TEMP_EXTREME.vrange = [10.0, 40.0]
UKCP_TEMP_EXTREME.vmid = 0.0
UKCP_TEMP_EXTREME.vstep = 5.0


# Precipitation rate.
UKCP_PRECIP = UKCPNEAT.copy()
UKCP_PRECIP.tag = "UKCP_precip"
UKCP_PRECIP.default_barlabel = "Precipitation rate, mm day$^{-1}$"
# UKCP_PRECIP.default_barlabel = "Precipitation rate, mm/day"
UKCP_PRECIP.preferred_unit = cf_units.Unit("mm/day")
UKCP_PRECIP.extendcolbar = "max"
UKCP_PRECIP.cpal = "Blues"
UKCP_PRECIP.undercol = "#3a240b"
UKCP_PRECIP.overcol = "#09382e"
UKCP_PRECIP.vrange = [0.0, 8.0]
UKCP_PRECIP.vmid = None
UKCP_PRECIP.vstep = 1.0

# Precipitation rate anomalies
#   Note that this is in %, not mm/day!
#   This is done automatically in
#   ukcp_common_analysis.common_analysis.make_anomaly()
#   if the preferred_unit is set to the preferred_unit here.
UKCP_PRECIP_ANOM = UKCP_PRECIP.copy()
UKCP_PRECIP_ANOM.tag = "UKCP_precip_anom"
UKCP_PRECIP_ANOM.preferred_unit = cf_units.Unit("%")
UKCP_PRECIP_ANOM.default_barlabel = "Precipitation rate anomaly, %"
# UKCP_PRECIP_ANOM.default_barlabel = (
#    "Precipitation rate anomaly, mm day$^{-1}$")
# UKCP_PRECIP_ANOM.default_barlabel = "Precipitation rate anomaly, mm/day"
UKCP_PRECIP_ANOM.extendcolbar = "both"
UKCP_PRECIP_ANOM.cpal = "BrBG"
UKCP_PRECIP_ANOM.undercol = "#3a240b"
UKCP_PRECIP_ANOM.overcol = "#09382e"
UKCP_PRECIP_ANOM.vrange = [-80.0, 60.0]
UKCP_PRECIP_ANOM.vmid = 0.0
UKCP_PRECIP_ANOM.vstep = 10.0


# Snowfall flux at surface
UKCP_SNOW_FLUX = UKCPNEAT.copy()
UKCP_SNOW_FLUX.tag = "UKCP_snow_flux"
UKCP_SNOW_FLUX.default_barlabel = "Snowfall Flux, mm day$^{-1}$"
UKCP_SNOW_FLUX.preferred_unit = cf_units.Unit("mm/day")
UKCP_SNOW_FLUX.extendcolbar = "max"
UKCP_SNOW_FLUX.cpal = "PuOr"
UKCP_SNOW_FLUX.undercol = "#3a240b"
UKCP_SNOW_FLUX.overcol = "#240938"
UKCP_SNOW_FLUX.vrange = [0.0, 8.0]
UKCP_SNOW_FLUX.vmid = None
UKCP_SNOW_FLUX.vstep = 1.0

# Snowfall flux at surface anomalies
UKCP_SNOW_FLUX_ANOM = UKCP_SNOW_FLUX.copy()
UKCP_SNOW_FLUX_ANOM.tag = "UKCP_snow_flux_anom"
UKCP_SNOW_FLUX_ANOM.preferred_unit = cf_units.Unit("%")
UKCP_SNOW_FLUX_ANOM.default_barlabel = "Snowfall Flux anomaly, %"
UKCP_SNOW_FLUX_ANOM.extendcolbar = "both"
UKCP_SNOW_FLUX_ANOM.cpal = "PuOr"
UKCP_SNOW_FLUX_ANOM.vrange = [-100.0, 50.0]
UKCP_SNOW_FLUX_ANOM.vmid = 0.0
UKCP_SNOW_FLUX_ANOM.vstep = 10


# Amount of snow on the ground
UKCP_SNOW = UKCPNEAT.copy()
UKCP_SNOW.tag = "UKCP_snow"
UKCP_SNOW.default_barlabel = "Surface snow amount, mm"
UKCP_SNOW.preferred_unit = cf_units.Unit("mm")
UKCP_SNOW.extendcolbar = "max"
UKCP_SNOW.cpal = "PuOr"
UKCP_SNOW.undercol = "#492f0b"
UKCP_SNOW.overcol = "#240938"
UKCP_SNOW.vrange = [0.0, 8.0]
UKCP_SNOW.vmid = None
UKCP_SNOW.vstep = 1.0

# Amount of snow on the ground anomalies
UKCP_SNOW_ANOM = UKCP_SNOW.copy()
UKCP_SNOW_ANOM.tag = "UKCP_snow_anom"
UKCP_SNOW_ANOM.preferred_unit = cf_units.Unit("mm")
UKCP_SNOW_ANOM.default_barlabel = "Surface snow amount anomaly, mm"
UKCP_SNOW_ANOM.extendcolbar = "both"
UKCP_SNOW_ANOM.cpal = "PuOr"
UKCP_SNOW_ANOM.vrange = [-6.0, 2.0]
UKCP_SNOW_ANOM.vmid = 0.0
UKCP_SNOW_ANOM.vstep = 0.5


# Wind speed.
UKCP_WIND = UKCPNEAT.copy()
UKCP_WIND.tag = "UKCP_wind"
UKCP_WIND.default_barlabel = "Wind speed, m s$^{-1}$"
# UKCP_WIND.default_barlabel = "Wind speed, m/s$"
UKCP_WIND.preferred_unit = cf_units.Unit("m/s")
UKCP_WIND.extendcolbar = "max"
UKCP_WIND.cpal = "PiYG"
UKCP_WIND.vrange = [0.0, 15.0]
UKCP_WIND.vmid = None
UKCP_WIND.vstep = 2.0


# Wind speed anomalies.
UKCP_WIND_ANOM = UKCP_WIND.copy()
UKCP_WIND_ANOM.tag = "UKCP_wind_anom"
UKCP_WIND_ANOM.default_barlabel = "Wind speed anomaly, m s$^{-1}$"
# UKCP_WIND_ANOM.default_barlabel = "Wind speed anomaly, m/s$"
UKCP_WIND_ANOM.extendcolbar = "both"
UKCP_WIND_ANOM.cpal = "PiYG"
UKCP_WIND_ANOM.undercol = "#380935"
UKCP_WIND_ANOM.overcol = "#2f3809"
UKCP_WIND_ANOM.vrange = [-2.0, 2.0]
UKCP_WIND_ANOM.vmid = 0.0
UKCP_WIND_ANOM.vstep = 0.5


UKCP_WIND_EASTWARD = UKCP_WIND.copy()
UKCP_WIND_EASTWARD.tag = "UKCP_wind_eastwards"
UKCP_WIND_EASTWARD.default_barlabel = "Eastward wind component, m s$^{-1}$"

UKCP_WIND_NORTHWARD = UKCP_WIND.copy()
UKCP_WIND_NORTHWARD.tag = "UKCP_wind_northwards"
UKCP_WIND_NORTHWARD.default_barlabel = "Northward wind component, m s$^{-1}$"


UKCP_WIND_EASTWARD_ANOM = UKCP_WIND_ANOM.copy()
UKCP_WIND_EASTWARD_ANOM.tag = "UKCP_wind_eastwards"
UKCP_WIND_EASTWARD_ANOM.default_barlabel = "Eastward wind component, m s$^{-1}$"

UKCP_WIND_NORTHWARD_ANOM = UKCP_WIND_ANOM.copy()
UKCP_WIND_NORTHWARD_ANOM.tag = "UKCP_wind_northwards"
UKCP_WIND_NORTHWARD_ANOM.default_barlabel = "Northward wind component, m s$^{-1}$"


# Radiation variables.
# Shortwave, downwelling.
UKCP_SWRAD_DOWN_MONTHLY = UKCPNEAT.copy()
UKCP_SWRAD_DOWN_MONTHLY.tag = "UKCP_irradiance_swdown_"
UKCP_SWRAD_DOWN_MONTHLY.default_barlabel = (
    "Downwelling shortwave irradiance, W m$^{-2}$"
)
UKCP_SWRAD_DOWN_MONTHLY.preferred_unit = cf_units.Unit("W/m^2")
UKCP_SWRAD_DOWN_MONTHLY.extendcolbar = "max"
UKCP_SWRAD_DOWN_MONTHLY.cpal = "PuOr"
UKCP_SWRAD_DOWN_MONTHLY.undercol = "#492f0b"
UKCP_SWRAD_DOWN_MONTHLY.overcol = "#240938"
UKCP_SWRAD_DOWN_MONTHLY.vrange = [0.0, 350.0]
UKCP_SWRAD_DOWN_MONTHLY.vmid = None
UKCP_SWRAD_DOWN_MONTHLY.vstep = 50.0

UKCP_SWRAD_DOWN_MONTHLY_BIAS = UKCP_SWRAD_DOWN_MONTHLY.copy()
UKCP_SWRAD_DOWN_MONTHLY_BIAS.default_barlabel = (
    "Bias in downwelling shortwave irradiance, W m$^{-2}$"
)
UKCP_SWRAD_DOWN_MONTHLY_BIAS.extendcolbar = "both"
UKCP_SWRAD_DOWN_MONTHLY_BIAS.cpal = "PuOr"
UKCP_SWRAD_DOWN_MONTHLY_BIAS.vrange = [-30.0, 75.0]
UKCP_SWRAD_DOWN_MONTHLY_BIAS.vmid = 0.0
UKCP_SWRAD_DOWN_MONTHLY_BIAS.vstep = 5.0


# Longwave, downwelling
UKCP_LWRAD_DOWN_MONTHLY = UKCPNEAT.copy()
UKCP_LWRAD_DOWN_MONTHLY.tag = "UKCP_irradiance_lwdown_"
UKCP_LWRAD_DOWN_MONTHLY.default_barlabel = "Downwelling longwave irradiance, W m$^{-2}$"
UKCP_LWRAD_DOWN_MONTHLY.preferred_unit = cf_units.Unit("W/m^2")
UKCP_LWRAD_DOWN_MONTHLY.extendcolbar = "max"
UKCP_LWRAD_DOWN_MONTHLY.cpal = "PuOr"
UKCP_LWRAD_DOWN_MONTHLY.undercol = "#492f0b"
UKCP_LWRAD_DOWN_MONTHLY.overcol = "#240938"
UKCP_LWRAD_DOWN_MONTHLY.vrange = [200.0, 380.0]
UKCP_LWRAD_DOWN_MONTHLY.vmid = None
UKCP_LWRAD_DOWN_MONTHLY.vstep = 20.0

UKCP_LWRAD_DOWN_MONTHLY_BIAS = UKCP_LWRAD_DOWN_MONTHLY.copy()
UKCP_LWRAD_DOWN_MONTHLY_BIAS.default_barlabel = (
    "Bias in downwelling longwave irradiance, W m$^{-2}$"
)
UKCP_LWRAD_DOWN_MONTHLY_BIAS.extendcolbar = "both"
UKCP_LWRAD_DOWN_MONTHLY_BIAS.cpal = "PuOr"
UKCP_LWRAD_DOWN_MONTHLY_BIAS.vrange = [-15.0, 35.0]
UKCP_LWRAD_DOWN_MONTHLY_BIAS.vmid = 0.0
UKCP_LWRAD_DOWN_MONTHLY_BIAS.vstep = 5.0


# Shortwave, net.
UKCP_SWRAD_NET_MONTHLY = UKCPNEAT.copy()
UKCP_SWRAD_NET_MONTHLY.tag = "UKCP_irradiance_swnet_"
UKCP_SWRAD_NET_MONTHLY.default_barlabel = (
    "Net downward shortwave irradiance, W m$^{-2}$"
)
UKCP_SWRAD_NET_MONTHLY.preferred_unit = cf_units.Unit("W/m^2")
UKCP_SWRAD_NET_MONTHLY.extendcolbar = "max"
UKCP_SWRAD_NET_MONTHLY.cpal = "PuOr"
UKCP_SWRAD_NET_MONTHLY.undercol = "#492f0b"
UKCP_SWRAD_NET_MONTHLY.overcol = "#240938"
UKCP_SWRAD_NET_MONTHLY.vrange = [0.0, 300.0]
UKCP_SWRAD_NET_MONTHLY.vmid = None
UKCP_SWRAD_NET_MONTHLY.vstep = 50.0

UKCP_SWRAD_NET_MONTHLY_BIAS = UKCP_SWRAD_NET_MONTHLY.copy()
UKCP_SWRAD_NET_MONTHLY_BIAS.default_barlabel = (
    "Bias in net downward shortwave irradiance, W m$^{-2}$"
)
UKCP_SWRAD_NET_MONTHLY_BIAS.extendcolbar = "both"
UKCP_SWRAD_NET_MONTHLY_BIAS.cpal = "PuOr"
UKCP_SWRAD_NET_MONTHLY_BIAS.vrange = [-30.0, 60.0]
UKCP_SWRAD_NET_MONTHLY_BIAS.vmid = 0.0
UKCP_SWRAD_NET_MONTHLY_BIAS.vstep = 10.0


# Longwave, net
UKCP_LWRAD_NET_MONTHLY = UKCPNEAT.copy()
UKCP_LWRAD_NET_MONTHLY.tag = "UKCP_irradiance_lwnet_"
UKCP_LWRAD_NET_MONTHLY.default_barlabel = "Net downward longwave irradiance, W m$^{-2}$"
UKCP_LWRAD_NET_MONTHLY.preferred_unit = cf_units.Unit("W/m^2")
UKCP_LWRAD_NET_MONTHLY.extendcolbar = "max"
UKCP_LWRAD_NET_MONTHLY.cpal = "PuOr"
UKCP_LWRAD_NET_MONTHLY.undercol = "#492f0b"
UKCP_LWRAD_NET_MONTHLY.overcol = "#240938"
UKCP_LWRAD_NET_MONTHLY.vrange = [-100.0, 0.0]
UKCP_LWRAD_NET_MONTHLY.vmid = None
UKCP_LWRAD_NET_MONTHLY.vstep = 10.0

UKCP_LWRAD_NET_MONTHLY_BIAS = UKCP_LWRAD_NET_MONTHLY.copy()
UKCP_LWRAD_NET_MONTHLY_BIAS.default_barlabel = (
    "Bias in net downward longwave irradiance, W m$^{-2}$"
)
UKCP_LWRAD_NET_MONTHLY_BIAS.extendcolbar = "both"
UKCP_LWRAD_NET_MONTHLY_BIAS.cpal = "PuOr"
UKCP_LWRAD_NET_MONTHLY_BIAS.vrange = [-20.0, 35.0]
UKCP_LWRAD_NET_MONTHLY_BIAS.vmid = 0.0
UKCP_LWRAD_NET_MONTHLY_BIAS.vstep = 5.0


# Cloud fraction
UKCP_CLOUDFRAC_MONTHLY = UKCPNEAT.copy()
UKCP_CLOUDFRAC_MONTHLY.tag = "UKCP_cloudfraction_"
UKCP_CLOUDFRAC_MONTHLY.default_barlabel = "Cloud area fraction, %"
UKCP_CLOUDFRAC_MONTHLY.preferred_unit = cf_units.Unit("%")
UKCP_CLOUDFRAC_MONTHLY.extendcolbar = "neither"
UKCP_CLOUDFRAC_MONTHLY.cpal = "PuOr"
UKCP_CLOUDFRAC_MONTHLY.undercol = "#492f0b"
UKCP_CLOUDFRAC_MONTHLY.overcol = "#240938"
UKCP_CLOUDFRAC_MONTHLY.vrange = [0.0, 100.0]
UKCP_CLOUDFRAC_MONTHLY.vmid = 50.0  # None
UKCP_CLOUDFRAC_MONTHLY.vstep = 10.0

UKCP_CLOUDFRAC_MONTHLY_BIAS = UKCP_CLOUDFRAC_MONTHLY.copy()
# Note we're showing the difference in percentage points,
# NOT the percentage difference of the percentage!
UKCP_CLOUDFRAC_MONTHLY_BIAS.default_barlabel = (
    "Bias in cloud area fraction (difference in %)"
)
UKCP_CLOUDFRAC_MONTHLY_BIAS.extendcolbar = "both"
UKCP_CLOUDFRAC_MONTHLY_BIAS.cpal = "PuOr"
UKCP_CLOUDFRAC_MONTHLY_BIAS.vrange = [-20.0, 30.0]
UKCP_CLOUDFRAC_MONTHLY_BIAS.vmid = 0.0
UKCP_CLOUDFRAC_MONTHLY_BIAS.vstep = 5.0


# Other variables:
UKCP_SPECIFIC_HUMIDITY = UKCPNEAT.copy()
UKCP_SPECIFIC_HUMIDITY.tag = "UKCP_sh"
UKCP_SPECIFIC_HUMIDITY.default_barlabel = "Specific humidity"
UKCP_SPECIFIC_HUMIDITY.preferred_unit = cf_units.Unit(1)
UKCP_SPECIFIC_HUMIDITY.extendcolbar = "both"
UKCP_SPECIFIC_HUMIDITY.cpal = "PuOr"
UKCP_SPECIFIC_HUMIDITY.undercol = "#492f0b"
UKCP_SPECIFIC_HUMIDITY.overcol = "#240938"
UKCP_SPECIFIC_HUMIDITY.vrange = [0.0, 1.0]
UKCP_SPECIFIC_HUMIDITY.vmid = 0.5
UKCP_SPECIFIC_HUMIDITY.vstep = 0.1


UKCP_SPECIFIC_HUMIDITY_ANOM = UKCP_SPECIFIC_HUMIDITY.copy()
UKCP_SPECIFIC_HUMIDITY_ANOM.tag = "UKCP_sh_anom"
UKCP_SPECIFIC_HUMIDITY_ANOM.default_barlabel = "Specific humidity anomaly, %"
UKCP_SPECIFIC_HUMIDITY_ANOM.preferred_unit = cf_units.Unit("%")
UKCP_SPECIFIC_HUMIDITY_ANOM.vrange = [-10.0, 20.0]
UKCP_SPECIFIC_HUMIDITY_ANOM.vmid = 0.0
UKCP_SPECIFIC_HUMIDITY_ANOM.vstep = 2.0


UKCP_RELATIVE_HUMIDITY = UKCPNEAT.copy()
UKCP_RELATIVE_HUMIDITY.tag = "UKCP_rh"
UKCP_RELATIVE_HUMIDITY.default_barlabel = "Relative humidity"
UKCP_RELATIVE_HUMIDITY.preferred_unit = cf_units.Unit("%")
UKCP_RELATIVE_HUMIDITY.extendcolbar = "both"
UKCP_RELATIVE_HUMIDITY.cpal = "PuOr"
UKCP_RELATIVE_HUMIDITY.undercol = "#492f0b"
UKCP_RELATIVE_HUMIDITY.overcol = "#240938"
UKCP_RELATIVE_HUMIDITY.vrange = [0.0, 100.0]
UKCP_RELATIVE_HUMIDITY.vmid = 50.0
UKCP_RELATIVE_HUMIDITY.vstep = 10.0


UKCP_RELATIVE_HUMIDITY_ANOM = UKCP_RELATIVE_HUMIDITY.copy()
UKCP_RELATIVE_HUMIDITY_ANOM.tag = "UKCP_rh_anom"
UKCP_RELATIVE_HUMIDITY_ANOM.default_barlabel = "Relative humidity anomaly"
UKCP_RELATIVE_HUMIDITY_ANOM.preferred_unit = cf_units.Unit("%")
UKCP_RELATIVE_HUMIDITY_ANOM.vrange = [-10.0, 10.0]
UKCP_RELATIVE_HUMIDITY_ANOM.vmid = 0.0
UKCP_RELATIVE_HUMIDITY_ANOM.vstep = 2.0


UKCP_PMSL_ANOM = UKCPNEAT.copy()
UKCP_PMSL_ANOM.tag = "UKCP_pmsl_anom"
UKCP_PMSL_ANOM.default_barlabel = "Sea level pressure anomaly, hPa"
UKCP_PMSL_ANOM.preferred_unit = cf_units.Unit("hPa")
UKCP_PMSL_ANOM.extendcolbar = "both"
UKCP_PMSL_ANOM.cpal = "PuOr"
UKCP_PMSL_ANOM.undercol = "#492f0b"
UKCP_PMSL_ANOM.overcol = "#240938"
UKCP_PMSL_ANOM.vrange = [-25.0, 25.0]
UKCP_PMSL_ANOM.vmid = 0.0
UKCP_PMSL_ANOM.vstep = 5.0

# Amount of precipitation in 1 day
UKCP_1DAY_PRECIP = UKCPNEAT.copy()
UKCP_1DAY_PRECIP.tag = "UKCP_1day_precip"
UKCP_1DAY_PRECIP.default_barlabel = "1-day total precipitation, mm"
UKCP_1DAY_PRECIP.preferred_unit = cf_units.Unit("mm")
UKCP_1DAY_PRECIP.extendcolbar = "max"
UKCP_1DAY_PRECIP.cpal = "Blues"
UKCP_1DAY_PRECIP.undercol = "#492f0b"
UKCP_1DAY_PRECIP.overcol = "#240938"
UKCP_1DAY_PRECIP.vrange = [20, 110]
UKCP_1DAY_PRECIP.vmid = None
UKCP_1DAY_PRECIP.vstep = 10

# Amount of precipitation in 1 day anomalies
UKCP_1DAY_PRECIP_ANOM = UKCP_1DAY_PRECIP.copy()
UKCP_1DAY_PRECIP_ANOM.tag = "UKCP_1day_precip_anom"
UKCP_1DAY_PRECIP_ANOM.preferred_unit = cf_units.Unit("mm")
UKCP_1DAY_PRECIP_ANOM.default_barlabel = "1-day total precipitation anomaly, mm"
UKCP_1DAY_PRECIP_ANOM.extendcolbar = "both"
UKCP_1DAY_PRECIP_ANOM.cpal = "Blues"
UKCP_1DAY_PRECIP_ANOM.vrange = [20, 110]
UKCP_1DAY_PRECIP_ANOM.vmid = None
UKCP_1DAY_PRECIP_ANOM.vstep = 10

# Amount of precipitation in 5 days
UKCP_5DAY_PRECIP = UKCPNEAT.copy()
UKCP_5DAY_PRECIP.tag = "UKCP_5DAY_precip"
UKCP_5DAY_PRECIP.default_barlabel = "5-day total precipitation, mm"
UKCP_5DAY_PRECIP.preferred_unit = cf_units.Unit("mm")
UKCP_5DAY_PRECIP.extendcolbar = "max"
UKCP_5DAY_PRECIP.cpal = "Blues"
UKCP_5DAY_PRECIP.undercol = "#492f0b"
UKCP_5DAY_PRECIP.overcol = "#240938"
UKCP_5DAY_PRECIP.vrange = [50, 200]
UKCP_5DAY_PRECIP.vmid = None
UKCP_5DAY_PRECIP.vstep = 15

# Amount of precipitation in 5 days anomalies
UKCP_5DAY_PRECIP_ANOM = UKCP_5DAY_PRECIP.copy()
UKCP_5DAY_PRECIP_ANOM.tag = "UKCP_5day_precip_anom"
UKCP_5DAY_PRECIP_ANOM.preferred_unit = cf_units.Unit("mm")
UKCP_5DAY_PRECIP_ANOM.default_barlabel = "1-day total precipitation anomaly, mm"
UKCP_5DAY_PRECIP_ANOM.extendcolbar = "both"
UKCP_5DAY_PRECIP_ANOM.cpal = "Blues"
UKCP_5DAY_PRECIP_ANOM.vrange = [50, 200]
UKCP_5DAY_PRECIP_ANOM.vmid = None
UKCP_5DAY_PRECIP_ANOM.vstep = 15
