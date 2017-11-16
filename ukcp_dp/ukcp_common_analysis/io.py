# -*- coding: utf-8 -*-
'''
This contains handy reading (and maybe writing) routines
for use with the GCM and CPM data for UKCP18,
and E-OBS and NCIC gridded obs data, which we're using with UKCP18.

You would usually import this module as:

import ukcp_common_analysis.io  as ukcpio

--------------------------------------------------------
Contents:

* Directories for GCM data
* Lists of PPE members to exclude from the GCM
* Directories for E-OBS and NCIC data
* Paths to ancilary files, such as land-sea masks


* gcm_filenames() gets a list of GCM PPE filenames ready for loading
                  (with a test_gcm_filenames() function)

* load_gcm_data() general GCM PPE data loading function
                  (with a test_load_gcm_data() function)



* get_eobs_filenames() gets a list of filenames of the E-OBS data
                       that has been monthly-averaged and regridded to N216.

* get_ncic5km_filenames() gets a list of filenames of the monthly 
                          or daily 5km NCIC data.


* load_eobs_data()  and  load_ncic5km_data()  are wrappers to...

* load_obs_data() is a general function for reading the E-OBS and NCIC obs data
                  (with test_load_eobs_data() and test_load_ncic5km_data() functions)


* load_ncic_ukmean() dedicated function for reading in the NCIC UK-mean data 
                    (with a test_load_ncic_ukmean() function)


--------------------------------------------------------
'''
import os
import glob
import iris
import cf_units 
import common_analysis as common
import datetime as dt
import numpy as np
import itertools

from settings import INPUT_DIR

#=========================================================================

# Main data locations here.
# (THESE WILL LATER NEED SEPARATING INTO A SEPARATE FILE
#  BEFORE THIS CODE GOES ONTO GITHUB)

#GCM_SUITES = ("u-an398", "u-ap977", "u-ar095")
GCM_SUITES = (dict(name="u-an398", startdate=iris.time.PartialDateTime(1899,12,1)),
              dict(name="u-ap977", startdate=iris.time.PartialDateTime(1970,12,1)),
              dict(name="u-ar095", startdate=iris.time.PartialDateTime(2005,12,1)),
              dict(name="DUMMY",   startdate=iris.time.PartialDateTime(3000,12,1)) )
# Defining this as a tuple keeps it ordered.
# Note the additional dummy suite, so we can always check the start date of the "next" suite.
NSUITES = len(GCM_SUITES) - 1



# This was the initial GCM run, 
# which was cancelled after finding too many errors in its configuration:
#OLD_GCM_SUITES = ("u-ak048")
OLD_GCM_SUITES = (dict(name="u-ak048",startdate=iris.time.PartialDateTime(1899,12,1))  )


GCM_COUPLED_MAIN= '/project/spice/qump_hadgem3/GA7/COUPLED/' #u-an398/'
GCM_COUPLED_MAIN= INPUT_DIR + "/"
GCM_COUPLED_ALT =             '/project/ukcp18/GA7/COUPLED/' #u-an398/'

GCM_COUPLED_MONTHLY_TAG = "netcdf/monthly/"
GCM_COUPLED_DAILY_TAG   = "netcdf/daily/"

ALT_VBLS = ["heaviside","ua","uas","va","vas"]
# The "alt" location has the daily heaviside function and wind components.
# The "main" location has precip, PMSL, tasmax,tasmin.


# These members have failed, but are still present 
# - we need to exclude them when reading.
GCM_EXCLUDED_MEMBERS = [1100103]   # Failed early on, too unstable

# These were excluded by David Sexton for the old runs - see email 18/05/2017
# It remains to be seen if we want to hard-code their exclusion 
# for the new runs.
#GCM_EXCLUDED_MEMBERS += [1102829, 1102549, 1100939] # weak AMOC, ran slowly
#GCM_EXCLUDED_MEMBERS += [1102884]                   # strong SST warm bias




# Obs data locations:
EOBS_N216_MONMEANS_DIR = '/project/ukcp18/E-OBS_on_N216grid_monthlymeans/'

NCIC_BASE_DIR    = '/project/ncic_data/UKCP09/data/'
NCIC_MONTHLY_DIR = NCIC_BASE_DIR+'gridded-land-obs-monthly/grid/netcdf/'
NCIC_DAILY_DIR   = NCIC_BASE_DIR+'gridded-land-obs-daily/grid/netcdf/'


NCIC_UKMEAN_DIR  = '/project/ukcp18/NCIC_processed_data/'

#===================================================================================



#=========================================================================
# Ancilary files:
LSM_N216_FILE = '/project/spice/qump_hadgem3/GA7/COUPLED/masks/qrparm.mask'
# This data doesn't have a mask as such,
# but is just a data array where 0 ==> SEA  and  1 ==> LAND

LANDFRAC_N216_FILE = '/project/spice/qump_hadgem3/GA7/COUPLED/masks/qrparm.landfrac'
#=========================================================================
















