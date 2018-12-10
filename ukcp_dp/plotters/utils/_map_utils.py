# -*- coding: utf-8 -*-
import logging
import math
from os import path

import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import iris
import iris.plot as iplt
import matplotlib
import matplotlib.cm as mpl_cm
import matplotlib.colors as mpl_col
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from ukcp_dp.constants import DPI_DISPLAY, DPI_SAVING, ROOT_DIR
from ukcp_dp.plotters.utils._plotting_utils import end_figure, \
    make_colourbar, start_figure
from ukcp_dp.plotters.utils._region_utils import UKSHAPES
from ukcp_dp.plotters.utils._region_utils import get_ukcp_shapefile_regions
from ukcp_dp.processors import add_mask, rectify_units


log = logging.getLogger(__name__)


def plot_standard_map(thecube, settings, fig=None, ax=None,
                      barlab=None, bar_orientation=None,
                      mask_sea=False, mask_land=False, lsm_cube=None,
                      outfnames=["x11"]):
    """
    Wrapper to plot_map(),
    where most of the settings are given
    in a StandardMap object called 'settings'

    thecube is a single 2-D cube to plot.

    barlab is a string to use for the colour bar label,
    making it easy to override the default in the StandardMap object.
    (if None then it is taken from settings.default_barlabel)

    If bar_orientation is None then it is taken from settings,
    but having it here makes it easy to override,
    e.g. with "none" to specify no colour bar!
    (if you're making a multi-panel plot,
     your settings probably define the bar the the whole figure,
     but you still want to switch it off for the panels)

    Note that settings.maskcol is used for
    both the badcol and axbackgroundcol arguments.
    """

    if barlab is None:
        barlab = settings.default_barlabel
    if bar_orientation is None:
        bar_orientation = settings.bar_orientation

    result = plot_map(thecube, fig=fig, ax=ax, cont=settings.cont,
                      cpal=settings.cpal, bar_orientation=bar_orientation,
                      bar_position=settings.bar_position,
                      bar_tick_spacing=settings.bar_tick_spacing,
                      extendcolbar=settings.extendcolbar,
                      vrange=settings.vrange, vstep=settings.vstep,
                      vmid=settings.vmid,
                      badcol=settings.maskcol, undercol=settings.undercol,
                      overcol=settings.overcol,
                      cmsize=settings.cmsize,
                      dpi=settings.dpi,  dpi_display=settings.dpi_display,
                      fsize=settings.fsize, fontfam=settings.fontfam,
                      proj=settings.proj,
                      marlft=settings.marlft, marrgt=settings.marrgt,
                      martop=settings.martop, marbot=settings.marbot,
                      marwsp=settings.marwsp, marhsp=settings.marhsp,
                      contlines=settings.contlines,
                      contlinealpha=settings.contlinealpha,
                      contlinew=settings.contlinew,
                      contlinecol=settings.contlinecol,
                      countrylw=settings.countrylw,
                      countrylcol=settings.countrylcol,
                      regionlw=settings.regionlw,
                      regionlcol=settings.regionlcol,
                      riverslw=settings.riverslw,
                      riverslcol=settings.riverslcol,
                      coastlw=settings.coastlw,
                      coastlcol=settings.coastlcol,
                      gridlw=settings.gridlw,
                      gridlcol=settings.gridlcol,
                      gridlsty=settings.gridlsty,
                      barlabel=barlab,
                      xlims=settings.xlims, ylims=settings.ylims,
                      showglobal=settings.showglobal,
                      preferred_unit=settings.preferred_unit,
                      xlims_for_grid=settings.xlims_for_grid,
                      ylims_for_grid=settings.ylims_for_grid,
                      dxgrid=settings.dxgrid, dygrid=settings.dygrid,
                      xgridax=settings.xgridax, ygridax=settings.ygridax,
                      mask_sea=mask_sea, mask_land=mask_land,
                      lsm_cube=lsm_cube,
                      axbackgroundcol=settings.maskcol,
                      figbackgroundcol=settings.figbackgroundcol,
                      outfnames=outfnames)

    return result


