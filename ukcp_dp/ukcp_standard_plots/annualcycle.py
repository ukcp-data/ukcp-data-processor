# -*- coding: utf-8 -*-
'''
Functions for making annual-cycle plots, 
i.e. showing the seasonality of a parameter.
(the x-axis is always the 12 months of the year,
 with an extra Dec on the left and extra Jan on the right,
 to show continuity over the cycle
 and keep the main 12 points unobscured by tickmarks etc)


Sometimes these are called seasonal cycle or monthly cycle plots,
but in any case *these* have monthly data on the x-axis.

You would usually import this module with:
import ukcp_standard_plots.annualcycle as annualcycle


--------------------------------------------------------
Contents:

annualcycle_panel(): 
   This is the main workhorse function.
   It produces a single panel annual cycle plot,
   and has a lot of styling options.
   You'd usually use it within a wrapper function to make your particular plot.

Rather than defining a plot settings class,
like we do for plotting maps, we instead just use that master function
and write a series of wrapper functions that produce plots for particular,
standardised cases. 

As the code evolves, other functions might be moved in and out of this module.


Other functions currently:

regenerate_data_for_UKannualcycle():
   This is the simple data reduction sequence used for processing data
   for the standard annual cycle plots of UK-mean values of temp & precip.


uk_seasonalcycle_forcpmselectionfromgcm():
   This uses the data produced by the above to make UK-mean annual cycle plots
   for either temp or precip, identifying each member individually.
   This is intended for the evaluation work when choosing GCM PPE members
   to run for the CPM. 


uk_seasonalcycle_tas_pr_forevaluation():
   This uses the data produced by regenerate_data_for_UKannualcycle() above
   for both temp and precip, for means and stdevs of UK means, 
   to make a 4-panel plot for the evaluation part of the Science Report.


--------------------------------------------------------




'''
#=========================================================================
import sys
import calendar
import itertools
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import cf_units
import standards_class as stds
import plotting_general as plotgeneral
import __init__ as stdplots
from ukcp_common_analysis import common_analysis as common
from ukcp_common_analysis import io              as ukcpio
from ukcp_common_analysis import regions         as regs

# Force matplotlib to use True Type fonts
# (the default is Type 3, pdf.fonttype 3)
# http://phyletica.org/matplotlib-fonts/
matplotlib.rcParams['pdf.fonttype'] = 42
#=========================================================================