#==============================================================================
def gcm_filenames(timeres,vartag, suite_index=None, memberslist=None, 
                  exclusionlist=None,  verbose=False):
    '''
    Gets the list of GCM filenames ready for loading.
    
    timeres is "monthly" or "daily"
    vartag is the label used for the variable in the filename,
    e.g. "tas" for near-surface air temperature.

    suite_index is an integer used to index the GCM_SUITES tuple,
    and can be used for separating filenames from the three suites: 
      0 ==> u-an398 (1899-1971)
      1 ==> u-ap977 (1970-2006)
      2 ==> u-ap977 (2005-____)
    Leaving as None returns filenames from both suites together.

    For efficienct selecting of particular members, 
    memberslist can be provided as a list of ints 
    which describe complete R__I__P____ codes,
    such as you'd get from common.ripstr_to_int() [hint, hint]
    (similar to GCM_EXCLUDED_MEMBERS).
    
    For convenience, you can also provide a list of members to EXCLUDE
    (in addition to GCM_EXCLUDED_MEMBERS).
    The exclusion occurs after the selection, 
    so takes priority over the memberslist selection.
    
    (More complex member selection should be done with a Constraint
     when loading the data)

    '''
    timeres_options = ["monthly","daily"]
    if timeres not in timeres_options:
        raise UserWarning("timeres '"+str(timeres)+"' not one of 'monthly' or 'daily'.")

    
    if timeres=="daily":
        if vartag in ALT_VBLS:
            thepath = GCM_COUPLED_ALT
        else:
            thepath = GCM_COUPLED_MAIN
        
        if suite_index is None:
            # Include both suites:
            thepaths = [thepath + suite["name"] +"/" + GCM_COUPLED_DAILY_TAG for suite in GCM_SUITES]
        else:
            # Include just the selected suite, but as a list for convenience:
            thepaths = [thepath + GCM_SUITES[suite_index]["name"] +"/" ]

        # List of lists (one element per suite)
        lists_for_suites = [glob.glob(apath+"r*/"+vartag+"/r*_*_"+vartag+".nc") for apath in thepaths]

    else:
        thepath = GCM_COUPLED_MAIN
        if suite_index is None:
            # Include both suites:
            thepaths = [thepath + suite["name"] +"/" + GCM_COUPLED_MONTHLY_TAG for suite in GCM_SUITES]
        else:
            # Include just the selected suite, but as a list for convenience:
            thepaths = [thepath + GCM_SUITES[suite_index]["name"] +"/"+ GCM_COUPLED_MONTHLY_TAG ]

        lists_for_suites = [glob.glob(apath+"r*/*_"+vartag+".nc") for apath in thepaths]


    # Merge lists down to a single list over all suites, and sort:
    input_fnames = sorted(list(itertools.chain.from_iterable(lists_for_suites)))



    # If explicitly selecting members,
    if memberslist is not None:
        # Make a list of strings in the format "r_i_p_____", 
        # as used in the filenames/directories:
        selection_rips = [common.ripint_to_str(selmember) for selmember in memberslist]
        if verbose:
            print "Sub-selecting only members " + ", ".join(selection_rips)
        # Include only the selected realizations:
        # (this is a bit complicated because of the nesting)
        input_fnames = [fname for fname in input_fnames \
                            if any([selmember in fname for selmember in selection_rips]) ]


    if verbose:
        print "Input filenames (" ,len(input_fnames),"):"
        print "\n".join(input_fnames)
    


    # Finally, exclude bad members:
    if exclusionlist is None:   exclusionlist = [] # (We can add empty lists, but not Nones)

    # Again, make a list of strings in the format "r_i_p_____", 
    # as used in the filenames/directories:
    exclusion_rips = [common.ripint_to_str(badmember) for badmember in GCM_EXCLUDED_MEMBERS+exclusionlist]
  
    # Exclude the bad realizations:
    # (this is a bit complicated because of the nesting)
    clean_fnames = [fname  for fname in input_fnames \
                        if not any([badmember in fname  for badmember in exclusion_rips]) ]
    if verbose:
        print "Cleaned filenames (" ,len(clean_fnames),"):"
        for fname in clean_fnames: 
            print fname

    return clean_fnames


#-----------------------------------------------------------------------------


def test_gcm_filenames():
    '''
    This isn't a very thorough test function, but it will do for now.
    '''
    print "Testing gcm_filenames() function:"
    print "············································"

    print "Air temperature monthly filenames:"
    fnames = gcm_filenames("monthly","tas")
    print "\n".join(fnames)
    assert len(fnames) > 0
    print "············································"

    selmember = 1101935
    print "Air temperature monthly filenames for member ",selmember,":"
    fnames = gcm_filenames("monthly","tas",memberslist=[selmember])
    print "\n".join(fnames)
    assert len(fnames) > 0
    print "············································"

    selmembers = [1100000, 1102305, 1102914]
    print "Air temperature monthly filenames for members ",selmembers,":"
    fnames = gcm_filenames("monthly","tas",memberslist=selmembers)
    print "\n".join(fnames)
    assert len(fnames) > 0
    print "············································"

    fnames = gcm_filenames("daily","tasmax")
    print "Air temperature maximum daily filenames:"
    print "\n".join(fnames)
    assert len(fnames) > 0
    print "············································"

    selmember = 1101935
    print "Air temperature maximum  daily filenames for member ",selmember,":"
    fnames = gcm_filenames("daily","tasmax",memberslist=[selmember])
    print "\n".join(fnames)
    assert len(fnames) > 0
    print "············································"

    try:
        fnames = gcm_filenames("rubbish","tas")
    except UserWarning:
        print "Correctly rejected rubbish for the timeres argument."
    print "············································"

    fnames = gcm_filenames("monthly","rubbish")
    print "Rubbish monthly filenames:"
    print "\n".join(fnames)
    assert len(fnames) == 0
    print "(Correctly got no filenames)"
    print "············································"
    
    print "Note: We're not testing for the presence or completeness of variables here."
    return



#--------------------------------------------------------------------------------------------
def dtype_callback(cube, field, filename):
    '''
    Ensure cubes read in are converted
    to use maked arrays of 32-bit floats.
    '''
    cube.data = np.ma.asarray(cube.data, dtype=np.float32)
#--------------------------------------------------------------------------------------------






