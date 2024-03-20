import calendar
import logging

import matplotlib
from matplotlib.ticker import MaxNLocator

import cf_units
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np


LOG = logging.getLogger(__name__)

# Force matplotlib to use True Type fonts
# (the default is Type 3, pdf.fonttype 3)
# http://phyletica.org/matplotlib-fonts/
matplotlib.rcParams["pdf.fonttype"] = 42


def start_figure(cmsize, dpi_display, fontfam, fsize, figbackgroundcol=None):
    """
    Set up a figure object.
    The arguments can be taken from a StandardMap object,
    but there's a handy wrapper for that below...

    cmsize:  Size in cm of the Figure, as a tuple/list: (width,height)
    dpi_dispaly:  Onscreen resolution of the Figure, in dots per inch
                  (NOT necessarily the print resolution!
                   That is set when saving the figure to a file)
    fontfam: Font family name
    fsize:   Font size, in points
    figbackgroundcol: Colour to use for the Figure object background

    The font family and size are set globally
    by editng the matplotlib.rcParams.
    To prevent odd side-effects in other plots,
    the original font family and size are returned,
    in a tuple alongsize the Figure object itself.
    """

    # Change overall font family:
    oldfont_family = matplotlib.rcParams["font.family"]
    matplotlib.rcParams["font.family"] = fontfam
    # (Default is 'sans-serif',
    # which is 'Bitstream Vera Sans','DejaVu Sans', 'Lucida Grande',... )
    # To see a list of available font families, do:
    # sorted(set([f.name for f in matplotlib.font_manager.fontManager.afmlist+
    # matplotlib.font_manager.fontManager.ttflist]))

    # Do the same sort of thing with size:
    oldfont_size = matplotlib.rcParams["font.size"]
    matplotlib.rcParams["font.size"] = fsize  # Default is 12

    # Set up the figure:
    size_inches = [aside / 2.54 for aside in cmsize]
    fig = plt.figure(figsize=size_inches, dpi=dpi_display)

    # Specify the Figure background colour:
    # The user can specify the alpha by using an rgba tuple,
    # e.g. (1,0,1,0.5) would be semitransparent magenta.
    if figbackgroundcol is not None:
        fig.patch.set_facecolor(figbackgroundcol)
        # fig.patch.set_alpha(1.0)

    return fig, oldfont_family, oldfont_size


def start_standard_figure(settings):
    """
    Wrapper to start_figure() above,
    but taking the arguments from 'settings',
    which is probably a StandardMap object, or similar.

    Again, the original font family and size are returned,
    in a tuple alongside the Figure object itself.
    """
    fig, oldfont_family, oldfont_size = start_figure(
        settings.cmsize,
        settings.dpi_display,
        settings.fontfam,
        settings.fsize,
        settings.figbackgroundcol,
    )
    return fig, oldfont_family, oldfont_size


def end_figure(outfnames, dpi=None, oldfont_family=None, oldfont_size=None):
    """
    Do all the complicated logic related to
    finishing off a figure - plotting to screen/file, and closing.

    Because the "print" dpi doesn't have to be the same as the "display" dpi,
    we can pass it in here, e.g. from a StandardMap object.
    If not provided, the figure's display dpi will be used,
    which could be much lower.


    oldfont_family and oldfont_size can be provided,
    in which case the matplotlib.rcParams are restored
    to those original values after plotting.
    """
    # Loop over strings in the outfnames list
    # (allows us to write to different devices efficiently):

    if dpi is None:
        dpi = plt.gcf().dpi

    # First, ensure that outfnames IS a list:
    if isinstance(outfnames, str):
        outfnames = [outfnames]
    showit = False
    for outf in outfnames:
        extn = outf.split(".")[-1].lower()
        if extn == "x11":
            showit = True
        else:
            # We have to explicitly set the "saved" Figure colour
            # to what we (might have) specified earlier:
            plt.savefig(
                outf, dpi=dpi, facecolor=plt.gcf().get_facecolor(), edgecolor="none"
            )
            LOG.debug("Plot saved to %s", outf)

    if showit:
        plt.show()  # Have to do this last, it clears the Figure

    # If we made a plot, then close it:
    # plt.close() ## Allows memory to be freed, prevents a warning.
    plt.close("all")  # Allows memory to be freed, prevents a warning.

    # Reset font:
    LOG.debug("Plot closed")
    if oldfont_family is not None:
        LOG.debug("Resetting font family")
        matplotlib.rcParams["font.family"] = oldfont_family
    if oldfont_size is not None:
        LOG.debug("Resetting font size")
        matplotlib.rcParams["font.size"] = oldfont_size