def plot_standard_choropleth_map(thecube, settings, fig=None, ax=None,
                                 barlab=None, bar_orientation=None,
                                 outfnames=["x11"], hi_res=True):
    """
    Wrapper to plot_choropleth_map(),
    where most of the settings are given
    in a StandardMap object called 'settings'

    """
    resolution = thecube.attributes['resolution']
    shapefile_regions = get_ukcp_shapefile_regions(resolution, hi_res=hi_res)
    print(thecube)
    if barlab is None:
        barlab = settings.default_barlabel
    if bar_orientation is None:
        bar_orientation = settings.bar_orientation

    result = plot_choropleth_map(
        shapefile_regions, [thecube], fig=fig, ax=ax,
        barlabel=barlab, bar_orientation=bar_orientation,
        bar_position=settings.bar_position, outfnames=outfnames,
        cpal=settings.cpal,
        extendcolbar=settings.extendcolbar,
        vrange=settings.vrange, vstep=settings.vstep, vmid=settings.vmid,
        badcol=settings.maskcol, undercol=settings.undercol,
        overcol=settings.overcol,
        cmsize=settings.cmsize, dpi=settings.dpi,
        fsize=settings.fsize, fontfam=settings.fontfam,
        proj=settings.proj,
        marlft=settings.marlft, marrgt=settings.marrgt,
        martop=settings.martop, marbot=settings.marbot,
        marwsp=settings.marwsp, marhsp=settings.marhsp,
        countrylw=settings.countrylw, countrylcol=settings.countrylcol,
        regionlw=settings.regionlw,  regionlcol=settings.regionlcol,
        riverslw=settings.riverslw,  riverslcol=settings.riverslcol,
        coastlw=settings.coastlw,
        xlims=settings.xlims, ylims=settings.ylims,
        showglobal=settings.showglobal, preferred_unit=settings.preferred_unit,
        dxgrid=settings.dxgrid, dygrid=settings.dygrid,
        xgridax=settings.xgridax, ygridax=settings.ygridax,
        axbackgroundcol=settings.maskcol,
        figbackgroundcol=settings.figbackgroundcol)

    return result