def load_gcm_data(timeres,vartag, datelimits=None, 
                  otherconstraint=None, 
                  memberslist=None,exclusionlist=None,
                  returnCL=False, verbose=False):
    ''' 
    Read in GCM data.

    timeres is "monthly" or "daily"

    vartag is the label used for the variable in the filename,
    e.g. "tas" for near-surface air temperature.


    datelimits is a 2-element list/tuple of iris.time.PartialDateTime objects.
    e.g.       dtlims = [iris.time.PartialDateTime(year=1901,month=6,day=1), 
                         iris.time.PartialDateTime(year=1911,month=9,day=1) ]
    OR            a 2-element list/tuple of ints, e.g. [1961,1991],
                  which are then interpreted as years
                  and made into iris.time.PartialDateTime objects.
    These are used to create a Constraint on the time coord,
    from the lower limit INCLUSIVELY, to the upper limit EXCLUSIVELY
    (matching the usual python behaviour)
    
    This is necessary because the runs are currently still in progress,
    so the files have different numbers of timesteps 
    - and so can't be concatenated into a single Cube.
    This functionality will likely be changed in future,
    perhaps allowing some standard default climatological periods 
    to be specified simply.

    As an alternative, datelimits="all" can be specified.
    This means that there is no constraint on the dates.
    Again, this will fail if the data don't have the same number of timesteps.
    
    So, we have an additional option, returnCL,
    to allow returning a CubeList instead of a Cube.
    (the Cubes are still concatenated as far as they can go,
     and thus might not all have the same dimensions in the CubeList.)

    It is expected that a user would either pick a known set of dates,
    or not specify the dates and return a CubeList,
    which they would manipulate manually afterwards.

    (Basically, I couldn't think of a sufficiently general algorithm 
     that would allow the user to just pick all realizations that covered 
     the whole requested date range,
     because neither netcdftime objects nor iris.time.PartialDateTime objects
     have timedelta or "-" override functions, so I can't check 
     that any cube has actually covered the whole period as much as possible.)
    
    
    otherconstraint is another iris.Constraint (or list of them)
    that will be included with the date Constraint when loading.

    In practice, especially for the daily data, it is likely that 
    users would just process single members at a time.


    Because data is separated by realization in the files,
    there is a shortcut option (memberslist) to select members from a list,
    and another (exclusionlist) to exclude members, 
    without having to use an iris.Constraint.
    
    This is passed directly to the gcm_filenames function and not parsed here,
    so the format is the same as there:
    memberslist and exclusionlist should be provided as a list of ints 
    which describe complete R__I__P____ codes,
    such as you'd get from common.ripstr_to_int() [hint, hint]
    (similar to GCM_EXCLUDED_MEMBERS).
    Note that because this shortens the list of filenames to read,
    it is much more efficient that supplying a Constraint on realization!

    (exclusionlist is applied AFTER memberslist, so takes priority)

    WARNING: I couldn't get some daily cubes to concatenate 
    as they changed data type from float64 to float32 at 1910.
    '''
    
    if datelimits is None:
        print "WARNING: No date limits specified!"
        print "         Reading will fail."
        print "         To be super-helpful, I'll read in the available data as a CubeList,"
        print "         and tell you the realization number and date ranges in each Cube."
        filenames = gcm_filenames(timeres,vartag, memberslist=memberslist, 
                                  exclusionlist=exclusionlist, verbose=verbose)
        # This way meant we had to load them all in at once,
        # and they didn't come out sorted:
        #alldata = iris.load_raw(filenames)
        #for acube in alldata:
        #    tcoordlims = [acube.coord('time')[0], acube.coord('time')[-1] ]
        #    dtlims = [cf_units.num2date( tcoord.points,
        #                                 tcoord.units.name,
        #                                 tcoord.units.calendar)[0]  for tcoord in tcoordlims]
        #    realization = acube.coord('realization').points[0]
        #    print acube.__repr__(), realization, dtlims
        # 
        # This way, we sort (group) the filenames by realization,
        # and load each cube separately, reporting as we go.
        #
        # Get the realizations:
        realizations = [ common.ripstr_to_int(fname.split("/")[-2]) for fname in filenames]
        # Make a list of (realization,fname) pairs:
        realiz_fnames = zip(realizations,filenames)
        realiz_fnames.sort()
        # Now just pull out the filenames from the sorted paired list:
        fnames_sorted = [f for r,f in realiz_fnames]
        
        for fname in fnames_sorted:
            acube = iris.load_cube(fname)
            tcoordlims = [acube.coord('time')[0], acube.coord('time')[-1] ]
            dtlims = [cf_units.num2date( tcoord.points,
                                         tcoord.units.name,
                                         tcoord.units.calendar)[0]  for tcoord in tcoordlims]
            realization = acube.coord('realization').points[0]
            print acube.__repr__(), realization, dtlims
        raise UserWarning("Refusing to let you try to load GCM data without a date constraint")



    if type(datelimits) is str:
        if datelimits.lower()=="all":
            dateconstraint = None
            if verbose:
                print "All dates requested; not constrainting on time."
        else:
            raise UserWarning("datelimits should be 'all' or a 2-element iterable, in load_gcm_data()")
    else:
        if len(datelimits) != 2:
            raise UserWarning("datelimits should be 'all' or a 2-element iterable, in load_gcm_data()")

        if not all([type(dtlim) is iris.time.PartialDateTime for dtlim in datelimits]):
            if all([type(dtlim) is int                       for dtlim in datelimits]):
                if verbose:
                    print "datelimits provided as integers, interpreting as years..."

                dateconstraint = iris.Constraint(time = lambda t:
                                         datelimits[0] <= t.point.year <= datelimits[1])