def get_time_series(cube, slice_and_sel_coord):
    """
    Get the time series from the cube.

    Convert the time coord into fractions of years so we can easily use it for plotting.

    @param cube (Cube): an iris data cube
    @param slice_and_sel_coord (str): the name of the coord to slice over

    @return a list of time values

    """
    if slice_and_sel_coord is not None:
        tcoord = cube.slices_over(slice_and_sel_coord).next().coord("time")
    else:
        tcoord = cube.coord("time")

    if tcoord.units.calendar is not None:
        tsteps = list(tcoord.units.num2date(tcoord.points))

        if (
            isinstance(tsteps[0], (dt.date, dt.datetime))
            or tcoord.units.calendar == "standard"
        ):
            tpoints = [
                t.year
                + t.timetuple().tm_yday / (366.0 if calendar.isleap(t.year) else 365.0)
                for t in tsteps
            ]

        elif isinstance(
            tsteps[0],
            (cf_units.cftime.datetime, cf_units.cftime._cftime.Datetime360Day),
        ):
            if tcoord.units.calendar == "360_day":
                tpoints = [t.year + t.dayofyr / 360.0 for t in tsteps]
            else:
                raise Exception(
                    "Got time points as cftime objects, "
                    "but NOT on a 360-day calendar."
                )

        else:
            LOG.warning(
                "Using num2date on the time coord points didn't give "
                "standard or netcdf date/datetime objects. The time "
                "coord units were:%s, num2date gave objects of type "
                "%s",
                units=tcoord.units,
                type=type(tsteps[0]),
            )
            raise Exception("Unrecognised time coord data type, cannot plot")

    else:
        # Non-date time coord, like a year! Simples!
        LOG.info(
            "Time coord points are not date-like objects, ASSUMEING they "
            "are in year-fractions."
        )
        tpoints = tcoord.points

    return tpoints


def make_colourbar(
    fig,
    bar_orientation,
    extendcolbar,
    levels,
    barlabel,
    colmappable=None,
    bar_pos=None,
    ticklen=0,
    ticklabs=None,
):
    """
    Create a colour bar Axes for maps.

    fig is the Figure object,
    bar_orientation is "horizontal" or "vertical"
    extendcolbar is 'neither', 'min', 'max', or 'both'.

    levels is the list of values used for the tick marks,
    and should be the same as the levels in the colour bar itself!

    barlabel is the string to use as the colourbar label.

    colmappable will usually be the thing
    returned from contourf or pcolormesh.

    bar_pos is a list of [left,bottom,width,height]
    used to explicitly create the colourbar Axes.

    ticklen is the length of the tickmarks in the bar;
    usually you'd want them gone (ticklen=0),
    but you might want to set this if using discrete catagories.

    if ticklabs is present, it will be used for the tick labels.
    """
    if bar_pos is not None:
        bar_axes = fig.add_axes(bar_pos)
    else:
        bar_axes = None

    colour_bar = fig.colorbar(
        colmappable,
        cax=bar_axes,
        orientation=bar_orientation,
        drawedges=False,
        extend=extendcolbar,
    )
    colour_bar.ax.tick_params(length=ticklen)
    colour_bar.set_ticks(levels)

    if ticklabs is not None:
        colour_bar.set_ticklabels(ticklabs)

    if barlabel is not None:
        colour_bar.set_label(barlabel)

    return colour_bar