def plot_map(dcube_input, fig=None, ax=None,
             cont=False, vrange=[-1, 1], vstep=0.2, vmid=None,
             cpal="RdBu_r", bar_tick_spacing=1,
             bar_orientation='horizontal', bar_position=None,
             extendcolbar="both", badcol=(1, 1, 1, 0),
             undercol="magenta", overcol="yellow",
             cmsize=[23, 18], dpi=DPI_SAVING, dpi_display=DPI_DISPLAY,
             fsize=12, fontfam="Arial",
             proj=ccrs.PlateCarree(),
             marlft=0.03, marrgt=0.97, martop=0.96, marbot=0.06, marwsp=0,
             marhsp=0,
             contlines=None, contlinew=1.0, contlinecol="yellow",
             contlinealpha=1,
             countrylw=1, countrylcol='grey',
             regionlw=1, regionlcol=None,
             riverslw=1, riverslcol=None,
             coastlw=1, coastlcol="black",
             gridlw=0.5, gridlcol="grey", gridlsty=":",
             barlabel="Unknown", preferred_unit=None,
             xlims=None, ylims=None, showglobal=False,
             xlims_for_grid=None, ylims_for_grid=None,
             dxgrid=20, dygrid=20, xgridax=[True, False],
             ygridax=[True, False],
             mask_sea=False, mask_land=False, lsm_cube=None,
             axbackgroundcol=None, figbackgroundcol=None,
             outfnames=["x11"]):
    """
    All the gubbins required to make a nice map.
    Most arguments are the same as components of a stds.StandardMap object;
    see there for further documentation.

    dcube is a single 2-D cube holding the data to plot.

    outfnames is a list of strings;
    If any end in 'x11', the plot will be displayed onscreen;
    otherwise, it attempts to write it to a file.
    To NOT plot to file or screen, set outfnames=None;
    you can then add other things to the plot
    as the Axes object is returned.
    """
    # FIRST THING is to convert the unit of the data cube, if required.
    # (if not, just point dcube to the input cube without a copy)
    if preferred_unit is not None:
        if dcube_input.units != preferred_unit:
            log.debug("NOTE: converting cube units (in a copy) from {} to {}".
                      format(dcube_input.units.name, preferred_unit.name))
            dcube = dcube_input.copy()

            # Got a function to do all this now:
            rectify_units(dcube, target_unit=preferred_unit)

        else:
            # Already in the right units
            dcube = dcube_input
    else:
        # No preferred unit, leave as it is:
        dcube = dcube_input

    # Show the value range, and the units:
    log.debug("Input cube value range: {}-{} {}".format(
        dcube.data.min(), dcube.data.max(), dcube.units.title("")))

    # Next, add a mask to the cube covering the sea/land as selected.
    # We go by the assumption that, in the land-sea mask (LSM) file,
    #  1 ==> land, 0 ==> sea.
    #  So to mask out the sea,  we mask where LSM < 0.5,
    # and to mask out the land, we mask where LSM > 0.5.
    if mask_sea or mask_land:
        if lsm_cube is None:
            log.warn("No land--sea mask specified, but mask requested "
                     "(sea:{}; land:{},)".format(mask_sea, mask_land))
            raise UserWarning("Land--sea mask cube required in plot_map().")
        #
        log.debug("Applying LSM:")
        # Note we let the user mask either the land or sea or both (!).
        # More fool them.
        if mask_sea:
            dcube_masked = add_mask(
                dcube, lsm_cube, comparator="<", threshold=0.5)
        if mask_land:
            dcube_masked = add_mask(
                dcube, lsm_cube, comparator=">", threshold=0.5)
    else:
        # Leave as it is:
        dcube_masked = dcube

    # Set up the Figure object, if required:
    if fig is None:
        newfig = True
        # Set up the Figure object
        # (including setting the font family and size)
        fig, oldfont_family, oldfont_size = start_figure(cmsize, dpi_display,
                                                         fontfam, fsize,
                                                         figbackgroundcol)

    else:
        # Figure object already exists.
        newfig = False
        log.debug("Figure object already exists, ")
        log.debug("Not using plot_map() arguments: ")
        log.debug("              cmsize,dpi_display, fsize,fontfam,")
        log.debug("              marlft,marrgt,martop,marbot,marwsp,marhsp")

    # Set up the Axes object:
    if ax is None:
        # Set up the Axes object as a cartopy GeoAxes object,
        # i.e. one that is spatial-aware, so we can add coastlines etc later.)
        # (just doing the iplt.contourf will also do this,
        #  but we'd have to grab the gca() afterwards then)
        ax = plt.axes(projection=proj)
    else:
        # Already got an Axes object:
        log.debug("Axes object already exists,")
        log.debug("Not using plot_map() argument: proj")

    # Set the Axes background colour:
    # The user can specify the alpha by using an rgba tuple,
    # e.g. (1,0,1,0.5) would be semitransparent magenta.
    if axbackgroundcol is not None:
        ax.patch.set_facecolor(axbackgroundcol)
        # ax.patch.set_alpha(1.0)

    # Set up colour bar:
    # http://matplotlib.org/examples/color/colormaps_reference.html
    #
    levels = np.arange(vrange[0], vrange[1] + vstep, vstep)
    # np.arange can give inconsistent results
    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.arange.html

    # Allow for not labelling every colour in the colourbar:
    levels_labelled = np.arange(vrange[0],
                                vrange[1] + vstep * bar_tick_spacing,
                                vstep * bar_tick_spacing)

    # Set up the colourmap:
    cmap = _setup_colourmap(cpal, vrange, vstep, vmid=vmid)

    # Add values for bad/over/under:
    # Note we're not hardcoding an alpha value.
    # The user can specify it through badcol by using an rgba tuple,
    # e.g. (1,0,1,0.5) would be semitransparent magenta.
    if badcol is not None:
        cmap.set_bad(color=badcol)

    # Require the user to have specified overcol and undercol:
    cmap.set_over(color=overcol)
    cmap.set_under(color=undercol)

    # Set plot limits.
    # For some projections (Robinson!),
    # it only makes sense to use them globally,
    # but setting global extents seems to confuse it.
    # So we have an override option:
    if showglobal:
        ax.set_global()
    else:
        # A previous version prevented specifying Axes extents
        # if we used the ccrs.OSGB() projection;
        # now we have a better projection,
        # I've removed that special case, letting it get confused
        # if anyone uses it...

        # Get the x/y limits from the data if they're not specified:
        if not xlims:
            xlims = [dcube_masked.coord('longitude').points.min(),
                     dcube_masked.coord('longitude').points.max()]
        if not ylims:
            ylims = [dcube_masked.coord('latitude').points.min(),
                     dcube_masked.coord('latitude').points.max()]

        ax.set_extent(xlims + ylims, crs=proj)

    # Only label the axes if we're in the Plate Carrée projection:
    if proj == ccrs.PlateCarree():
        ax.set_xlabel(r"Longitude")
        ax.set_ylabel(r"Latitude")

    # Plot the data!
    if cont:
        # Filled contours
        # (always discrete colours, unless you cheat and have many colours)
        cf = iplt.contourf(dcube_masked, levels,
                           cmap=cmap, extend=extendcolbar)
    else:
        # Shaded gridcells
        # (discrete colours if the number is given when setting up cmap,
        #  otherwise continuous colours)
        cf = iplt.pcolormesh(dcube_masked, cmap=cmap,
                             vmin=vrange[0], vmax=vrange[1])

    # Add extra annotations!
    # e.g. http://www.naturalearthdata.com/downloads/50m-cultural-vectors/

    # Extra contour lines, if requested:
    if contlines is not None:
        # Set the negative linestyle to be solid, like positive.
        # (the default is 'dashed'; 'dotted' doesn't work)
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'

    # The original pbskill_maps.py routine
    # had a bit here for outlining [lat--lon-defined] subregions.
    # I've cut this from here,
    # as regional maps should probably be done elsewhere...

    # Add gridlines if the grid linewidth > 0
    # (and label them on the axes, IF we're in PlateCarree)
    if gridlcol is not None:
        gridlabels = (proj == ccrs.PlateCarree())
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=gridlabels,
                          linewidth=gridlw, linestyle=gridlsty, color=gridlcol)
        if gridlabels:
            # Options to switch on/off individual axes labels:
            gl.xlabels_bottom = xgridax[0]
            gl.xlabels_top = xgridax[1]
            gl.ylabels_left = ygridax[0]
            gl.ylabels_right = ygridax[1]

        # Set limits for the grid separate to the plot's xlims/ylims:
        if showglobal:
            xlims_for_grid = [-180, 180]
            ylims_for_grid = [-90, 90]
        else:
            if xlims_for_grid is None:
                xlims_for_grid = xlims if xlims is not None else [
                    dcube_masked.coord('longitude').points.min(),
                    dcube_masked.coord('longitude').points.max()]
            if ylims_for_grid is None:
                ylims_for_grid = ylims if ylims is not None else [
                    dcube_masked.coord('latitude').points.min(),
                    dcube_masked.coord('latitude').points.max()]

        xgridrange = [float(dxgrid) * np.round(float(val) / float(dxgrid))
                      for val in xlims_for_grid]
        ygridrange = [float(dygrid) * np.round(float(val) / float(dygrid))
                      for val in ylims_for_grid]

        xgridpts = np.arange(xgridrange[0], xgridrange[1] + dxgrid, dxgrid)
        ygridpts = np.arange(ygridrange[0], ygridrange[1] + dygrid, dygrid)
        # Filter in case the rounding meant we went off-grid!
        xgridpts = [xgridpt for xgridpt in xgridpts if (
            xgridpt >= -180 and xgridpt <= 360)]
        ygridpts = [ygridpt for ygridpt in ygridpts if (
            ygridpt >= -90 and ygridpt <= 90)]

        gl.xlocator = mticker.FixedLocator(xgridpts)
        gl.ylocator = mticker.FixedLocator(ygridpts)
        if gridlabels:
            gl.xformatter = LONGITUDE_FORMATTER
            gl.yformatter = LATITUDE_FORMATTER

    # Adjust the margins:
    if newfig:
        # We could legally do this even if this wasn't a new figure,
        # (we've got the figure object using gcf() above),
        # but in practice we'll be designing the multipanel figure
        # elsewhere, and that is where the margins should be set.
        if (marlft is None and marrgt is None and martop is None and
                marbot is None):
            plt.tight_layout()
        else:
            fig.subplots_adjust(left=marlft,  bottom=marbot,
                                right=marrgt,  top=martop,
                                wspace=marwsp,  hspace=marhsp)
    # (note that we have a wrapper, plotgeneral.set_standard_margins(),
    # which does this for a StandardMap object)

    # Colour bar:
    if bar_orientation.lower() == "none":
        log.debug("Skipping colour bar")
    else:
        make_colourbar(fig, bar_orientation, extendcolbar, levels_labelled,
                       barlabel, colmappable=cf, bar_pos=bar_position)

    # Finally, make the plot, if we've provided any filenames:
    if outfnames is not None:
        # This saves to any filenames if specified, and/or displays to screen,
        # closes the plot and resets the font family & size.
        end_figure(outfnames, dpi=dpi, oldfont_family=oldfont_family,
                   oldfont_size=oldfont_size)

    else:
        log.debug("No outfnames provided, continue plotting using Axes ax")

    log.debug("All done in plot_map, returning")

    return (ax, cf)


