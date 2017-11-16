# -*- coding: utf-8 -*-
'''
This is a python package containing modules with functions
designed to simplify common analysis procedures for UKCP18.

See 
   http://fcm9/projects/UKCPClimateServices/wiki/StandardAnalysisAndPlottingFramework
for full details.
This package was developed by Philip Bett and the UKCP18 Climate Services team.


-----------------------------------------------
The package can be imported simply as

import ukcp_common_analysis as ukcp

although there is nothing actually defined in this package __init__.py file.
-----------------------------------------------


-----------------------------------------------
Many functions are just in the common_analysis.py module,
which you can load with 

import ukcp_common_analysis.common_analysis as common
-----------------------------------------------


-----------------------------------------------
Input/output functions, including data locations, are in the io.py module,
which can be loaded with

import ukcp_common_analysis.io as ukcpio
-----------------------------------------------


-----------------------------------------------
Functions related to defining and extracting regional data,
including averaging in regions and using shapefile-based regions,
are in the regions.py module, which can be loaded with

import ukcp_common_analysis.regions  as regs 
-----------------------------------------------


This package is being developed throughout ticket #41 and beyond...
'''
#=========================================================================

