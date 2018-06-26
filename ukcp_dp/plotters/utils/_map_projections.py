# -*- coding: utf-8 -*-
import cartopy.crs as ccrs


OSGB_GLOBE = ccrs.Globe(datum='OSGB36', ellipse='airy')
# See the output of the shell commands `proj -ld` and `proj -le`
# to see how these options are defined!

UKCP_OSGB = ccrs.TransverseMercator(central_longitude=-2.0,
                                    central_latitude=49.0,
                                    false_easting=400000,
                                    false_northing=-100000,
                                    scale_factor=0.9996012717,
                                    globe=OSGB_GLOBE)