def plot_choropleth_map(regions, regionaldata_input, regional_sigs=None,
                        fig=None, ax=None,
                        vrange=[-1, 1], vstep=0.2, vmid=None, cpal="RdBu_r",
                        badcol="dimgrey", undercol="magenta", overcol="yellow",
                        bar_orientation='horizontal', bar_position=None,
                        extendcolbar="both",
                        regionlw=1, regionlcol="black",
                        cmsize=[23, 18], dpi=DPI_SAVING,
                        dpi_display=DPI_DISPLAY, fsize=12, fontfam="Arial",
                        proj=ccrs.PlateCarree(),
                        marlft=0.03, marrgt=0.97, martop=0.96, marbot=0.06,
                        marwsp=0, marhsp=0,
                        countrylw=1,    countrylcol="grey",
                        othershapefile=None,
                        othershapefilelw=1,  othershapefilelcol=None,
                        othershapefile_sel=dict(
                            key="Region", vals=['England', 'Scotland']),
                        shapes_projtag="projection_forUKCP",
                        riverslw=1,     riverslcol=None,
                        coastlw=1,      coastlcol="blue",
                        barlabel="Unknown", preferred_unit=None,
                        stock_img=False,
                        xlims=None, ylims=None, showglobal=False,
                        dxgrid=20, dygrid=20, xgridax=[True, False],
                        ygridax=[True, False],
                        axbackgroundcol=None, figbackgroundcol=None,
                        outfnames=["x11"]):
    """
    All the gubbins required to make a nice choropleth map
    (i.e. a map where we shade in polygonal regions according to values,
    rather than contours or a grid of pixels),

    regions is a list of cartopy.io.shapereader.Record objects,
    e.g. as returned by get_ukcp_shapefile_regions() or get_shapefile_regions()

    regionaldata is a CubeList (in future: a cube?)
    with one element (a scalard Cube) per region.
    (it gets turned into a dictionary within this function)

    regional_sigs is intended to be used for flagging areas
    (e.g. where "significant" or not)
    to overlay with crosshatching of some sort.
    I haven't implemented this yet as it's not obvious what data structures
    we'd use for this yet.

    Set cpal to be a list of colours to trigger category plotting
    (following general_choropleth() again)

    stock_img will underplot the standard Cartopy stock image.


    Other arguments are pretty much the same as for plot_maps()
    above. Note that we don't have a wrapper function
    that passes in StandardMap settings yet.

    Furthermore, because so much of this function is identical
    to plot_maps(), it might be good to unify them in some way
    at some point.


    outfnames is a list of strings;
    If any end in 'x11', the plot will be displayed onscreen;
    otherwise, it attempts to write it to a file.
    To NOT plot to file or screen, set outfnames=None;
    you can then add other things to the plot
    as the Axes object is returned.
    """
    # FIRST THING is to convert the unit of the data cube, if required.
    # (if not, just point dcube to the input cube without a copy)
    if preferred_unit is not None:
        regionaldata = iris.cube.CubeList()
        for regcube_input in regionaldata_input:
            if regcube_input.units != preferred_unit:
                log.debug("NOTE: converting cube units (in a copy) from {} to "
                          "{}".format(regcube_input.units.name,
                                      preferred_unit.name))
                regcube = regcube_input.copy()

                # Got a function to do all this now:
                rectify_units(regcube, target_unit=preferred_unit)

            else:
                # Already in the right units
                regcube = regcube_input

            regionaldata.append(regcube)

    else:
        # No preferred unit, leave as it is:
        regionaldata = regionaldata_input

    # While we're poking around, we make a dictionary out of the cube data,
    # for ease of working with later.
    # (note that each cube in the CubeList must be a scalar
    #  otherwise we couldn't plot it)
    # -- the details of what we're doing here are likely to change later!

    # This is used to look up metadata for the shapefiles:
    region_set = regionaldata[0].attributes['resolution']
    reg_key = UKSHAPES[region_set]["attr_key"]
    regdata_dict = dict()
    for regcube in regionaldata:
        for reg_slice in regcube.slices_over(['region']):
            regdata_dict[reg_slice.coords(var_name='geo_region')[
                0].points[0]] = float(reg_slice.data)
    regunits = regcube.units
    # Don't delete the CubeList - we'll probably want it later for
    # labelling...?

    # Do the same for regional_sigs, if present:
    if regional_sigs is not None:
        raise UserWarning(
            "Not yet implemented how we're handling data for significance "
            "shading!")

    # Show the value range, and the units:
    log.debug("Input cube value range: {}-{} {}".format(
              min(regdata_dict.values()), max(regdata_dict.values()),
              regunits.title("")))

    # Set up the Figure object, if required:
    if fig is None:
        newfig = True
        # Set up the Figure object
        # (including setting the font family and size)
        fig, oldfont_family, oldfont_size = start_figure(cmsize, dpi_display,
                                                         fontfam, fsize,
                                                         figbackgroundcol)

    else:
        # Figure object already exists.
        newfig = False
        log.debug("Figure object already exists, ")
        log.debug("Not using plot_choropleth_map() arguments: ")
        log.debug("              cmsize,dpi_display, fsize,fontfam,")
        log.debug("              marlft,marrgt,martop,marbot,marwsp,marhsp")

    # Set up the Axes object:
    if ax is None:
        # Set up the Axes object as a cartopy GeoAxes object,
        # i.e. one that is spatial-aware, so we can add coastlines etc later.)
        # (just doing the iplt.contourf will also do this,
        #  but we'd have to grab the gca() afterwards then)
        ax = plt.axes(projection=proj)
    else:
        # Already got an Axes object:
        log.debug("Axes object already exists,")
        log.debug("Not using plot_choropleth_map() argument: proj")

    # Set the Axes background colour:
    # The user can specify the alpha by using an rgba tuple,
    # e.g. (1,0,1,0.5) would be semitransparent magenta.
    if axbackgroundcol is not None:
        ax.patch.set_facecolor(axbackgroundcol)
        # ax.patch.set_alpha(1.0)

    do_categories = isinstance(cpal, list) or isinstance(cpal, tuple)

    # Set up colour bar:
    # http://matplotlib.org/examples/color/colormaps_reference.html
    #
    if do_categories:
        # Categorical case:
        log.debug("Categorical plot selected.")
        level_ticks = np.arange(vrange[0], vrange[1] + vstep, vstep)
        level_bndry = np.arange(
            vrange[0] - vstep, vrange[1] + vstep, vstep) + 0.5
        cmap = matplotlib.colors.ListedColormap(cpal)
        normalizer = matplotlib.colors.BoundaryNorm(level_bndry, cmap.N)
        # Note that this normalisation scales all values to the
        # range of discrete integers provided.
        # This means that NaNs/unders/overs are replaced with the min/max in
        #  the range, so it's useful to add extra categories for these too.
        # (The usual normalisation matplotlib.colors.Normalize()
        #  scales data values to 0..1 for plotting)

        # Remove tick label for first and last category ("under" and "over"):
        level_tick_labs = [str(x) for x in level_ticks]
        level_tick_labs[0] = ""
        level_tick_labs[-1] = ""

    else:
        # Usual case: range of values.
        # levels = np.arange(vrange[0], vrange[1]+vstep, vstep)
        # np.arange can give inconsistent results
        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.arange.html
        # so this is better:
        nsteps = (vrange[1] - vrange[0]) / vstep
        levels = np.linspace(vrange[0], vrange[1],
                             num=nsteps + 1, endpoint=True)

        # Set up the colourmap:
        cmap = _setup_colourmap(cpal, vrange, vstep, vmid=vmid)

        # This is an important feature for choropleth maps:
        normalizer = matplotlib.colors.Normalize(
            vmin=vrange[0], vmax=vrange[1])
        # Give this a real value (°C or whatever)
        # and this returns the normalised (0,1) value
        # that we can pass to cmap to return a colour!

    # [DOES THIS NEED TO BE WITHIN THE do_categories=False CASE??]
    # Add values for bad/over/under:
    # Note we're not hardcoding an alpha value.
    # The user can specify it through badcol by using an rgba tuple,
    # e.g. (1,0,1,0.5) would be semitransparent magenta.
    if badcol is not None:
        cmap.set_bad(color=badcol)

    # Require the user to have specified overcol and undercol:
    cmap.set_over(color=overcol)
    cmap.set_under(color=undercol)

    # Set plot limits.
    # For some projections (Robinson!),
    # it only makes sense to use them globally,
    # but setting global extents seems to confuse it.
    # So we have an override option:
    if showglobal:
        ax.set_global()
    else:
        # A previous version prevented specifying Axes extents
        # if we used the ccrs.OSGB() projection;
        # now we have a better projection,
        # I've removed that special case, letting it get confused
        # if anyone uses it...

        # Get the x/y limits from the data if they're not specified:
        if not xlims:
            raise UserWarning("Not sure how to get x-limits if not specified!")
        if not ylims:
            raise UserWarning("Not sure how to get y-limits if not specified!")

        # And set the Axes limits in lat/lon coordinates:
        ax.set_extent(xlims + ylims, crs=ccrs.PlateCarree())

    # Only label the axes if we're in the Plate Carrée projection:
    if proj == ccrs.PlateCarree():
        ax.set_xlabel(r"Longitude")
        ax.set_ylabel(r"Latitude")

    if stock_img:
        ax.stock_img()

    # Plot the data!
    for i, region in enumerate(regions):
        reg_name = region.attributes[reg_key]
        if reg_name not in regdata_dict.keys():
            continue
        else:
            val = regdata_dict[reg_name]

        if math.isnan(val):
            continue

        facecolor = cmap(normalizer([val]))

        # Project region, if necessary:
        reg_proj = region.attributes['projection_forUKCP']
        if reg_proj != proj:
            region_geometry = proj.project_geometry(
                region.geometry, src_crs=reg_proj)
        else:
            region_geometry = region.geometry

        # Indicators about significance:
        # NOTE that currently hatching styling is HARDCODED in the pdf backend,
        #      so it will look different in the pdf and png outputs.
        # e.g.
        # http://matplotlib.org/examples/pylab_examples/contourf_hatching.html
        # http://matplotlib.1069221.n5.nabble.com/Change-hatch-intensity-color-for-PDF-backend-td27412.html
        # https://github.com/matplotlib/matplotlib/blob/9ca2c4118f684b4e145bd109008f77731d2d7cd4/lib/matplotlib/backends/backend_pdf.py#L1061
        # So, I'll just use a fairly intense hatch for now,
        # and see how we go.
        #
        # NOT IMPLEMENTED DATA STRUCTURES FOR THIS YET:
        # if regional_sigs is not None:
        #    if regional_sigs[region.tag]:
        #        hatchsty = None
        #        sigtag   = "*"
        #        edgecolor= regionlcol
        #    else:
        #        #hatchsty = "..." # Dots are too faint in pdfs
        #        hatchsty  = "////\\\\"
        #        sigtag   = "-"
        #        edgecolor= "black"
        #        #facecolor="dimgrey"
        # else:
        #    hatchsty = None
        #    sigtag   = "-"
        #    edgecolor= regionlcol
        hatchsty = None
        edgecolor = regionlcol
        #
        # Output to terminal:
        log.debug("Region {}: '{}'. Value = {}, colour ={}".format(
            i, reg_name, val, facecolor))

        # Plot it:
        _ = ax.add_geometries([region_geometry], proj,
                              facecolor=facecolor,
                              edgecolor=edgecolor, linewidth=regionlw,
                              hatch=hatchsty)

    # Add gridlines (and label them on the axes, IF we're in PlateCarree)
    gridlabels = (proj == ccrs.PlateCarree())
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=gridlabels,
                      linewidth=0.5, color="grey")
    if gridlabels:
        # Options to switch on/off individual axes labels:
        gl.xlabels_bottom = xgridax[0]
        gl.xlabels_top = xgridax[1]
        gl.ylabels_left = ygridax[0]
        gl.ylabels_right = ygridax[1]

    # Set limits for the grid separate to the plot's xlims/ylims:
    if showglobal:
        xlims_for_grid = [-180, 180]
        ylims_for_grid = [-90, 90]
    else:
        xlims_for_grid = xlims if xlims is not None else [
            dcube_masked.coord('longitude').points.min(),
            dcube_masked.coord('longitude').points.max()]
        ylims_for_grid = ylims if ylims is not None else [
            dcube_masked.coord('latitude').points.min(),
            dcube_masked.coord('latitude').points.max()]

    xgridrange = [dxgrid * np.round(val / dxgrid) for val in xlims_for_grid]
    ygridrange = [dygrid * np.round(val / dygrid) for val in ylims_for_grid]

    xgridpts = np.arange(xgridrange[0], xgridrange[1] + dxgrid, dxgrid)
    ygridpts = np.arange(ygridrange[0], ygridrange[1] + dygrid, dygrid)
    # Filter in case the rounding meant we went off-grid!
    xgridpts = [xgridpt for xgridpt in xgridpts if (
        xgridpt >= -180 and xgridpt <= 360)]
    ygridpts = [ygridpt for ygridpt in ygridpts if (
        ygridpt >= -90 and ygridpt <= 90)]

    gl.xlocator = mticker.FixedLocator(xgridpts)
    gl.ylocator = mticker.FixedLocator(ygridpts)
    if gridlabels:
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

    # Adjust the margins:
    if newfig:
        # We could legally do this even if this wasn't a new figure,
        # (we've got the figure object using gcf() above),
        # but in practice we'll be designing the multipanel figure
        # elsewhere, and that is where the margins should be set.
        if (marlft is None and marrgt is None and martop is None and
                marbot is None):
            plt.tight_layout()
        else:
            fig.subplots_adjust(left=marlft,  bottom=marbot,
                                right=marrgt,  top=martop,
                                wspace=marwsp,  hspace=marhsp)
    # (note that we have a wrapper, plotgeneral.set_standard_margins(),
    # which does this for a StandardMap object)

    # (need to make a ScalarMappable ourselves as we don't have an image,
    # http://stackoverflow.com/questions/8342549/matplotlib-add-colorbar-to-a-sequence-of-line-plots
    # )
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=normalizer)
    sm._A = []  # fake up the array of the scalar mappable. Urgh...
    # Colour bar:
    if bar_orientation.lower() == "none":
        log.debug("Skipping colour bar")
    else:
        if do_categories:
            ticklabs = level_tick_labs
            ticklen = 4  # points
        else:
            ticklabs = None
            ticklen = 0

        make_colourbar(fig, bar_orientation, extendcolbar, levels, barlabel,
                       colmappable=sm, bar_pos=bar_position, ticklen=ticklen,
                       ticklabs=ticklabs)

    # Finally, make the plot, if we've provided any filenames:
    if outfnames is not None:
        # This saves to any filenames if specified, and/or displays to screen,
        # closes the plot and resets the font family & size.
        end_figure(outfnames, dpi=dpi, oldfont_family=oldfont_family,
                   oldfont_size=oldfont_size)

    else:
        log.debug("No outfnames provided, continue plotting using Axes ax")

    log.debug("All done in plot_map, returning")

    return (ax, sm)