#=================================================================================
def annualcycle_panel(ppe_cube_in=None, obs_cube_in=None, fig=None, ax=None,
                      preferred_unit=None, cmsize=(11,10),fsize=12,
                      moncoord="month_number",membercoord="realization", periodic=True,
                      ppe_style=dict(lw=1,cols=["red"], ltys=["-"], quants=None,alphashade=0.2,alphaline=1),
                      obs_style=dict(lw=3,col="black",  lty="-"),  
                      ylab="Unknown", ylims=None,
                      marlft=None, marrgt=None, martop=None, marbot=None, 
                      marwsp=None, marhsp=None, xlabfmt="m", legend_loc=None,
                      outfnames=["x11"] ):
    '''
    Make a single panel plot of an annual cycle.

    ppe_cube_in is a cube usually of PPE model data to plot,
    where we show a distribution each month (e.g. over the ensemble members).
    The months used for the x-axis must be in a coord given by moncoord,
    and the distributuion is shown by slicing over the membercoord
    (although you could override this with any coord with unique values)
    
    obs_cube_in is a cube of something like observations,
    and will be plotted as a single line (i.e. no distribution)


    If a Figure or Axes object are not provided (fig and ax arguments),
    then new ones will be created from scratch.
    
    The data will be converted to the preferred_unit, if not None

    cmsize is the size in cm of the resulting figure
    fsize is the font size in points
    (these are both ignored if a Figure object is provided)

    if periodic=True then the x-axis is DJFMAMJJASONDJ,
    i.e. Dec & Jan are plotted on both sides of the graph,
    showing the continuity of the cycle.
    You can switch this off with periodic=False,
    in which case the inital Dec and final Jan are omitted.
    This makes sense when you're plotting single years for example.

    
    The aesthetics of the PPE and obs lines are given in the 
    ppe_style and obs_style dictionaries.
    Both should have a lineweight (lw),
    and the obs should have a line type and colour (lty and col);
    the PPE should have (plural: a list of) line types and colours (ltys and cols).
    These are converted into cyclical iterator (itertools.cycle)
    and implemented such that the colours vary fastest, 
    and the next linetype is chosen after each cycle of colours.

    The ppe_style dict should also have a quants option: 
    if not None, this is a 5-element list of quantiles for shading, 
    with the middle quantile shown as a line.
    You'd usually do something like [2.5, 25,50,75, 97.5],
    and the transparency of the fills and line is given by 
    alphashading and alphaline respectively.

    ylab is the y-axis label (usually related to the variable & units in question)
    ylims is a tuple/list giving the y-axis limits (chosen automatically if None)

    The margins are given by the mar??? arguments just as for the map plots;

    Note the xlabfmt is a way of describing how to abbreviate months
    for the x-axis labels:
       * xlabfmt="m"   for the first letter only,
       * xlabfmt="mmm" for the standard 3-letter abbreviation
       * xlabfmt="i"   for the integer month number (1=Jan etc)
    Note that these are NOT standard python format strings!

    If legend_loc is not None, then a legend will be displayed,
    using legend_loc as the loc argument to plt.legend().
      e.g. set legend_loc to a 2-tuple to show the legend with its bottom-left corner
           at that location in relative Axes coordinates.
    or set legend_loc to 0 to just place it in the "best" position within the Axes.
    http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.legend
    
    The plot is saved/displayed if outfnames is not None.
    (otherwise you can continue plotting afterwards, 
     as the function returns its Axes object for further use.)
    '''
    ##---------------------------------------------------------------
    ## FIRST THING is to convert the unit of the data cube, if required.
    # (if not, just point dcube to the input cube without a copy)
    if preferred_unit is not None:
        if ppe_cube_in is not None:
            if ppe_cube_in.units != preferred_unit:
                print "NOTE: converting PPE cube units (in a copy) from "+ppe_cube_in.units.name + \
                    " to "+preferred_unit.name + "..."
                ppe_cube = ppe_cube_in.copy()

                # Got a function to do all this now:
                common.rectify_units(ppe_cube, target_unit=preferred_unit)
            else:
                # Already in the right units
                ppe_cube = ppe_cube_in
        else:
            # Set ppe_cube to be None too:
            ppe_cube = ppe_cube_in

        # Now do the same for the obs cube:
        if obs_cube_in is not None:
            if obs_cube_in.units != preferred_unit:
                print "NOTE: converting PPE cube units (in a copy) from "+obs_cube_in.units.name + \
                    " to "+preferred_unit.name + "..."
                obs_cube = obs_cube_in.copy()

                # Got a function to do all this now:
                common.rectify_units(obs_cube, target_unit=preferred_unit)
            else:
                # Already in the right units
                obs_cube = obs_cube_in
        else:
            # Set obs_cube to be None too:
            obs_cube = obs_cube_in
    else:
        # No preferred unit, leave as it is:
        ppe_cube = ppe_cube_in
        obs_cube = obs_cube_in

    # Show the value range, and the units:
    print "Input cubes value ranges: "
    if ppe_cube is not None:
        print ppe_cube.data.min(), ppe_cube.data.max(), ppe_cube.units.title("")
    if obs_cube is not None:
        print obs_cube.data.min(), obs_cube.data.max(), obs_cube.units.title("")
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
        print "(Figure object provided, not using cmsize or fsize arguments)"
    #------------------------------------------------------------



    #------------------------------------------------------------
    # Set up the Axes object:
    if ax is None:
        newaxes = True
        ax = plt.axes()
    else:
        # Already got an Axes object:
        newaxes = False
    #------------------------------------------------------------

    #---------------------------------------------------------------
    # Set up axis details of the plot:
    # x-axis values: just Jan--Dec, 
    # but with an extra Dec on left edge, and extra Jan on right edge.
    MON_ABBRS = list(calendar.month_abbr)[1:13]
    fakemonths = range(0,14) # using these keeps them in order left-to-right
    months = [12]+range(1,13)+[1]
    ax.set_xlabel('Month')
    ax.set_xlim(0, 13)
    ax.set_xticks(months)

    if xlabfmt.lower()=="mmm":
        monlabs= [MON_ABBRS[m-1] for m in months]
        ax.set_xticklabels(monlabs)
    if xlabfmt.lower()=="m":
        monlabs= [MON_ABBRS[m-1][0] for m in months]
        ax.set_xticklabels(monlabs)
    if xlabfmt.lower()=="i":
        ax.set_xticklabels(months)

    ax.set_ylabel(ylab)
    if ylims is not None:
        ax.set_ylim(ylims)
    #---------------------------------------------------------------

    # Add PPE data:
    if ppe_cube is not None:
        quants = ppe_style["quants"]

        # Need to check for this special case
        # (e.g. if you want to plot years instead of members, against months)
        same_dims = ppe_cube.coord_dims(membercoord) == ppe_cube.coord_dims(moncoord)
        if same_dims:
            print "NOTE: 'month' and 'member' coords are on the same cube dimension."
            if quants is not None:
                raise UserWarning("Not set up to plot quantiles in this case!")

        # Can't guarantee the order of the months in the Cube
        # (they'll be monotonic, but might well start at 12 or 1),
        # and we want some repeats anyway.
        # So, get an array of indices to the month number coord,
        # which we will use to pull out the data we want
        # (the coord and data will be in the same order)
        ppe_imonths = np.array([np.where(ppe_cube.coord(moncoord).points==m)[0][0] \
                                    for m in months])
        # (the extra [0][0] above is just because I'm pulling out lots of 1-element arrays,
        #  and we just want a simple 1-d array at the end)
        #[note this only makes sense if same_dims is False; 
        # we calculate it separately for the same_dims case below]

        if quants is None:
            # Check if the plot style parameters are strings
            # - if so, make an intertools cycler out of them,
            #   just for simplicity/consistency in the ax.plot command below.
            ppe_cols = itertools.cycle(ppe_style["cols"])
            ppe_ltys = itertools.cycle(ppe_style["ltys"])
            n_ppe_cols= len(ppe_style["cols"])

            # Just plot all the lines from each "member" separately:
            if same_dims:
                # Special case, 
                # e.g. if you want to plot years instead of members, against months.
                membervals = sorted(set(ppe_cube.coord(membercoord).points))
                for m,memberval in enumerate(membervals):
                    ppe_member = ppe_cube.extract(iris.Constraint(coord_values={membercoord:memberval}))
                    # 
                    ppe_imonths = np.array([np.where(ppe_member.coord(moncoord).points==mo)[0][0] \
                                                for mo in months])
                    
                    ppe_data = ppe_member.data[ppe_imonths]
                    if not periodic:
                        ppe_data[ 0] = np.nan
                        ppe_data[-1] = np.nan

                    membernumber = ppe_member.coord(membercoord).points[0]
                    ppe_col = ppe_cols.next()
                    if (m % n_ppe_cols) == 0:
                        ppe_lty = ppe_ltys.next()


                    # Plot this line:
                    ax.plot(fakemonths,ppe_data, color=ppe_col, linestyle=ppe_lty, 
                            linewidth=ppe_style["lw"], alpha=ppe_style["alphaline"],
                            label=str(membernumber) )

            else:
                # Usual case:
                for m,ppe_member in enumerate(ppe_cube.slices_over(membercoord)):
                    ppe_data = ppe_member.data[ppe_imonths]
                    if not periodic:
                        ppe_data[ 0] = np.nan
                        ppe_data[-1] = np.nan

                    membernumber = ppe_member.coord(membercoord).points[0]
                    ppe_col = ppe_cols.next()
                    if (m % n_ppe_cols) == 0:
                        ppe_lty = ppe_ltys.next()

                    #print "PPE Data:"
                    #for i in range(len(months)):
                    #    print "{:02d} {:02d} {:s} {:02d} {:8.3f}".format(i,fakemonths[i],\
                    #                                                     monlabs[i],months[i],\
                    #                                                     float(ppe_data[i]))

                    # Plot this line:
                    ax.plot(fakemonths,ppe_data, color=ppe_col, linestyle=ppe_lty, 
                            linewidth=ppe_style["lw"], alpha=ppe_style["alphaline"],
                            label=str(membernumber) )


        else:
            # Plot two levels of shading and a central line, 
            # representing quantiles of the distribution of ensemble members:
            # (we've deliberately prevented you from using this when same_dims is True)
            if len(quants) != 5:
                raise UserWarning("Please provide 5 quantiles, or None. You provided "+str(quants))
            # We need to re-arrange the monthly data same as above.
            # Since it involves indexing the cube's data array, 
            # I'm going to have to ASSUME which dim is which:
            realiz_dim = ppe_cube.coord_dims(membercoord)[0]
            if realiz_dim != 0:
                raise UserWarning("I was expecting realization to be dim 0, but it is dim "+str(realiz_dim))
            # In particular, this will mean a failure if you're looking 
            # at the distribution over some coordinate other than realization,
            # which is not the zeroth dimension.

            # If it's all as expected, this will work:
            ppe_data = ppe_cube.data[:,ppe_imonths]
            if not periodic:
                ppe_data[ 0] = np.nan
                ppe_data[-1] = np.nan
                
            # Get the quantiles over members:
            ppe_quants = np.array(np.percentile(ppe_data,quants, axis=0)) # Shape: (5,12)

            # And plot them as shading:

            col = ppe_style["cols"][0]
            lty = ppe_style["ltys"][0]

            ax.fill_between(fakemonths, ppe_quants[0,:], y2=ppe_quants[4,:],
                            color=col, alpha=ppe_style["alphashade"])
            ax.fill_between(fakemonths, ppe_quants[1,:],y2=ppe_quants[3,:],
                            color=col, alpha=ppe_style["alphashade"])
            ax.plot(        fakemonths, ppe_quants[2,:],
                            color=col, linestyle=lty, linewidth=ppe_style["lw"], 
                            alpha=ppe_style["alphaline"] )


    # Add obs data:
    if obs_cube is not None:
        # Do the same thing with the obs data:
        obs_imonths = np.array([np.where(obs_cube.coord(moncoord).points==m)[0][0] for m in months])
        obs_data = obs_cube.data[obs_imonths]
        ax.plot(fakemonths,obs_data, 
                linestyle=obs_style["lty"],linewidth=obs_style["lw"],color=obs_style["col"])
    #---------------------------------------------------------------


    #---------------------------------------------------------------
    # Add legend if requested:
    if legend_loc is not None:
        plt.legend( loc=legend_loc, fontsize="small" )
        # Note that the fontsize string is relative to the current default
        # (an int can be given to specify it in absolute points)
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
        print "No outfnames provided, continue plotting using Axes ax..."
    #---------------------------------------------------------------

    
    print "All done in annualcycle_panel, returning..."
    return ax