def make_standard_bar(settings, fig, barlabel=None, colmappable=None, bar_pos=None):
    """
    Wrapper to make_colourbar above,
    but taking the arguments from 'settings',
    which is probably a StandardMap object, or similar


    fig is the Figure object,
    barlabel is the string to use as the colourbar label.
    (taken from settings.default_barlabel if None)

    colmappable will usually be the thing
    returned from contourf or pcolormesh.

    bar_pos is a list of [left,bottom,width,height]
    used to explicitly create the colourbar Axes.
    (taken from settings.bar_position if None)
    """
    # Compute the levels for the tickmarks
    # from the map value range and steps
    # used to define the colour map originally.
    levels = np.arange(
        settings.vrange[0],
        settings.vrange[1] + settings.vstep * settings.bar_tick_spacing,
        settings.vstep * settings.bar_tick_spacing,
    )

    # Same procedure as mapper.plot_standard_map():
    # Use the settings' default barlabel if one wasn't specified,
    # but make it easy to override the default.
    if barlabel is None:
        barlabel = settings.default_barlabel

    if bar_pos is None:
        bar_pos = settings.bar_position

    colour_bar = make_colourbar(
        fig,
        settings.bar_orientation,
        settings.extendcolbar,
        levels,
        barlabel,
        colmappable=colmappable,
        bar_pos=bar_pos,
    )
    return colour_bar


def set_x_limits(cube, ax):
    """
    Set the x limits for the plot.

    @param cube (Cube): an iris data cube
    @param ax (AxesSubplot): the sub-plot

    """
    # Get x-axis limits from the Cube's time coord.
    tcoord = cube.coord("time")
    # Do this differently for datetime-like coords vs integer coords:
    if tcoord.units.calendar is not None:
        if tcoord.units.name.startswith("hour"):
            # Can't easily use dt.timedelta objects with netcdfdatetimes,
            # which is likely to be what these are.
            xlims = [
                tcoord.units.num2date(tcoord.points[0]),
                tcoord.units.num2date(tcoord.points[-1]),
            ]
        elif tcoord.units.name.startswith("day"):
            # Can't easily use dt.timedelta objects with netcdfdatetimes,
            # which is likely to be what these are.
            xlims = [
                tcoord.units.num2date(tcoord.points[0]),
                tcoord.units.num2date(tcoord.points[-1]),
            ]
        else:
            raise Exception(
                "Time coord units are "
                + str(tcoord.units)
                + " but I can only handle days and hours!"
            )
    else:
        # x-axis will be in units of integer years.
        LOG.info(
            "Time coord points are not date-like objects, ASSUMEING they "
            "are in year-fractions."
        )
        tsteps = tcoord.points
        xlims = [tsteps[0], tsteps[-1]]

    # Now we've got proposed x-axis limits (as some data type),
    # we convert those x-axis limits into fractions of years.
    if isinstance(xlims[0], (dt.date, dt.datetime)):
        xlims_touse = [
            t.year
            + t.timetuple().tm_yday / (366.0 if calendar.isleap(t.year) else 365.0)
            for t in xlims
        ]

    elif isinstance(
        xlims[0], (cf_units.cftime.datetime, cf_units.cftime._cftime.Datetime360Day)
    ):
        # Strictly-speaking, this might not be on a 360-day calendar,
        # but in practice we're unlikely to get this kind of object
        # unless a 360-day calendar is involved.
        LOG.info(
            "Time axis limits specified with cftime.datetime "
            "objects, ASSUMEING they're on a 360-day calendar."
        )
        xlims_touse = [t.year + t.dayofyr / 360.0 for t in xlims]

    elif isinstance(xlims[0], (float, int)):
        xlims_touse = xlims

    else:
        raise Exception(
            "Unacceptable format for x-limits! Please use "
            "standard or netcdf date/datetime objects, or ints or "
            "floats."
        )

    # Finally, apply the limits:
    ax.set_xlim(xlims_touse)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))


def wrap_string(text, width):
    """
    Wrap a string so that each line is no more than <width> characters long.
    Insert line breaks to wrap.
    This is to enable titles to be plotted without overlapping the logos.
    """
    # split the string so that we can recombine into a new string with line
    # breaks at the wrap width
    split_text = text.split(" ")
    new_text = ""
    new_line_length = 0
    for st in split_text:
        # if it's over the width then add a line break and reset the line length
        # counter
        if new_line_length + len(st) > width:
            new_line_length = 0
            new_text += "\n"
        # add the string plus a space to the new string and increase the line length
        new_text += st + " "
        new_line_length += len(st) + 1

    # now to try to align vertically
    if new_text.count("\n") == 0:
        new_text = f"\n\n{new_text}"
    elif new_text.count("\n") < 3:
        new_text = f"\n{new_text}"

    return new_text