def _get_mplcolmap_from_file(color_txt_file, reverse=False, ncols=None):
    """
    This reads in a text file of rgb colours,
    (formatted as 3 space-separeted values from 0 to 1 on each line,
    representing r,g,b) and turns them into a matplotlib colormap.

    This is based on a function Neil Kaye found online somewhere.
    """
    LinL = np.loadtxt(color_txt_file)  # 12*3 element array

    b3 = LinL[:, 2]  # n-element list: value of blue at each point.
    b2 = LinL[:, 2]  # Same!
    # position of each of the n values: ranges from 0 to 1
    b1 = np.linspace(0, 1, len(b2))

    # setting up columns for list
    g3 = LinL[:, 1]
    g2 = LinL[:, 1]
    g1 = np.linspace(0, 1, len(g2))

    r3 = LinL[:, 0]
    r2 = LinL[:, 0]
    r1 = np.linspace(0, 1, len(r2))

    # creating list.
    # Each are n-element lists of 3-element tuples
    R = zip(r1, r2, r3)
    G = zip(g1, g2, g3)
    B = zip(b1, b2, b3)

    # transposing list
    # n-element list of 3-element tuples of 3-element tuples
    RGB = zip(R, G, B)
    rgb = zip(*RGB)  # 3-element list of 12-element tuple of 3-element tuples

    # creating dictionary
    keys = ['red', 'green', 'blue']
    LinearL = dict(zip(keys, rgb))  # makes a dictionary from 2 lists
    # Value for each key is a 12-element tuple of 3-element tuples.

    if reverse:
        LinearL = mpl_cm.revcmap(LinearL)

    if ncols is None:
        my_cmap = mpl_col.LinearSegmentedColormap('my_colormap', LinearL)
    else:
        my_cmap = mpl_col.LinearSegmentedColormap(
            'my_colormap', LinearL, N=ncols)

    return my_cmap