#=================================================================================

























#=================================================================================
#=================================================================================
# SPECIALIST WRAPPER FUNCTIONS FOR PARTICULAR PLOTS
#=================================================================================
#=================================================================================
'''
These hard-code the particular plot parameters (sizes, colours, margins etc)
for particular plots.
 
If just exploring, I'd recommend you make your own wrapper based on these functions,
(or not use a wrapper at all).

If making a new style of plot for an important, reproducible purpose
then make a new wrapper function below, based on these.
'''


#-------------------------------------------------------------------------------------
def regenerate_data_for_UKannualcycle(source,datelimits, vartag, UKweights=None, exclusionlist=None):
   '''
   Simple processing sequence commonly used for processing data
   for standard annual cycle plots of UK-average values.
   
   source is a string that determines what data to load/process (see below) 
   
   datelimits is a 2-element list/tuple e.g. of iris PartialDateTime objects.
   
   vartag is the usual variable tag e.g. "tas" or "pr"
   
   exclusionlist is a list of ensemble members to exclude
   (see ukcpio.load_gcm_data for details)
   
   The function returns a tuple of (UKdata,UKweights);
   the UKweights can be reused in subsequent calls e.g. of different variables.
   
   Note that this is really a processing function, not a plotting function,
   so it really shouldn't be here; 
   it might be moved elsewhere in future.
   '''   
   
   if source not in ["eobs","ncic","gcm"]: #,"rcm","cpm"]:
      raise UserWarning("Data source is "+str(source)+", not eobs, ncic, gcm.") #, rcm or cpm.")
   else:
      print "Reading global "+source+" data for the specified period..." ; sys.stdout.flush()
      
      
   print "Generating UK-mean data for "+source+" "+vartag+" annual cycle plots..."
      
      

   if source=="gcm":
      alldata =  ukcpio.load_gcm_data("monthly",vartag,datelimits=datelimits,
                                      exclusionlist=exclusionlist,
                                      otherconstraint=None,verbose=False)
   elif source=="eobs":
      alldata =  ukcpio.load_obs_data("eobs", "monthly",vartag,datelimits=datelimits,
                                      otherconstraint=None,verbose=False)
   elif source=="ncic":
      # Go straight to the UK-averaged data here:
      UKdata = ukcpio.load_ncic_ukmean("monthly",vartag,datelimits=datelimits, verbose=False)      
      
   else:
      raise UserWarning("Not implemented UK-mean generation for data source "+str(source)+"!\n" +
                        "Only 'gcm' or 'eobs' or 'ncic' recognised.")

    
          
   if source != "ncic":
      # Extract the region we want:
      print "Extracting British Isles rectangular region..." ; sys.stdout.flush()
      data_here = regs.reg_extract(alldata, reg_dict=regs.REG_BI_DATA, check_mask=False)
      del(alldata)

      if UKweights is None:
         # Get the land--sea mask, for the area-averaging:
         if source=="gcm":
            print "Reading land--sea mask..." ; sys.stdout.flush()
            lsm_cube = iris.load_cube(ukcpio.LSM_N216_FILE)  # 0: sea,   1: land
            lsm_here = regs.reg_extract(lsm_cube,reg_dict=regs.REG_BI_DATA, check_mask=False)
            lsm_mask = lsm_here.data == 0   # Mask out where it is SEA
            # This makes the assumption that lsm_mask has lat and lon as dims 0 & 1...
            # (this takes a little while)
            print "Reshaping land--sea mask..." ; sys.stdout.flush()
            data_lat_lon_shape = (data_here.coord_dims('latitude')[0],
                                  data_here.coord_dims('longitude')[0] )
            # This will usually be (2,3) i.e. realiz & time will be dims 0 & 1 for the PPE
            lsm_mask_reshaped = iris.util.broadcast_to_shape(lsm_mask, 
                                                             data_here.data.shape, 
                                                             data_lat_lon_shape    )

         elif source=="eobs":
            # The sea is already masked out in this case,
            # so we'll use the cube's own mask to get the array
            # (it'll already be the right shape)
            lsm_mask_reshaped = data_here.data.mask
          
         else:
            raise UserWarning("NOT IMPLEMENTED UK-MEAN GENERATION FOR RCM or CPM!")
         


         # Read in the shapefile, and get the weights in the grid cells
         print "Reading in UK shapefile..." ; sys.stdout.flush()
         #UKreg = regs.get_uk_shapefile_region()
         UKreg = regs.get_ukcp_shapefile_regions("uk")[0]
         print "Calculating grid cell weights..." ; sys.stdout.flush()
         UKweights = regs.get_cube_shapefileregion_weights(data_here, UKreg, weightfn="area",
                                                           mask=lsm_mask_reshaped,take_cube_shape=True)
         

      # Finally, get the area-weighted average:
      print "Getting UK area-average..." ; sys.stdout.flush()
      UKdata = data_here.collapsed(['longitude','latitude'],iris.analysis.MEAN, weights=UKweights)

   else:
      print "Using NCIC UK-average data, no need to area-average here."; sys.stdout.flush()
      UKweights = None


   # Add handy coord categories for later use:
   print "Adding coord categories..." ; sys.stdout.flush()
   common.add_coord_categories(UKdata)
   
   return UKdata,UKweights
