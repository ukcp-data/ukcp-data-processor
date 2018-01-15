# -*- coding: utf-8 -*-
'''
Functions for plotting time series, plumes etc.
i.e. showing a parameter with some measure of time on the x-axis.

You would usually import this module with:
import ukcp_standard_plots.timeseries as ukcpts

--------------------------------------------------------
Contents:

plot_ts():
   This is the main function for plotting timeseries...
--------------------------------------------------------




'''
#=========================================================================
import sys
import iris
import iris.coord_categorisation
import cf_units
import cartopy.crs as ccrs
#import nc_time_axis
import numpy as np
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import itertools

import plotting_general as plotgeneral

from  ukcp_dp.ukcp_common_analysis import common_analysis as common


# Force matplotlib to use True Type fonts
# (the default is Type 3, pdf.fonttype 3)
# http://phyletica.org/matplotlib-fonts/
matplotlib.rcParams['pdf.fonttype'] = 42
#=========================================================================



#=========================================================================

def plot_ts(d_in, fig=None, ax=None,
            preferred_unit=None, cmsize=(25,10),fsize=11,
            tcoordname='time', slice_and_sel_coord="realization",
            #membercols=["#999999"], memberalpha=0.5, memberlw=1.0,
            membercols=["#A1A0AA"], memberalpha=0.5, memberlw=1.0,
            selmembers=None, 
            #selmembercols=["#3399bb"], selmemberalpha=1.0, selmemberlw=2.0,
            selmembercols=["#007AA9"], selmemberalpha=1.0, selmemberlw=2.0,
            quantiles=None, quantcol="#B9DC0C", quantalpha=0.5,
            xgridcol="lightgrey", ygridcol="lightgrey",
            xlims=None, dxlab_years=10, dxtick_years=5,
            ylims=None, ylab=None,
            marlft=None, marrgt=None, martop=None, marbot=None, 
            marwsp=None, marhsp=None, 
            outfnames=["x11"], verbose=False ):
    '''
    Make a single panel plot of a timeseries.

    d_in ("data, input") is a cube with one time-like dimension, 
    and another dimension we can slice over (like realization).

    The time coord might actually be times (Datetime objects or netcdftime objects)
    or you could use integers like in a year or season_year AuxCoord.
    That might be much simpler when comparing different data sets!
    
    In any case, the x-axis points, limits and tick marks are converted
    into fractions-of-years. 
    This allows the maximum interoperability and simiplicity between data sets,
    for our case where we're usually looking over many years.


    Most members are plotted with the membercols, memberalpha and memberlw 
    styling. membercols is turned into a cyclic iterator (i.e. the colours will loop)
    If memberlw is not > 0 (e.g. =0 or =None) then lines are not plotted.

    One or more members can be picked out for highighting,
    provided as a list of ints (e.g. selmembers = [1100834, 1102089] ),
    with the styles selmembercols, selmemberalpha, selmemberlw.

    Quantiles of the member distribution at each time step can be plotted,
    by providing a 2-element list/tuple to the quantiles argument.
    e.g. the max and min can be shaded using quantiles=[0,100]
    (note they're given as percentages, not unit fractions!!)
    The colour and translucency of the shading is given by quantcol & quantalpha.


    The x-axis (time) and y-axis limits can be specified by xlims & ylims,
    but will be chosen automatically if those arguments are None.
    xlims should be given as fractions of years, e,g. [1950, 1980.6]

    dxlab_years  is the spacing between x-axis tick labels, in years
    dxtick_years is the spacing between x-axis tick marks,  in years.

    ylab is the y-axis label (usually related to the variable & units in question)
    ylims is a tuple/list giving the y-axis limits (chosen automatically if None)

    Gridlines will be plotted if their colours (xgridcol, ygridcol) are not None.

    The margins are given by the mar??? arguments just as for the map plots;

    
    The plot is saved/displayed if outfnames is not None.
    (otherwise you can continue plotting afterwards, 
     as the function returns its Axes object for further use.)
    '''
    ##---------------------------------------------------------------
    # Just check some things first:
    assert isinstance(dxtick_years, int), \
        "dxtick_years must be an int, but yours was a "+str(type(dxtick_years))+"!"
    assert isinstance(dxlab_years, int), \
        "dxlab_years must be an int, but yours was a "+str(type(dxlab_years))+"!"
    ##---------------------------------------------------------------

   
    ## FIRST THING is to convert the unit of the data cube, if required.
    # (if not, just point dcube to the input cube without a copy)
    if preferred_unit is not None:
        if d_in.units != preferred_unit:
            print "NOTE: converting input cube units (in a copy) from "+d_in.units.name + \
                " to "+preferred_unit.name + "..."
            d = d_in.copy()

            # Got a function to do all this now:
            common.rectify_units(d, target_unit=preferred_unit)
        else:
            # Already in the right units
            d = d_in

    else:
        # No preferred unit, leave as it is:
        d = d_in


    # Show the value range, and the units:
    if verbose:
        print "Input cube value ranges: "
        print d.data.min(), d.data.max(), d.units.title("")
    ##---------------------------------------------------------------


    ##---------------------------------------------------------------
    if fig is None:
        newfig  = True
        fontfam = "Arial"
        dpi     = 94
        fig, oldfont_family,oldfont_size = plotgeneral.start_figure(cmsize,dpi,
                                                                    fontfam,fsize,
                                                                    figbackgroundcol="white" )
    else:
        # Figure object already exists.
        newfig = False
        if verbose: print "(Figure object provided, not using cmsize or fsize arguments)"
    #------------------------------------------------------------


    ##---------------------------------------------------------------
    # Set up the Axes object:
    if ax is None:
        newaxes = True
        ax = plt.axes()
    else:
        # Already got an Axes object:
        newaxes = False
    ##---------------------------------------------------------------

    
    #---------------------------------------------------------------
    # Set up axis details of the plot:

    #---------------------------------------------------------------
    if ylab is None:
        ylab = d.name() + " " + d.units.title("")
    ax.set_ylabel(ylab)
    if ylims is not None:
        ax.set_ylim(ylims)


    ax.set_xlabel('Date')
    if xlims is None:
        # Get x-axis limits from the Cube's time coord.
        tcoord = d.coord(tcoordname)
        # Do this differently for datetime-like coords vs integer coords:
        if tcoord.units.calendar is not None:
            if tcoord.units.name.startswith('hour'):
                # Can't easily use dt.timedelta objects 
                # with netcdfdatetimes, which is likely
                # to be what these are.
                #
                # Place the limits at ±1 year around the first & last time points:
                xlims = [ tcoord.units.num2date(tcoord.points[ 0] - 24*360),
                          tcoord.units.num2date(tcoord.points[-1] + 24*360)  ]
            else:
                raise UserWarning("Time coord units are "+str(tcoord.units) \
                                      + " but I can only handle hours!")
        else:
            # x-axis will be in units of integer years.
            # Place the limits at ±1 year around the first & last time points:
            print "   WARNING: time coord points are not date-like objects,"
            print "            so I'm going to ASSUME they are in year-fractions."
            tsteps = tcoord.points
            xlims = [tsteps[ 0] - 1.0, 
                     tsteps[-1] + 1.0 ] 

        if verbose: print "Computed x-axis limits: ",xlims
    
    # Now we've got proposed x-axis limits (as some data type),
    # we convert those x-axis limits into fractions of years.
    if isinstance(xlims[0], dt.date) or isinstance(xlims[0],dt.datetime):
        xlims_touse = [t.year    + t.timetuple().tm_yday /               \
                           (366.0 if calendar.isleap(t.year) else 365.0) \
                           for t in xlims]
        
    elif isinstance(xlims[0], cf_units.netcdftime.datetime):
        # Strictly-speaking, this might not be on a 360-day calendar,
        # but in practice we're unlikely to get this kind of object
        # unless a 360-day calendar is involved.
        # Still, we'll give a warning.
        print "   WARNING: time axis limits specified with netcdftime.datetime objects"
        print "            I'm going to ASSUME they're on a 360-day calendar."
        xlims_touse = [t.year + t.dayofyr / 360.0   for t in xlims]

    elif isinstance(xlims[0], float) or isinstance(xlims[0], int):
        xlims_touse = xlims
        
    else:
        raise UserWarning("Unacceptable format for x-limits!\n"\
                         +"Please use standard or netcdf date/datetime objects," \
                         +" or ints or floats.")

    # Finally, apply the limits:
    if verbose: print "Computed x-axis limits in year-fractions: ",xlims_touse
    ax.set_xlim(xlims_touse)


    #--------------------------------------------------------------------------
    # Set these up as fractions of years. (Actually, integers in practice)
    # Minor x-axis ticks:
    xtks_minor_lims = [round(xlims_touse[0]/float(dxtick_years))*dxtick_years - dxtick_years, 
                       round(xlims_touse[1]/float(dxtick_years))*dxtick_years + dxtick_years]
    xtks_minor = np.arange(xtks_minor_lims[0], xtks_minor_lims[1]+dxtick_years,
                           dxtick_years)
    xtks_minor = xtks_minor[np.logical_and( xtks_minor>=xlims_touse[0], xtks_minor<=xlims_touse[1] )]
    if verbose: print "Tick marks (x, minor):\n  ",xtks_minor
    ax.set_xticks(xtks_minor, minor=True)


    # Major x-axis ticks, with labels:
    xtks_lims = [round(xlims_touse[0]/float(dxlab_years))*dxlab_years - dxlab_years, 
                 round(xlims_touse[1]/float(dxlab_years))*dxlab_years + dxlab_years]
    xtks_major = np.arange(xtks_lims[0], xtks_lims[1]+dxlab_years,
                           dxlab_years)
    xtks_major = xtks_major[np.logical_and( xtks_major>=xlims_touse[0], xtks_major<=xlims_touse[1] )]
    if verbose: print "Tick marks (x, major):\n  ",xtks_major
    
    xtklabs = ["{:4.0f}".format(xtk) for xtk in xtks_major] 
    ax.set_xticks(xtks_major)
    ax.set_xticklabels(xtklabs)
    #--------------------------------------------------------------------------    


    
    ##-------------------------------------------------------------------
    # Add gridlines?
    # (plot underneath everything else)
    if xgridcol is not None: ax.grid(axis="x", linestyle="-",color=xgridcol, zorder=1)
    if ygridcol is not None: ax.grid(axis="y", linestyle="-",color=ygridcol, zorder=1)

    # Add fiducial line at zero:
    if verbose: print "***WARNING: No option for fiducial lines yet ***"
    #fiducial = ax.axhline(y=0, marker="",linestyle="-", color="grey")
    ##-------------------------------------------------------------------



    ##-------------------------------------------------------------------
    # Main plotting:
    membercolcyc    = itertools.cycle(   membercols)
    selmembercolcyc = itertools.cycle(selmembercols)

    # Convert the time coord into fractions of years,
    # so we can easily use it for plotting:
    tcoord = d.slices_over(slice_and_sel_coord).next().coord(tcoordname)
    if tcoord.units.calendar is not None:
        tsteps = list(tcoord.units.num2date(tcoord.points))
        if isinstance(tsteps, dt.date) or isinstance(tsteps,dt.datetime):
            tpoints = [t.year    + t.timetuple().tm_yday /               \
                           (366.0 if calendar.isleap(t.year) else 365.0) \
                           for t in tsteps]

        elif isinstance(tsteps[0], cf_units.netcdftime.datetime):
            if tcoord.units.calendar=="360_day":
                tpoints = [t.year + t.dayofyr / 360.0   for t in tsteps]
            else:
                raise UserWarning("SURPRISE! Got time points as netcdftime objects,\n" + \
                                  "          but NOT on a 360-day calendar.\n" + \
                                  "          What's all that about then??")
        else:
            print "Using num2date on the time coord points didn't give\n" +\
                                  "standard nor netcdf date/datetime objects.\n" +\
                                  "Not sure what to do about that."
            print "The time coord units were:", tcoord.units
            print "num2date gave objects of type ",type(tsteps[0])
            raise UserWarning("Unrecognised time coord data type, cannot plot :(")

    else:
        # Non-date time coord, like a year! Simples!
        print "   WARNING: time coord points are not date-like objects,"
        print "            so I'm going to ASSUME they are in year-fractions."
        tpoints = tcoord.points




    # Quantile shading (if requested):
    if quantiles is not None:
        try:
            assert len(quantiles)==2, "Quantiles provided, but the wrong length."
        except TypeError:
            raise UserWarning("Quantiles provided, but not a list/tuple.")
        # Now get each quantile separately:
        ALPHAP = 1  # default
        BETAP  = 1  # default
        # See here for details of these parameters,
        # which govern the interpolation to get the quantiles.
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mstats.mquantiles.html
        # Margaret's routine ~frgo/wave/calc_quantiles_mdi.pro
        # corresponds to alphap=0,betap=0 (R type 6)
        # alphap=0,betap=1 ==> linear interpolation of CDF, as in R type 4 
        #                     (and my getpercentilevalues.pro IDL routine)
        # alphap=1,betap=1 (SciPy default) is R's type 7, and is also R's default.
        #
        lovals = d.collapsed(slice_and_sel_coord, iris.analysis.PERCENTILE, 
                                 percent=quantiles[0], alphap=ALPHAP, betap=BETAP)
        hivals = d.collapsed(slice_and_sel_coord, iris.analysis.PERCENTILE,
                                 percent=quantiles[1], alphap=ALPHAP, betap=BETAP)
        if verbose:
            print "PLOTTING QUANTILES at "
            print tpoints
            print lovals.data
            print hivals.data
        _=ax.fill_between(tpoints, lovals.data, y2=hivals.data,
                          edgecolor="none", linewidth=0, 
                          facecolor=quantcol, alpha=quantalpha, zorder=100 )
        

        
        

    # Plot lines:
    # Iterate over slice_and_sel_coord
    # (usually "realization", hence referring to slices as "members")
    for amember in d.slices_over(slice_and_sel_coord):      
        realization = amember.coord(slice_and_sel_coord).points[0]
                        
        if realization not in selmembers:
            if memberlw > 0:
                # Standard case:
                _=ax.plot(tpoints, amember.data, linestyle="-",marker="None",
                          color=membercolcyc.next(), alpha=memberalpha,
                          linewidth=memberlw, label=str(realization), zorder=2 )
        else:
            # Special case:
            _=ax.plot(tpoints, amember.data, linestyle="-",marker="None",
                      color=selmembercolcyc.next(), alpha=selmemberalpha,
                      linewidth=selmemberlw, label=realization, zorder=200 )

    ##-------------------------------------------------------------------


    # Skip legend...
    #---------------------------------------------------------------
    # Add legend if requested:
    #if legend_loc is not None:
    #    plt.legend( loc=legend_loc, fontsize="small" )
    #    # Note that the fontsize string is relative to the current default
    #    # (an int can be given to specify it in absolute points)
    #---------------------------------------------------------------




    #---------------------------------------------------------------
    if newfig:
        if marlft is None and marrgt is None and martop is None and marbot is None:
            plt.tight_layout()
        else:
            fig.subplots_adjust(left  = marlft,  bottom = marbot,
                                right = marrgt,  top    = martop,
                                wspace= marwsp,  hspace = marhsp )
    #---------------------------------------------------------------


    #---------------------------------------------------------------
    if outfnames is not None:
        if newfig:
            plotgeneral.end_figure(outfnames,
                                   oldfont_family=oldfont_family,
                                   oldfont_size=oldfont_size)
        else:
            # Having to guess what oldfont_family and oldfont_size were
            # (doesn't really matter though):
            plotgeneral.end_figure(outfnames, 
                                   oldfont_family="sans-serif",
                                   oldfont_size=12)
    else:
        if verbose: print "No outfnames provided, continue plotting using Axes ax..."
    #---------------------------------------------------------------


    print "Done in plot_ts(), returning..."
    return ax
#=========================================================================