def _setup_colourmap(cpal, vrange, vstep, vmid=None):
    """
    Creat a matplotlob colormap object
    according to the colour palette specified (the string cpal),
    the value range and step size (vrange 2-element list/tuple, and vstep),
    skewing it appropriately if a midpoint value is given (vmid).

    If cpal starts with "UKCP_", then it is loaded from a text file!
    These text files can be generated from Neil Kaye's ClimPal tool
    https://www.metoffice.gov.uk/hadobs/climviz/climpal/
    """
    levels = np.arange(vrange[0], vrange[1] + vstep, vstep)
    if vmid is None:
        # Usual case.
        # (note that specifying levels forces cmap to be discrete,
        #  but ensures consistency between contourf & pcolormesh)
        if cpal.startswith("UKCP_"):
            reverse = cpal.endswith("_r")
            filename = (cpal[:-2] if reverse else cpal) + ".txt"
            col_file = path.join(ROOT_DIR, 'ukcp_dp/plotters/utils', filename)
            log.debug("Attempting to read colour palette from {}".format(
                col_file))
            cmap = _get_mplcolmap_from_file(
                col_file, reverse=reverse, ncols=len(levels) - 1)
        else:
            cmap = mpl_cm.get_cmap(cpal, len(levels) - 1)

    else:
        # Explicit midpoint specified, make an off-centre (skewed) colourbar.
        # Based on a colourbar that extends an equal distance either side of
        # the midpoint, but is then cropped to the value range selected.

        # First, get whichever is the biggest distance above or below vmid:
        deltamax = max(vrange[1] - vmid, vmid - vrange[0])
        # Full range either side of vmid
        vfull = [vmid - deltamax, vmid + deltamax]
        # levfull = np.arange( vfull[0], vfull[1], vstep ) # Levels over full
        # value range

        ncols = len(levels) - 1  # number of colours we actually want to use

        # We'll map 0-1 to vfull[0]--vfull[1] (size: 2*deltamax),
        # so we need to know how far along vrange[0] and vrange[1] are.
        vlo_frac = (vrange[0] - vfull[0]) / (2.0 * deltamax)  # 0 or greater
        vhi_frac = (vrange[1] - vfull[0]) / (2.0 * deltamax)  # 1 or less
        # (one of these two must be 0 or 1)

        if cpal.startswith("UKCP_"):
            reverse = cpal.endswith("_r")
            filename = (cpal[:-2] if reverse else cpal) + ".txt"
            col_file = path.join(ROOT_DIR, 'ukcp_dp/plotters/utils', filename)
            log.debug("Attempting to read colour palette from {}".format(
                col_file))
            cmap_base = _get_mplcolmap_from_file(col_file, reverse=reverse)
        else:
            cmap_base = mpl_cm.get_cmap(cpal)  # maps the range 0-1 to colours

        cols = cmap_base(np.linspace(vlo_frac, vhi_frac, ncols))
        cmap = mpl_col.LinearSegmentedColormap.from_list(
            'skewed', cols, N=ncols)

    return cmap