#-------------------------------------------------------------------------------------









#-------------------------------------------------------------------------------------
def uk_seasonalcycle_forcpmselectionfromgcm(vartag, gcm_monthlyLTA, obs_monthlyLTA,
                                            obs2_monthlyLTA=None,
                                            label=None, outdevs=["x11"], outfiletag=None):
    '''
    Make a plot of the mean annual cycle from the GCM PPE and the obs,
    to aid in selecting GCM members to drive the CPM.

    It is expected that this would be used with temperature and precip data,
    specified with vartag="tas" or vartag="pr" respectively.
    
    This should be called from a wrapper script 
    that does all the reading and processing of the input data.

    For these plots, we need to be able to identify each member,
    so they are styled separately (which can look a bit messy).

    gcm_monthlyLTA and obs_monthlyLTA are cubes of
    the long-term averages each month of the gcm and obs data,
    providing the annual cycle for each.

    An additional set of obs data can be provided with obs2_monthlyLTA,
    for comparison.

    '''
    YLABS = dict(tas="UK mean temperature, $^\circ$C",
                 pr ="UK mean precipitation, mm/day")

    required_units = dict(tas=cf_units.Unit("Celsius"),
                          pr =cf_units.Unit("mm/day")  )
    # Note that annualcycle_panel() itself checks and converts units,
    # so we don't need to do that here.

    
    cols = ["red","lightcoral","lime","forestgreen","blue","cornflowerblue","darkviolet","magenta"]
    ltys = ["-","--",":"]


    # Set up the output filename:
    OUTDIR = '/project/ukcp18/gcm_plots_for_cpm_selection/'
    outfile_base = OUTDIR+'gcm_uk_'+vartag+'_seasonalcycle_for_cpm_selection'
    if outfiletag is not None:
        outfile_base += outfiletag
    outfiles = [outfile_base + "." + dev for dev in outdevs]


    fig, oldfont_family,oldfont_size = plotgeneral.start_figure( (16,12.5), 94,"Arial",11,
                                                                 figbackgroundcol="white")
    ax = annualcycle_panel(ppe_cube_in=gcm_monthlyLTA, obs_cube_in=obs_monthlyLTA, 
                           fig=fig, ax=None, preferred_unit=required_units[vartag],
                           moncoord="month_number",membercoord="realization",
                           ppe_style=dict(cols=cols,  lw=1.5,ltys=ltys, alphaline=1.0,
                                          quants=None,alphashade=1),
                           obs_style=dict(col="black",lw=2,lty="-"),  
                           ylab=YLABS[vartag], ylims=None,xlabfmt="m",
                           #marlft=0.09, marrgt=0.78, martop=0.97, marbot=0.10, 
                           #marwsp=0.2, marhsp=0.2,
                           legend_loc=(1.05,-0.1),  outfnames=None )
    
    if obs2_monthlyLTA is not None:
         ax = annualcycle_panel(ppe_cube_in=None, obs_cube_in=obs2_monthlyLTA, 
                                fig=fig, ax=ax, preferred_unit=required_units[vartag],
                                moncoord="month_number",membercoord="realization",
                                ppe_style=dict(cols=cols,  lw=1.5,ltys=ltys, alphaline=1.0,
                                               quants=None,alphashade=1),
                                obs_style=dict(col="black",lw=2,lty="--"),  
                                ylab=YLABS[vartag], ylims=None,xlabfmt="m",
                                legend_loc=(1.05,-0.1),  outfnames=None )
         
    ax.text(0.05,0.90, label, size=10, color='black', transform=ax.transAxes)

    fig.subplots_adjust(left  = 0.09,  bottom = 0.10,
                        right = 0.78,  top    = 0.97,
                        wspace= 0.20,  hspace = 0.20 )
    plotgeneral.end_figure(outfiles, 
                           oldfont_family=oldfont_family,
                           oldfont_size=oldfont_size)

    return
