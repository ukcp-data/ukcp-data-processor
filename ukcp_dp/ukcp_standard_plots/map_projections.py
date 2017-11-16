# -*- coding: utf-8 -*-
'''
This module also defines some standard map projections,
which can be used when plotting maps, or regridding data etc.



It was necessary to move this out to a separate file
because both ukcp_common_analysis.regions needed it,
and the StandardMap objects in ukcp_standard_plots.standards_class
also needed both the projections AND the standard regions,
so we'd end up with a circular reference.

In any case, it is only a temporary fix -- eventually,
this will all be defined in JSON files on GitHub.




Standard use:

import ukcp_standard_plots.map_projections as projns

'''
import cartopy.crs as ccrs


#=========================================================================
# Handy map projections.
UKCP_OSGB = ccrs.TransverseMercator(central_longitude=-2.0, central_latitude=49.0,
                                    false_easting=400000, false_northing=-100000,
                                    scale_factor=0.9996012717, 
                                    globe=ccrs.Globe(datum='OSGB36', ellipse='airy'))
# This is a copy of the projection parameters of cartopy.crs.OSGB()
# http://scitools.org.uk/cartopy/docs/latest/_modules/cartopy/crs.html#OSGB
# but without specifying the plot boundaries like OSGB does.
# This makes it much more flexible and easier to use when plotting.



UKCP_NAE_LATLON = ccrs.PlateCarree(central_longitude=-20)

# Probably want a projection for an NAE region too...
# Other projections that might be useful:
#        ccrs.PlateCarree(central_longitude=11.0)
#        ccrs.Mollweide(central_longitude=11.0)
#        ccrs.Orthographic(central_longitude=-1.0, central_latitude=55.0)
#        ccrs.Robinson(central_longitude=50)


UKCP_EUR_LATLON = ccrs.PlateCarree(central_longitude=10)


#=========================================================================