#                datelimits = [iris.time.PartialDateTime(year=dtlim,month=1,day=1) \
#                                  for dtlim in datelimits]
            else:
                raise UserWarning("Not all date limits were iris.time.PartialDateTime objects or ints!")
        

        else:
            # Sorted out date limits, now make Constraint:
            dateconstraint = iris.Constraint(time = lambda t: 
                                         datelimits[0] <= t.point <= datelimits[1])


    # Sorted out constraints, now putting them together...
    # (note that both dateconstraint and otherconstraint could be None)
    if otherconstraint is not None:
        theconstraint = dateconstraint & otherconstraint
    else:
        theconstraint = dateconstraint
    

    # Get the filenames from the two suites separately:
    filenames_of_suites = [gcm_filenames(timeres,vartag, suite_index=i, memberslist=memberslist, 
                               exclusionlist=exclusionlist, verbose=verbose) for i in range(NSUITES) ]
    #filenames0 = gcm_filenames(timeres,vartag, suite_index=0, memberslist=memberslist, 
    #                           exclusionlist=exclusionlist, verbose=verbose)
    #filenames1 = gcm_filenames(timeres,vartag, suite_index=1, memberslist=memberslist, 
    #                           exclusionlist=exclusionlist, verbose=verbose)
    
    # Files from the first suite (1899-12 to 1971-02) need trimming
    # so they only go to 1970-11
    # (so we take 1970-12 onwards from the second suite only)

    # Each suite goes on for a few months after the next suite starts,
    # so they need these last extra dates trimming off.
    # Make a list of Constraints for taking the date to be before the next suite's start date:
    suitedates_constraints = [iris.Constraint(time = lambda cell: cell < GCM_SUITES[i+1]["startdate"]) for i in range(NSUITES)]
    #suitedates_constraint = iris.Constraint(time = lambda cell: cell < iris.time.PartialDateTime(1970,12,1))
    #suitedates_constraint = iris.Constraint(time = lambda cell: cell < iris.time.PartialDateTime(2005,12,1))


    # Finally: load the data.
    if returnCL:
        if verbose:
            print "Loading data to be returned as a CubeList..."
        # Load the data such that a CubeList is returned:
        thedata = iris.cube.CubeList()
        with iris.FUTURE.context(cell_datetime_objects=True):    
            for i in range(NSUITES):
                thedata.extend( iris.load(filenames_of_suites[i], 
                                          theconstraint & suitedates_constraints[i], 
                                          callback=dtype_callback) )
            #thedata =       iris.load(filenames0, theconstraint & suitedates_constraint, callback=dtype_callback)
            #thedata.extend( iris.load(filenames1, theconstraint,                         callback=dtype_callback) )
        if verbose:
            print "Read data into CubeList with the following limits:"
            for i,acube in enumerate(thedata):
                tcoordlims = [acube.coord('time')[0], acube.coord('time')[-1] ]
                dtlims = [cf_units.num2date( tcoord.points,
                                             tcoord.units.name,
                                             tcoord.units.calendar)[0]  for tcoord in tcoordlims]
                realizations = acube.coord('realization').points
                print i,":",acube.__repr__(), " Dates:",dtlims," Realizations:",realizations

            
    else:
        if verbose: print "Attempting to loading data into a single Cube..."
        # The usual case: try to load the data in as a single Cube:
        # (although it's a bit more complicated than that,
        #  as we have to get the data from the two suites separately)
        thedata_insuites = iris.cube.CubeList()
        if verbose:
            print "Read data into cubes for each suite:"
        with iris.FUTURE.context(cell_datetime_objects=True):    
            for i in range(NSUITES):
                if verbose:
                    print "Suite ",i,": ("+GCM_SUITES[i]["name"]+"):"
                #import code ; code.interact(local=locals())
                try:
                    thedata_insuites.append( iris.load_cube(filenames_of_suites[i], 
                                                            theconstraint & suitedates_constraints[i],
                                                            callback=dtype_callback) )
                    if verbose:
                        print "   ",thedata_insuites[i].__repr__()
                     #
                except iris.exceptions.ConstraintMismatchError as cause:
                    if verbose:
                        print "     (No data)"
                    print "     Didn't get any data from suite ",i,  \
                        ", with iris.exceptions.ConstraintMismatchError:" ,cause
            #
            # First suite:
            #try:
            #    thedata0 = iris.load_cube(filenames0, theconstraint & suitedates_constraint, callback=dtype_callback)
            #except iris.exceptions.ConstraintMismatchError as cause:
            #    print "Didn't get any data from suite 0, with iris.exceptions.ConstraintMismatchError:" ,cause
            #    thedata0 = None
            ## Second suite:
            #try:
            #    thedata1 = iris.load_cube(filenames1, theconstraint,                         callback=dtype_callback)
            #except iris.exceptions.ConstraintMismatchError as cause:
            #    print "Didn't get any data from suite 1, with iris.exceptions.ConstraintMismatchError:" ,cause
            #    thedata1 = None
        # Combine what we've got:
        #if thedata0 is None:
        #    thedata = thedata1
        #elif thedata1 is None:
        #    thedata = thedata0
        #else:
        #    thedata = iris.cube.CubeList([thedata0,thedata1]).concatenate_cube()
        thedata = thedata_insuites.concatenate_cube()
   
        if verbose:
            #print "Read data into cubes for each suite:"
            #print "First suite ("+GCM_SUITES[0]["name"]+"):"
            #print "   ",thedata0.__repr__()
            #print "Second suite ("+GCM_SUITES[1]["name"]+"):"
            #print "   ",thedata1.__repr__()
            #print "Third suite ("+GCM_SUITES[2]["name"]+"):"
            #print "   ",thedata1.__repr__()
            print "Resulting single Cube:"
            print "   ",thedata.__repr__()
            tcoordlims = [thedata.coord('time')[0], thedata.coord('time')[-1] ]
            dtlims = [cf_units.num2date( tcoord.points,
                                         tcoord.units.name,
                                         tcoord.units.calendar)[0]  for tcoord in tcoordlims]
            realizations = thedata.coord('realization').points
            print "Date range:  ", dtlims
            print "Realizations:", realizations
    
    
    return thedata


#-------------------------------------------------------------------


def test_load_gcm_data():
    '''
    This isn't a very thorough test function, but it will do for now.
    '''
    print "Testing load_gcm_data() function:"
    vartag  = "tas"
    timeres = "monthly"
    verbose = True
    dtlims_ok = [ iris.time.PartialDateTime(year=1900,month=1,day=1),
                  iris.time.PartialDateTime(year=1910,month=1,day=1) ]
    dtlims_bad = [iris.time.PartialDateTime(year=1900,month=1,day=1),
                  iris.time.PartialDateTime(year=1990,month=1,day=1) ]
    dtlims_transition = [iris.time.PartialDateTime(1969,6,1), 
                         iris.time.PartialDateTime(1980,6,1) ]
    dtlims_suite1 = [iris.time.PartialDateTime(1980,1,1), 
                     iris.time.PartialDateTime(1983,1,1) ]
    members_suite1= [1100000,1102753,1102914,1101649]
    members_exclude= [1100000,1102753,1102914,1101649]
    print "············································"

    print "Reading in without any constraint:"
    try:
        acube = load_gcm_data(timeres,vartag, datelimits=None,  returnCL=False, verbose=verbose)
    except UserWarning:
        print "Correctly refused to work."
    print "············································"

    print "Trying to read in data with sensible date limits:"
    acube = load_gcm_data(timeres,vartag, datelimits=dtlims_ok,  returnCL=False, verbose=verbose)
    print "That worked fine."
    print "············································"

    print "Trying to read in data with bad date limits:"
    try:
        acube = load_gcm_data(timeres,vartag, datelimits=dtlims_bad,  returnCL=False, verbose=verbose)
    except iris.exceptions.ConstraintMismatchError:
        print "Correctly failed."
    print "············································"

    print "Trying to read in all dates into a single Cube:"
    try:
        acube = load_gcm_data(timeres,vartag, datelimits="all",  returnCL=False, verbose=verbose)
    except iris.exceptions.ConstraintMismatchError:
        print "Correctly failed."
    print "············································"

    selmember = 1101843
    print "Trying to read in all dates from member",selmember," into a single Cube:"
    acube = load_gcm_data(timeres,vartag, datelimits="all", memberslist=[selmember], returnCL=False, verbose=verbose)
    print "That worked fine."
    print "············································"

    print "Trying to read all dates into a CubeList:"
    acubelist = load_gcm_data(timeres,vartag, datelimits="all",  returnCL=True, verbose=verbose)
    print "That worked fine."
    print "············································"

    print "Trying to read in data with sensible date limits into a CubeList:"
    acubelist = load_gcm_data(timeres,vartag, datelimits=dtlims_ok,  returnCL=True, verbose=verbose)
    assert len(acubelist)==1
    print "That worked fine."
    print "············································"
    


    print "Trying to read in data across first suite only:"
    dtlims = [ iris.time.PartialDateTime(year=1899,month=12,day=1),
               iris.time.PartialDateTime(year=1913,month=12,day=1) ]
    acube = load_gcm_data(timeres,vartag, datelimits=dtlims_transition, memberslist=[1100000],  returnCL=False, verbose=verbose)
    print "That worked fine."
    print "············································"

    print "Trying to read in data across second uite only:"
    dtlims = [ iris.time.PartialDateTime(year=1975,month=12,day=1),
               iris.time.PartialDateTime(year=1990,month=12,day=1) ]
    acube = load_gcm_data(timeres,vartag, datelimits=dtlims_transition, memberslist=[1100000],  returnCL=False, verbose=verbose)
    print "That worked fine."
    print "············································"

    print "Trying to read in data across third suite only:"
    dtlims = [ iris.time.PartialDateTime(year=2006,month=12,day=1),
               iris.time.PartialDateTime(year=2013,month=12,day=1) ]
    acube = load_gcm_data(timeres,vartag, datelimits=dtlims_transition, memberslist=[1100000],  returnCL=False, verbose=verbose)
    print "That worked fine."
    print "············································"

    print "Trying to read in data across all 3 suites:"
    dtlims = [ iris.time.PartialDateTime(year=1899,month=12,day=1),
               iris.time.PartialDateTime(year=2013,month=12,day=1) ]
    acube = load_gcm_data(timeres,vartag, datelimits=dtlims_transition, memberslist=[1100000],  returnCL=False, verbose=verbose)
    print "That worked fine."
    print "············································"



    print "Trying to exclude some members:"
    acube = load_gcm_data(timeres,vartag, datelimits=dtlims_ok, exclusionlist=members_exclude, returnCL=False, verbose=verbose)
    print "That worked fine."
    print "············································"





    print "Note: We're not testing for the presence or completeness of variables here."
    return