#-------------------------------------------------------------------------------------






#-------------------------------------------------------------------------------------
def uk_seasonalcycle_tas_pr_forevaluation(gcm_tas_monLTA =None,cpm_tas_monLTA =None,obs_tas_monLTA =None,
                                          gcm_tas_monLTSD=None,cpm_tas_monLTSD=None,obs_tas_monLTSD=None,
                                          gcm_pr_monLTA  =None,cpm_pr_monLTA  =None,obs_pr_monLTA  =None,
                                          gcm_pr_monLTSD =None,cpm_pr_monLTSD =None,obs_pr_monLTSD =None,
                                          style="shade",outdevs=["x11"], outfiletag=None):
    '''
    Make a 4-panel plot of the mean annual cycle (seasonality)
    of GCM PPE members, CPM PPE members and obs
    for UK-mean temperature and precip,
    demonstrating both the bias in the mean and in the interannual variability.
    
    style is a string in ["shade","lines","idlines"]:
    "shade": shade quantiles of the PPE distributions
    "lines": plot solid lines of the PPE members
    "idlines": colour/style-code the PPE members and add a legend, so they can be identified.
    
    It is expected that you'd only provide EITHER the GCM OR CPM if using "idlines",
    but it should be possible to provide both sensibly for the other options.
    
    Note that all 12 input cubes are optional,
    and contain long-term averages or standard deviations for each month.
    '''
    # Set up constants defining the three different styles:
    CMSIZES = dict(shade=(20,20), lines=(20,20), idlines=(23,20))
    LEGEND_LOCS  = dict(shade=None,    lines=None,    idlines=(1.05,-0.8) )
    GCM_TAS_COLS = dict(shade=["red"], lines=["red"], 
                        idlines=["red", "lightcoral",     "lime",      "forestgreen",
                                 "blue","cornflowerblue", "darkviolet","magenta"      ] )
    CPM_TAS_COLS = dict(shade=["blue"], lines=["blue"],  idlines=GCM_TAS_COLS["idlines"] )
    GCM_PR_COLS  = dict(shade=["red" ], lines=["red" ],  idlines=GCM_TAS_COLS["idlines"] )
    CPM_PR_COLS  = dict(shade=["blue"], lines=["blue"],  idlines=GCM_TAS_COLS["idlines"] )
    LTYS = dict(shade=["-"], lines=["-"], idlines=["-","--",":"])
    QUANTS  = dict(shade=[2.5, 25, 50, 75, 97.5], lines=None,idlines=None)
    LALPHAS = dict(shade=0.2, lines=0.2, idlines=1.0 )
    
    # Picking the plot size in cm also validates the style argument:
    cmsize = CMSIZES[style]


    # Set up the output filename:
    OUTDIR = '/project/ukcp18/model_evaluation/'
    outfile_base = OUTDIR+"SciRept_eval_seasonalcycle_tas_pr"
    if outfiletag is not None:
        outfile_base += outfiletag
    outfiles = [outfile_base + "." + dev for dev in outdevs]



    # Set up the choice of style:
    dpi = 94
    fontfam = "Arial"
    fsize = 12

    gcm_tas_style=dict(cols=GCM_TAS_COLS[style], lw=1, ltys=LTYS[style], alphaline=LALPHAS[style], quants=QUANTS[style], alphashade=0.2)
    cpm_tas_style=dict(cols=CPM_TAS_COLS[style], lw=1, ltys=LTYS[style], alphaline=LALPHAS[style], quants=QUANTS[style], alphashade=0.2)

    gcm_pr_style =dict(cols=GCM_PR_COLS[ style], lw=1, ltys=LTYS[style], alphaline=LALPHAS[style], quants=QUANTS[style], alphashade=0.2)
    cpm_pr_style =dict(cols=CPM_PR_COLS[ style], lw=1, ltys=LTYS[style], alphaline=LALPHAS[style], quants=QUANTS[style], alphashade=0.2)

    obs_style    =dict(col="black",lw=1,lty="-")


    legend_loc = LEGEND_LOCS[style] #(1.05, -0.8)  if style=="idlines" else None


    #---------------------------------------
    # Do the plotting:
    fig, oldfont_family,oldfont_size = plotgeneral.start_figure(cmsize,dpi,fontfam,fsize,
                                                                figbackgroundcol="white")

    # Top-left:
    ax = fig.add_subplot(2,2,1)
    ax = annualcycle_panel(ppe_cube_in=gcm_tas_monLTA, obs_cube_in=obs_tas_monLTA, fig=fig, ax=ax,
                           preferred_unit=cf_units.Unit("Celsius"),
                           moncoord="month_number",membercoord="realization",
                           ppe_style=gcm_tas_style,
                           obs_style=obs_style,  
                           ylab="UK mean temperature, $^\circ$C", ylims=None,
                           marlft=None, marrgt=None, martop=None, marbot=None, 
                           marwsp=None, marhsp=None,xlabfmt="m",
                           outfnames=None )
    ax = annualcycle_panel(ppe_cube_in=cpm_tas_monLTA, obs_cube_in=None, fig=fig, ax=ax,
                           preferred_unit=cf_units.Unit("Celsius"),
                           moncoord="month_number",membercoord="realization",
                           ppe_style=cpm_tas_style,
                           obs_style=obs_style,  
                           ylab="UK mean temperature, $^\circ$C", ylims=None,
                           marlft=None, marrgt=None, martop=None, marbot=None, 
                           marwsp=None, marhsp=None,xlabfmt="m",
                           outfnames=None )
    

    # Top-right (note we add the legend from the GCM plot here)
    ax = fig.add_subplot(2,2,2)
    ax = annualcycle_panel(ppe_cube_in=gcm_tas_monLTSD, obs_cube_in=obs_tas_monLTSD, fig=fig, ax=ax,
                           preferred_unit=cf_units.Unit("Celsius"),
                           moncoord="month_number",membercoord="realization",
                           ppe_style=gcm_tas_style,
                           obs_style=obs_style,  
                           ylab='Interannual variability ($\sigma$)\nof UK mean temperature,$^\circ$C',
                           ylims=None,
                           marlft=None, marrgt=None, martop=None, marbot=None, 
                           marwsp=None, marhsp=None,xlabfmt="m",
                           outfnames=None, legend_loc=legend_loc )
    ax = annualcycle_panel(ppe_cube_in=cpm_tas_monLTSD, obs_cube_in=None, fig=fig, ax=ax,
                           preferred_unit=cf_units.Unit("Celsius"),
                           moncoord="month_number",membercoord="realization",
                           ppe_style=cpm_tas_style,
                           obs_style=obs_style,  
                           ylab='Interannual variability ($\sigma$)\nof UK mean temperature,$^\circ$C',
                           ylims=None,
                           marlft=None, marrgt=None, martop=None, marbot=None, 
                           marwsp=None, marhsp=None,xlabfmt="m",
                           outfnames=None )

    # Bottom-left:
    ax = fig.add_subplot(2,2,3)
    ax = annualcycle_panel(ppe_cube_in=gcm_pr_monLTA, obs_cube_in=obs_pr_monLTA, fig=fig, ax=ax,
                           preferred_unit=cf_units.Unit("mm/day"),
                           moncoord="month_number",membercoord="realization",
                           ppe_style=gcm_pr_style,
                           obs_style=obs_style,  
                           ylab="UK mean precipitation, mm/day", ylims=None,
                           marlft=None, marrgt=None, martop=None, marbot=None, 
                           marwsp=None, marhsp=None,xlabfmt="m",
                           outfnames=None )
    ax = annualcycle_panel(ppe_cube_in=cpm_pr_monLTA, obs_cube_in=None, fig=fig, ax=ax,
                           preferred_unit=cf_units.Unit("mm/day"),
                           moncoord="month_number",membercoord="realization",
                           ppe_style=cpm_pr_style,
                           obs_style=obs_style,  
                           ylab="UK mean precipitation, mm/day", ylims=None,
                           marlft=None, marrgt=None, martop=None, marbot=None, 
                           marwsp=None, marhsp=None,xlabfmt="m",
                           outfnames=None )


    # Bottom-right:
    ax = fig.add_subplot(2,2,4)
    ax = annualcycle_panel(ppe_cube_in=gcm_pr_monLTSD, obs_cube_in=obs_pr_monLTSD, fig=fig, ax=ax,
                           preferred_unit=cf_units.Unit("mm/day"),
                           moncoord="month_number",membercoord="realization",
                           ppe_style=gcm_pr_style,
                           obs_style=obs_style,  
                           ylab='Interannual variability ($\sigma$)\nof UK mean precip, mm/day',
                           ylims=None,
                           marlft=None, marrgt=None, martop=None, marbot=None, 
                           marwsp=None, marhsp=None,xlabfmt="m",
                           outfnames=None )
    ax = annualcycle_panel(ppe_cube_in=cpm_pr_monLTSD, obs_cube_in=None, fig=fig, ax=ax,
                           preferred_unit=cf_units.Unit("mm/day"),
                           moncoord="month_number",membercoord="realization",
                           ppe_style=cpm_pr_style,
                           obs_style=obs_style,  
                           ylab='Interannual variability ($\sigma$)\nof UK mean precip, mm/day',
                           ylims=None,
                           marlft=None, marrgt=None, martop=None, marbot=None, 
                           marwsp=None, marhsp=None,xlabfmt="m",
                           outfnames=None )

    if style=="idlines":
        fig.subplots_adjust(left  = 0.07,  bottom = 0.08,
                            right = 0.86,  top    = 0.97,
                            wspace= 0.27,  hspace = 0.22 )
    else:
        plt.tight_layout()

    plotgeneral.end_figure(outfiles,
                           oldfont_family=oldfont_family,
                           oldfont_size=oldfont_size) 
    # All done!

    return

#-------------------------------------------------------------------------------------



#=================================================================================

