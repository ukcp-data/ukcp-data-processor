# -*- coding: utf-8 -*-
import logging

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


log = logging.getLogger(__name__)

# Force matplotlib to use True Type fonts
# (the default is Type 3, pdf.fonttype 3)
# http://phyletica.org/matplotlib-fonts/
matplotlib.rcParams['pdf.fonttype'] = 42


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
    oldfont_family = matplotlib.rcParams['font.family']
    matplotlib.rcParams['font.family'] = fontfam
    # (Default is 'sans-serif',
    # which is 'Bitstream Vera Sans','DejaVu Sans', 'Lucida Grande',... )
    # To see a list of available font families, do:
    # sorted(set([f.name for f in matplotlib.font_manager.fontManager.afmlist+
    # matplotlib.font_manager.fontManager.ttflist]))

    # Do the same sort of thing with size:
    oldfont_size = matplotlib.rcParams['font.size']
    matplotlib.rcParams['font.size'] = fsize  # Default is 12

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
    in a tuple alongsize the Figure object itself.
    """
    fig, oldfont_family, oldfont_size = start_figure(settings.cmsize,
                                                     settings.dpi_display,
                                                     settings.fontfam,
                                                     settings.fsize,
                                                     settings.figbackgroundcol)
    return fig, oldfont_family, oldfont_size


def end_figure(outfnames, dpi=None, oldfont_family=None, oldfont_size=None):
    """
    Do all the complicted logic related to
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
            plt.savefig(outf, dpi=dpi,
                        facecolor=plt.gcf().get_facecolor(), edgecolor='none')
            log.debug("Plot saved to {}".format(outf))

    if showit:
        plt.show()  # Have to do this last, it clears the Figure

    # If we made a plot, then close it:
    # plt.close() ## Allows memory to be freed, prevents a warning.
    plt.close('all')  # Allows memory to be freed, prevents a warning.

    # Reset font:
    log.debug("Plot closed")
    if oldfont_family is not None:
        log.debug("Resetting font family")
        matplotlib.rcParams['font.family'] = oldfont_family
    if oldfont_size is not None:
        log.debug("Resetting font size")
        matplotlib.rcParams['font.size'] = oldfont_size

    return


def make_colourbar(fig, bar_orientation, extendcolbar, levels,
                   barlabel, colmappable=None, bar_pos=None,
                   ticklen=0, ticklabs=None):
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

    bar = fig.colorbar(colmappable, cax=bar_axes, orientation=bar_orientation,
                       drawedges=False, extend=extendcolbar)
    bar.ax.tick_params(length=ticklen)
    bar.set_ticks(levels)

    if ticklabs is not None:
        bar.set_ticklabels(ticklabs)

    if barlabel is not None:
        bar.set_label(barlabel)

    return bar


def make_standard_bar(settings, fig, barlabel=None,
                      colmappable=None, bar_pos=None):
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
    levels = np.arange(settings.vrange[0],
                       settings.vrange[1] + settings.vstep *
                       settings.bar_tick_spacing,
                       settings.vstep * settings.bar_tick_spacing)

    # Same procedure as mapper.plot_standard_map():
    # Use the settings' default barlabel if one wasn't specified,
    # but make it easy to override the default.
    if barlabel is None:
        barlabel = settings.default_barlabel

    if bar_pos is None:
        bar_pos = settings.bar_position

    bar = make_colourbar(fig, settings.bar_orientation, settings.extendcolbar,
                         levels, barlabel, colmappable=colmappable,
                         bar_pos=bar_pos)
    return bar