#===============================================================================================


















#=============================================================================================

def get_eobs_filenames(timeres,vartag,yearlimits=None, verbose=False):
    '''
    Get a list of filenames of the monthly N216 E-OBS data.

    yearlimits can be a 2-element tuple/list,
    and is used to pre-filter the list of filenames.
    '''
    if timeres != "monthly":
        print "Only monthly mean N216 E-OBS data is currently available"
        print "from the load_eobs_data() function!"
        print "But we do have daily 0.25° data available elsewhere..."
        print "See ticket 6!"
        raise UserWarning("Non-monthly data requested from load_eobs_data().")


    filename_base = EOBS_N216_MONMEANS_DIR + "eobs_"+vartag+"_n216_monthly_"
    
    if yearlimits is None:
        filenames = sorted(glob.glob(filename_base + "????.nc"))

    else:
        if len(yearlimits) != 2:
            raise UserWarning("yearlimits should be a 2-element iterable if provided.")
        
        yearlist = range(yearlimits[0], yearlimits[1]+1)
        filenames = [filename_base + "{:04d}.nc".format(year) for year in yearlist]
        filenames = [f for f in filenames if os.path.exists(f) ]
        if len(filenames) != len(yearlist):
            print "*********************************************"
            print "WARNING: Number of filenames does not match"
            print "         the requested number of years!"
            print "*********************************************"
            # but let it go through anyway...
        
    if verbose: print "Filename list for reading E-OBS data:\n" + "\n".join(filenames)

    return filenames




#----------------------------------------------------------------------------



def get_ncic5km_filenames(timeres,vartag, yearlimits=None, verbose=False):
    ''' 
    Get a list of the filenames of the monthly or daily 5km NCIC data.
    
    yearlimits can be a 2-element tuple/list,
    and is used to pre-filter the list of filenames.
    '''
    ncicvartags = dict(tas="mean-temperature", pr="rainfall")
    ncictimedirs= dict(monthly=NCIC_MONTHLY_DIR, daily=NCIC_DAILY_DIR)
    yrsuffixes =  dict(monthly=["01","12"], daily=["0101","1231"])
    try:
        thedir = ncictimedirs[timeres]
    except KeyError:
        raise UserWarning("timeres should be 'monthly' or 'daily' and you used: '"+timeres+"'.")
    
    try:
        ncicvar = ncicvartags[vartag]
    except KeyError:
        raise UserWarning("vartag '"+vartag+"' not recognised, use tas or pr instead.")

    
    filename_base = thedir + ncicvar + '/ukcp09_gridded-land-obs-'+timeres+'_5km_'+ncicvar+'_'

    yearsep = "-"  # was "_"
    if yearlimits is None:
        yeartags = "????"+yrsuffixes[timeres][0] + yearsep+"????"+yrsuffixes[timeres][1]+".nc"
        if verbose:
            print "Globbing: ",filename_base + yeartags
        filenames = sorted(glob.glob(filename_base + yeartags))

    else:
        if len(yearlimits) != 2:
            raise UserWarning("yearlimits should be a 2-element iterable if provided.")
        
        yearlist = range(yearlimits[0], yearlimits[1]+1)
        yeartags = ["{:04d}".format(year)+yrsuffixes[timeres][0] + \
                        yearsep+"{:04d}".format(year)+yrsuffixes[timeres][1] +".nc"  \
                        for year in yearlist]
        
        filenames = [filename_base + yeartag for yeartag in yeartags]
        if verbose:
            print "Checking existance of:","\n".join(filenames)
        filenames = [f for f in filenames if os.path.exists(f) ]
        if len(filenames) != len(yearlist):
            print "*********************************************"
            print "WARNING: Number of filenames does not match"
            print "         the requested number of years!"
            print "*********************************************"
            # but let it go through anyway...


    if verbose:
        print "Filename list for reading "+timeres+" "+ncicvar+" data:\n" + "\n".join(filenames)
    
    return filenames



#----------------------------------------------------------------------------




def load_eobs_data(timeres,vartag, yearlimits=None, datelimits=None, 
                   otherconstraint=None, verbose=False):
    '''Wrapper to the more general function below.'''
    thedata = load_obs_data("eobs",timeres,vartag, 
                            yearlimits=yearlimits, datelimits=datelimits,
                            otherconstraint=otherconstraint,  verbose=verbose)
    return thedata
    

def load_ncic5km_data(timeres,vartag, yearlimits=None, datelimits=None, 
                      otherconstraint=None,  verbose=False):
    '''Wrapper to the more general function below.'''
    thedata = load_obs_data("ncic5km",timeres,vartag, 
                            yearlimits=yearlimits, datelimits=datelimits,
                            otherconstraint=otherconstraint,  verbose=verbose)
    return thedata





#----------------------------------------------------------------------------------




