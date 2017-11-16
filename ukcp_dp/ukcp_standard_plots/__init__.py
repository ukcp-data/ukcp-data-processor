# -*- coding: utf-8 -*-
'''
This is a python package for producing plots for the UKCP18 Climate Service,
including a simple class-based system to allow easy standardisation.

See 
   http://fcm9/projects/UKCPClimateServices/wiki/StandardAnalysisAndPlottingFramework
for full details.
This package was developed by Philip Bett and the UKCP18 Climate Services team.


-----------------------------------------------
The package can be imported simply as 

import ukcp_standard_plots as stdplots

so you can then access the constants in this file, 
such as the plot output directory.
-----------------------------------------------


Other modules in this package:


-----------------------------------------------
The standards_class.py module deals with the StandardMap class,
and can be loaded with:
import ukcp_standard_plots.standards_class as stds

This contains both the StandardMap definition and methods,
and all the standard StandardMap objects we need for our standard maps (!)

(users are free to make their own StandardMap objects
 for their own maps of course!)
-----------------------------------------------








-----------------------------------------------
The plotting_general.py module contains functions to
simplify setting up and finishing off plots,
adding colour bars and adjusting margins,
including wrappers for use with the StandardMap objects.
It can be loaded with 

import ukcp_standard_plots.plotting_general as plotgeneral
-----------------------------------------------


-----------------------------------------------
The mapper.py module contains a general map-plotting function
and a wrapper for use with StandardMap objects.
It can be loaded with

import ukcp_standard_plots.mapper as maps
-----------------------------------------------


-----------------------------------------------
The map_projections.py module contains our standard map projections.
It can be loaded with

import ukcp_standard_plots.map_projections as projns
-----------------------------------------------





-----------------------------------------------
REMINDER: For a VERY simple map (not using this system), just say

import matplotlib.pyplot as plt
import iris.quickplot as qplt
qplt.contourf(dhere) ; plt.gca().coastlines() ; qplt.show()


For a slightly fancier quick plot, do:
qplt.pcolormesh(dhere) ; plt.gca().coastlines("10m") ; qplt.show()
-----------------------------------------------

This package is being developed throughout ticket #41 and beyond...
'''


#=========================================================================

MAP_PLOT_DIR = '/project/ukcp18/map_plots/'



#=========================================================================
# Filenames for demonstration code:
TEST_MAPDATA_FILENAME = '/project/ukcp18/oldruns/gc2_piControl_anude/temperature_monthly_mean/anudea.pm2421dec.pp'
TEST_MAPDATA_PRECIP_DAILY_FILENAME  = '/project/ukcp18/testdata/u-ak048_daily_r001i1p00000_19101919_pr.nc' # 2 GB
TEST_MAPDATA_PRECIP_MONTHLY_FILENAME= '/project/ukcp18/testdata/u-ak048_monthly_r001i1p00000_pr.nc'        # 234 MB
TEST_MAPDATA_TEMP_MONTHLY_FILENAME  = '/project/ukcp18/testdata/u-ak048_monthly_r001i1p00000_tas.nc'       # 234 MB
# These have been copied from 
# /project/qump_hadgem3/GA7/COUPLED/u-ak048/netcdf/daily/r001i1p00000/pr/
# and
# /project/qump_hadgem3/GA7/COUPLED/u-ak048/netcdf/monthly/r001i1p00000/
# respectively, on 2017-04-03.
#=========================================================================