def load_obs_data(source,timeres,vartag, yearlimits=None, datelimits=None, otherconstraint=None, 
                  verbose=False):
    '''
    Read in obs data.

    This function works with E-OBS data:
       While the original daily, 0.25° E-OBS v12 data is available 
       locally from Ségolène Berthou, I have processed that data
       into monthly means at N216, for use with the GCM data.
       The data is in separate files for each year, 1950-2015.

    and with NCIC 5km data:
        Note that this is stored on transverse Mercator grid, 
        the data also has "normal" latitude/longitude aux coords, 
        so most things will still "just work".
        The data is in separate files earch year,
        for 1910-2015 for the monthly data,
        and 1960-2015 for the daily data (from 1958 for rainfall).
        NCIC precip is monthly/daily ACCUMULATIONS (mm),
        so here we automatically convert it to the MEAN DAILY RATE (mm/day),
        to make it much easier to work with later.
    
    yearlimits can be a 2-element tuple/list,
    and is used to pre-filter the list of filenames.
    (this is actually applied in get_eobs_filenames(), not here)

    More detailed date filtering can be done on the cube when loading,
    by providing a 2-element tuple/list of datetime-like objects
    (e.g. python datetimes or iris PartialDateTimes)
    to the datelimits argument.

    Even more general filtering can be done by providing a Constraint directly
    to the otherconstraint argument.
    '''
    eobs = False
    ncic = False
    if source == "eobs":
        eobs = True
        print "Setting up reading N216 E-OBS data set..."
        # Sense check:
        if timeres != "monthly":
            print "Only monthly mean N216 E-OBS data is currently available"
            print "from the load_eobs_data() function!"
            print "But we do have daily 0.25° data available elsewhere..."
            print "See ticket 6!"
            raise UserWarning("Non-monthly data requested from load_eobs_data().")

    elif source == "ncic5km":
        ncic = True
        print "Setting up reading 5km NCIC data set"
    else:
        raise UserWarning("Obs data source '"+source+"' not recognised! Use eobs or ncic5km.")




    # Get the list of filenames to use:
    if eobs:
        filenames = get_eobs_filenames(timeres,vartag,yearlimits=yearlimits, verbose=verbose)
    if ncic:
        filenames = get_ncic5km_filenames(timeres,vartag, yearlimits=yearlimits, verbose=verbose)
    if len(filenames) == 0:
        raise UserWarning("No files found!")



    # Set up the date constraint:
    if datelimits is not None:
        if len(datelimits) != 2:
            raise UserWarning("datelimits should be a 2-element iterable if provided.")
        if type(datelimits[0]) is dt.date:
            if verbose: print "Converting dt.date objects into dt.datetime objects..."
            datelimits = [dt.datetime.combine(dtlim,dt.time()) for dtlim in datelimits]
            # (this uses the fact that dt.time() returns midnight)

        if verbose: print "Constructing date constraint from datelimits provided."
        dateconstraint = iris.Constraint(time = lambda t: 
                                         datelimits[0] <= t.point <= datelimits[1])
    else:
        if verbose: print "No date constraint provided."
        dateconstraint = None

    # Combine with any other constraint provided:
    # (note that "&" doesn't work if both are None!)
    if otherconstraint is None:
        theconstraint = dateconstraint
    else:
        theconstraint = dateconstraint & otherconstraint
        



    # Now read the data:
    if verbose: print "Reading in obs data..."
        
    with iris.FUTURE.context(cell_datetime_objects=True):    
        try:
            thedata = iris.load_cube(filenames, theconstraint)
        except:
            print "Didn't manage to load as a single cube,"
            print "loading as a CubeList and concatenating manually..."
            thedataCL = iris.load(filenames, theconstraint)
            for i,acube in enumerate(thedataCL):
                # A datetime constraint can result in just getting
                # a single time point from a file,
                # resulting in a scalar time coord 
                # - we need to promote it back to a dim coord:
                if len(acube.coord_dims('time'))==0:
                    thedataCL[i] = iris.util.new_axis(acube,scalar_coord="time")
                # The catagory coords month_number and year
                # will be preventing concatenation.
                # We can remove them here (if present)
                # and add them back if we need them later on.
                try:
                    thedataCL[i].remove_coord('month_number')
                except:
                    pass
                try:
                    thedataCL[i].remove_coord('year')
                except:
                    pass

            # This should now work:
            try:
                thedata = thedataCL.concatenate_cube()
            except iris.exceptions.ConcatenateError as err:
                print "Still failed to concatenate!"
                print "Cubelist was:"
                print thedataCL
                raise iris.exceptions.ConcatenateError(err)

    

    if verbose: print "Read in cube: \n",thedata.__repr__()

    #----------------------------------
    if source=="ncic5km" and vartag=="pr":
        if timeres=="monthly":
            print "Converting NCIC monthly precip totals to mean daily rates..."
            tunit = thedata.coord('time').units
            timebounds = tunit.num2date(thedata.coord('time').bounds)
            lodates = timebounds[:,0]
            hidates = timebounds[:,1]
            ndata = len(hidates)
            ndays_eachmonth = np.array([ (hidates[i]-lodates[i]).days for i in range(ndata)])
            #import code ; code.interact(local=locals())
            if ndata > 1:
                ndays_eachmonth_reshaped = iris.util.broadcast_to_shape(ndays_eachmonth, thedata.data.shape, (0,))
            else:
                # Just a scalar really, don't need to broadcast:
                ndays_eachmonth_reshaped = ndays_eachmonth
            thedata.data = thedata.data / ndays_eachmonth_reshaped 
            # The cube metadata will also be changed, below...
                       
        if timeres=="daily":
            print "Converting NCIC daily precip totals to mean daily rates..."
            # (Only need to change the metadata - we do the same thing
            #  in eobs_regrid_and_monthlymean.py)

        # This bit applies to both monthly and daily data
        thedata.standard_name = "lwe_precipitation_rate"
        thedata.long_name     = "precipitation rate"
        thedata.var_name      = "pr"
        thedata.units         = cf_units.Unit("mm/day")
    #----------------------------------
    

    return thedata


#----------------------------------------------------------------------------


def test_load_eobs_data():
    '''
    Just some examples really
    '''
    print "Testing load_eobs_data() function:"
    
    print "----------------------------------------"
    print "Loading precip data for 1951-1970:"
    d = load_eobs_data("monthly","pr",  yearlimits=[1951,1970], verbose=True)
    print "Done"
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"

    print "----------------------------------------"
    print "Trying to load the same as daily data:"
    try:
        d = load_eobs_data("daily","pr", yearlimits=[1951,1970], verbose=True)
    except UserWarning:
        print "Correctly failed to load daily data."
    print "----------------------------------------"

    print "----------------------------------------"
    print "Requesting temperature data partially outside date range:"
    d = load_eobs_data("monthly","tas",  yearlimits=[1940,1959], verbose=True)
    print "Done"
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"


    print "----------------------------------------"
    print "Requesting data fully outside date range:"
    try:
        d = load_eobs_data("monthly","tas", yearlimits=[1899,1940], verbose=True)
    except UserWarning:
        print "Correctly failed to find files outside date range"
    print "----------------------------------------"


    print "----------------------------------------"
    print "Requesting 1981-10-25 to 1984-01-24 only:"
    dtlims = [dt.date(1981,10,25), dt.date(1984, 1,24)]
    d = load_eobs_data("monthly","tas", datelimits=dtlims,  verbose=True)
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"


    print "----------------------------------------"
    print "Requesting DJFs only:"
    djfconstraint = iris.Constraint(time = lambda t: t.point.month in [12,1,2])
    d = load_eobs_data("monthly","tas", otherconstraint=djfconstraint,  verbose=True)
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"

    print "Done with testing load_eobs_data()..."
    return


#----------------------------------------------------------------------------


def test_load_ncic5km_data():
    '''
    Just some examples really
    '''
    print "Testing load_ncic5km_data() function:"
    
    print "----------------------------------------"
    print "Loading precip data for 1961-1980:"
    d = load_ncic5km_data("monthly","pr",  yearlimits=[1961,1980], verbose=True)
    print "Done"
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"

    print "----------------------------------------"
    print "Loading the same period as daily data:"
    d = load_ncic5km_data("daily","pr", yearlimits=[1961,1980], verbose=True)
    print "Done"
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"

    print "----------------------------------------"
    print "Requesting temperature data partially outside date range:"
    d = load_ncic5km_data("monthly","tas",  yearlimits=[1899,1915], verbose=True)
    print "Done"
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"

    print "----------------------------------------"
    print "Requesting data fully outside date range:"
    try:
        d = load_ncic5km_data("daily","tas", yearlimits=[1899,1915], verbose=True)
    except UserWarning:
        print "Correctly failed to find files outside date range"
    print "----------------------------------------"


    print "----------------------------------------"
    print "Requesting daily data 1981-10-25 to 1984-01-24 only:"
    dtlims = [dt.date(1981,10,25), dt.date(1984, 1,24)]
    d = load_ncic5km_data("daily","tas", datelimits=dtlims,  verbose=True)
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"


    print "----------------------------------------"
    print "Requesting DJFs only:"
    djfconstraint = iris.Constraint(time = lambda t: t.point.month in [12,1,2])
    d = load_ncic5km_data("monthly","tas", otherconstraint=djfconstraint,  verbose=True)
    print "Time coord:"
    print d.coord('time')
    print "----------------------------------------"

    print "Done with testing load_ncic5km_data()..."
    return



#==============================================================================================








#==============================================================================================
def load_ncic_ukmean(timeres,vartag,yearlimits=None,datelimits=None, verbose=False):
    '''
    Read in UK-mean data from a text file,
    returning the result as a Cube.

    As in other functions, 
    yearlimits is a 2-element tuple/list of ints specifying which years to include
    datelimits is a 2-element list/tuple of iris.time.PartialDateTime objects
               used to make a Constraint on the resulting Cube.

    '''
    filename = NCIC_UKMEAN_DIR + "ukmean_"+vartag+".txt"

    # Constants:
    MDI = "---"  # Missing data indicator - will replace with NaN

    # These will be used for making the cube at the end.
    # Note that the precip data in the file
    # is the ACCUMULATION over that period (month, season, year),
    # but we'll convert it here to the mean daily RATE,
    # by dividing by the number of days in the period.
    # (this will make it much easier to work with later)
    std_names = dict(tas   = "air_temperature",
                     tasmin= "air_temperature",
                     tasmax= "air_temperature",
                     pr    = "lwe_precipitation_rate")
    #                pr="lwe_thickness_of_precipitation_amount")
    longnames = dict(tas   = "mean air temperature",
                     tasmin= "time mean of daily minimum air temperature",
                     tasmax= "time mean of daily maximum air temperature",
                     pr    = "precipitation rate" )
    #                pr    = "monthly accumulated precipitation")
    units = dict(tas   = cf_units.Unit("Celsius"),
                 tasmin= cf_units.Unit("Celsius"),
                 tasmax= cf_units.Unit("Celsius"),
                 pr    = cf_units.Unit("mm/day")      )
    #            pr    = cf_units.Unit("mm")      )

    # One thing we're not setting here is the CellMethods.
    # This would distinguish nicely between tas,tasmin,tasmax.

    # This functions as a parsing test for vartag:
    try:
        print "Reading in UK-mean data for "+str(vartag)+" ("+longnames[vartag]+")"
    except KeyError:
        raise UserWarning("vartag ("+str(vartag)+") not recognised! Use tas, tasmin, tasmax, or pr.")
    #-----------------------------------------------------------------------------


    if yearlimits is not None:
        if len(yearlimits) != 2:
            raise UserWarning("yearlimits should be a 2-element iterable if provided.")
        okyears = range(yearlimits[0],yearlimits[1]+1)
        


    #-----------------------------------------------------------------------------
    # Initialise:
    thedates = []
    data = []

    # Read the data:
    with open(filename,"r") as f:
        # First, skip all header lines:
        for aline in f:
            if aline.startswith("Year    JAN"):
                break
            if verbose: print "Header line detected: ",aline
        
        # Now start reading in the data itself:
        for aline in f:
            words = aline.split() # split on whitespace of any length

            if yearlimits is not None:
                # If we're restricting by years,
                # then skip this year if it's not in our list of OK years:
                if int(words[0]) not in okyears:
                    continue

            if timeres=="monthly":
                # Dates for this year:      (place them mid-month, on the 16th)
                thisyear = [dt.datetime(int(words[0]), m,16)  for m in range(1,12+1)]
                # Data for each month this year:
                dnow = [float(word) if word!=MDI else np.nan  for word in words[1:12+1]]

            elif timeres=="seasonal":
                # Dates for this year:      (place them mid-season)
                thisyear = [dt.datetime(int(words[0]), m, 1)  for m in [1,4,7,10] ]
                # Data for each month this year:
                dnow = [float(word) if word!=MDI else np.nan  for word in words[13:16+1]]

            elif timeres=="annual":
                # Dates for this year:      (place it mid-year)
                thisyear = [dt.datetime(int(words[0]), 7, 1) ]
                # Data for each month this year:
                dnow = [float(words[17]) if words[17]!=MDI else np.nan]

            else:
                raise UserWarning("timeres ("+str(timeres)+") not recognised; use monthly, seasonal or annual.")
            
            thedates += thisyear
            data     += dnow
            if verbose:
                print thisyear
                print dnow
                print "---------------------"
    #---------------------------------------------------------
    ndata = len(data)
    if ndata == 0:
        raise UserWarning("Failed to find any data in load_ncic_ukmean")
    #---------------------------------------------------------
    
                
    
    # Convert the data to a numpy array,
    # and get the lower and upper bounds on the time points
    # (the first of the month, and the first of the next month):
    data=np.array(data)

    # The upper limit is the time point AFTER the end of the period
    # so the 1st of the next month for monthly,
    #    the 1st of the month 2 months later for seasonal,
    #  & the 1st of Jan the next year for annual.
    if timeres=="monthly":
        lodates = [dt.datetime(adate.year,adate.month,1) for adate in thedates]
        hidates = [dt.datetime(adate.year,adate.month,1) for adate in \
                       [idate+dt.timedelta(days=17) for idate in thedates]    ]

    elif timeres=="seasonal":
        lodates = [dt.datetime(adate.year,adate.month,1) for adate in \
                       [idate-dt.timedelta(days=5) for idate in thedates]    ]
        #hidates = [dt.datetime(adate.year,adate.month,1) for adate in \
        #               [idate+dt.timedelta(days=40) for idate in thedates]    ]
        hidates = [dt.datetime(adate.year,adate.month,1) for adate in \
                       [idate+dt.timedelta(days=70) for idate in thedates]    ]
    elif timeres=="annual":
        lodates = [dt.datetime(adate.year,  1,1) for adate in thedates]
        hidates = [dt.datetime(adate.year+1,1,1) for adate in thedates]


    # Make the time coord for the Cube:
    tunit = cf_units.Unit('hours since 1970-01-01 00:00:00',
                          calendar=cf_units.CALENDAR_STANDARD)
    tpoints = tunit.date2num(thedates)
    tbounds = tunit.date2num( np.array([lodates,hidates]).T )
    time_coord = iris.coords.DimCoord(tpoints, standard_name='time',
                                      units=tunit, bounds=tbounds)


    # For precip, convert from monthly/seasonal/annual accumulation
    # to monthly/seasonal/annual mean daily rate
    if vartag=="pr":
        # Use the time bounds to get the number of days in each point
        ndays = np.array([ (hidates[i]-lodates[i]).days for i in range(ndata)])
        data = data/ndays


    # Finally, make the Cube:
    thecube = iris.cube.Cube(data,
                             dim_coords_and_dims=[(time_coord,0)],
                             standard_name = std_names[vartag],
                             long_name     = longnames[vartag],
                             var_name      = vartag,
                             units         = units[vartag],
                             attributes=dict(source="NCIC UK mean from http://www-ncic/series/textfiles.html"))

        
    # Finally, extract particular date range if requested:
    if datelimits is not None:
        if len(datelimits) != 2:
            raise UserWarning("datelimits should be a 2-element iterable if specified in load_ncic_ukmean()")
        if not all([type(dtlim) is iris.time.PartialDateTime for dtlim in datelimits]):
            raise UserWarning("datelimits should be a iris.time.PartialDateTime objected!")

        dateconstraint = iris.Constraint(time = lambda t: 
                                         datelimits[0] <= t.point <= datelimits[1])
        with iris.FUTURE.context(cell_datetime_objects=True):
            thecube = thecube.extract(dateconstraint)

        # Need to test if we've ended up with nothing here too:
        if thecube is None:
            raise UserWarning("Failed to find any data after applying date constraint!")


    return thecube

#-------------------------------------------------------------------------

def test_load_ncic_ukmean():
    ''' Some simple tests '''
    print "Testing load_ncic_ukmean() function:"
    
    print "----------------------------------------"
    print "Loading UK-mean monthly tas:"
    d = load_ncic_ukmean("monthly","tas")
    print "Done. Cube:"
    print d
    print "----------------------------------------"



    print "----------------------------------------"
    print "Loading UK-mean monthly tas from 1981-2000:"
    d = load_ncic_ukmean("monthly","tas", yearlimits=[1981,2000])
    print "Done. Cube:"
    print d
    print "Time coord range:"
    print d.coord('time')[0]
    print d.coord('time')[-1]
    print "----------------------------------------"


    print "----------------------------------------"
    print "Trying to load UK-mean monthly tas from 1881-1900:"
    try:
        d = load_ncic_ukmean("monthly","tas", yearlimits=[1881,1900])
    except UserWarning:
        print "Correctly failed to load data outside year range."
    print "----------------------------------------"


    print "----------------------------------------"
    print "Loading UK-mean monthly tas from Oct 1981 to  Jan 2000:"
    datelims = [iris.time.PartialDateTime(1981,10,1),
                iris.time.PartialDateTime(2000, 1,31)]
    d = load_ncic_ukmean("monthly","tas", datelimits=datelims)
    print "Done. Cube:"
    print d
    print "Time coord range:"
    print d.coord('time')[0]
    print d.coord('time')[-1]
    print "----------------------------------------"


    print "----------------------------------------"
    print "Trying to laod UK-mean monthly tas from Aug 2018 to May 2050:"
    datelims = [iris.time.PartialDateTime(2018, 8,1),
                iris.time.PartialDateTime(2050, 5,31)]
    try:
        d = load_ncic_ukmean("monthly","tas", datelimits=datelims)
    except UserWarning:
        print "Correctly failed to load data outside date range."
    print "----------------------------------------"


    print "----------------------------------------"
    print "Loading UK-mean seasonal tas:"
    d = load_ncic_ukmean("seasonal","tas")
    print "Done. Cube:"
    print d
    print "Time coord range:"
    print d.coord('time')[0]
    print d.coord('time')[-1]
    print "Data:"
    print d.data
    print "Attempting to add auxcoords..."
    common.add_coord_categories(d)
    print d
    print "----------------------------------------"

    print "----------------------------------------"
    print "Loading UK-mean annual tas:"
    d = load_ncic_ukmean("annual","tas")
    print "Done. Cube:"
    print d
    print "Time coord range:"
    print d.coord('time')[0]
    print d.coord('time')[-1]
    print "Data:"
    print d.data
    print "----------------------------------------"


    print "----------------------------------------"
    print "Loading UK-mean monthly tasmax:"
    d = load_ncic_ukmean("monthly","tasmax")
    print "Done. Cube:"
    print d
    print "----------------------------------------"


    print "----------------------------------------"
    print "Loading UK-mean monthly tasmin:"
    d = load_ncic_ukmean("monthly","tasmin")
    print "Done. Cube:"
    print d
    print "----------------------------------------"


    print "----------------------------------------"
    print "Loading UK-mean monthly precip:"
    d = load_ncic_ukmean("monthly","pr")
    print "Done. Cube:"
    print d
    print "----------------------------------------"

    print "Done with testing load_ncic_ukmean(()..."
    return
#=================================================================











#=========================================================================
if __name__=="__main__":
    print "Testing io.py module from ukcp_common_analysis package:"
    print "============================================================"
    test_gcm_filenames()
    print "============================================================"
    test_load_gcm_data()
    print "============================================================"
    print "Done"

#=========================================================================
