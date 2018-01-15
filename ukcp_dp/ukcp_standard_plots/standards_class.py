# -*- coding: utf-8 -*-
'''
This module defines a class for storing standard map settings,
for ease of use and reproducibility.
(Many of the map settings can be used with other plots too)



As well as the StandardMap definition, 
this module also defines some standard map projections,

and creates the standard StandardMap objects used
for making our standard maps (!).

(Users can - and should - of course make their own StandardMap objects
 for use with their own bespoke maps!)



Mapping and other plotting functions can be found 
in the mapper,py and plotting_general.py modules 
within this package.

Definitions of regions for plots can be found in 
the regions.py module of the ukcp_common_analysis package.
'''
#=========================================================================
import copy
#import numpy as np
#import iris
#import cartopy
import cf_units
import cartopy.crs as ccrs
import map_projections              as projns
import ukcp_dp.ukcp_common_analysis.regions as regs
#=========================================================================






#======================================================
class StandardMap(object):
    '''
    '''
    def __init__(self, tag,cont=False,vrange=[-1,1],vstep=0.2, vmid=None,
                 cpal="RdBu_r",bar_orientation="horizontal",extendcolbar="both",
                 bar_position=None,
                 maskcol=(1,1,1,1), undercol="magenta",overcol="yellow",
                 figbackgroundcol=(1,1,1,1),
                 cmsize=[23,18], dpi=94, fsize=12, fontfam="Arial",
                 proj=ccrs.PlateCarree(),
                 marlft=0.03,marrgt=0.97,martop=0.96,marbot=0.06,
                 marwsp=0,marhsp=0,
                 contlines=None,contlinealpha=1,
                 contlinew=1,   contlinecol="yellow",
                 countrylw=1,   countrylcol='grey',
                 regionlw =1,   regionlcol=None,
                 riverslw =1,   riverslcol=None,
                 coastlw  =1,    coastlcol="black", 
                 default_barlabel="Unknown", preferred_unit=None,
                 xlims=None,ylims=None, showglobal=False,
                 dxgrid=5,dygrid=5, xgridax=[True,False], ygridax=[True,False] ):
        '''
        tag could be used in filenames and printing to screen,
        so you'd usually set it to be the same as the object name,
        but as you can have different pointers to the same object
        it should have its own name stored here.

        Reasonable defaults are set for all options
        so that when making a new object 
        you only have to change the things that are different.
        These aren't "recommended" options!
        They are just defaults that will allow it to run.
        '''
        self.tag=tag                              # Brief name of the object
        self.cont=cont                            # plot as [filled] contours (True), or pixels (False)?
        
        self.vrange=vrange                        # value range: [min,max]
        self.vstep=vstep                          # value step 
        self.vmid=vmid                            # value midpoint (for when using a diverging colour palette) 
        self.cpal=cpal                            # colour palette name, 
        #                                           http://matplotlib.org/examples/color/colormaps_reference.html

        self.default_barlabel=default_barlabel    # Default colour-bar label string
        self.bar_orientation=bar_orientation      # Colour-bar orientation: "horizontal","vertical", "none"
        self.bar_position=bar_position            # Position of the colour-bar Axes: [left,bottom, width,height]
        self.extendcolbar=extendcolbar            # Extend the colour bar? 'neither', 'min', 'max', 'both'

        self.maskcol=maskcol                      # Colour to use for masked areas
        self.undercol=undercol                    # Colour to use for values below the minimum
        self.overcol=overcol                      # Colour to use for values above the maximum
        self.figbackgroundcol=figbackgroundcol    # Colour to use for the Figure object background
        self.cmsize=cmsize                        # Size in cm of the Figure, as a tuple/list: (width,height)
        self.dpi=dpi                              # Resolution of the Figure, in dots per inch
        self.fsize=fsize                          # Font size, in points 
        self.fontfam=fontfam                      # Font family name
        self.proj=proj                            # Map projection: should be a Cartopy CRS object

        # For the margins, if all 4 are set to None then tight_layout() is used instead.
        self.marlft=marlft                        # Left margin
        self.marrgt=marrgt                        # Right margin
        self.martop=martop                        # Top margin
        self.marbot=marbot                        # Bottom margin
        self.marwsp=marwsp                        # Width spacing between subplots
        self.marhsp=marhsp                        # Height spacing between subplots

        self.contlines    =contlines              # Values at which to plot additional contours
        self.contlinew    =contlinew              # Contour line width
        self.contlinecol  =contlinecol            # Contour line colour
        self.contlinealpha=contlinealpha          # Contour line alpha (transparency)

        self.countrylw  =countrylw                # Country borders line width
        self.countrylcol=countrylcol              # Country borders line colour (omit if None)
        # This uses the international borders from Natural Earth.

        self.regionlw  =regionlw                  # Subnational region line width
        self.regionlcol=regionlcol                # Subnational region line colour (omit if None)
        # This uses subnational regions from Natural Earth, and probably shouldn't be used.

        # The coastline and rivers are also from Natural Earth:
        self.coastlw   =coastlw                   # Coastline width
        self.coastlcol =coastlcol                 # Coastline colour (omit if None)
        self.riverslw  =riverslw                  # Rivers line width
        self.riverslcol=riverslcol                # Rivers line colour (omit if None)
        
        self.preferred_unit = preferred_unit      # Preferred unit to convert the data into

        self.xlims=xlims                          # x-axis limits [min,max]  (often longitude)
        self.ylims=ylims                          # y-axis limits [min,max]  (often latitude)
        self.showglobal=showglobal                # True/False to force showing the whole globe
        self.dxgrid=dxgrid                        # grid spacing in the x direction
        self.dygrid=dygrid                        # grid spacing in the y direction
        self.xgridax = xgridax                    # True/False switches for axis labels: [left-axis, right-axis]
        self.ygridax = ygridax                    # True/False switches for axis labels: [bottom-axis, top-axis]
    #-------------------------------------------

    # ==== METHODS =============================

    #-------------------------------------------
    def copy(self):
        '''
        Handy copy method.
        Use this to prevent accidentally
        editing an old/existing object!
        '''
        return copy.copy(self)
    #-------------------------------------------



    #-------------------------------------------
    def set_xylims(self, reg_dict):
        '''
        Convenience function to set xlims and ylims
        from a region dictionary (as used in ukcp_common_analysis.regions)
        '''
        self.xlims = reg_dict['lons']
        self.ylims = reg_dict['lats']
    #-------------------------------------------
    
    #-------------------------------------------
    def set_margins(self,left=None,right=None,bottom=None,top=None,
                    wspace=None, hspace=None):
        '''
        Convenience function to set margin components.
        Arguments are optional, so you can just set the one(s) you want.
        '''
        if left   is not None: self.marlft = left
        if right  is not None: self.marrgt = right
        if bottom is not None: self.marbot = bottom
        if top    is not None: self.martop = top
        if wspace is not None: self.marwsp = wspace
        if hspace is not None: self.marhsp = hspace
    #-------------------------------------------
    
    
    #-------------------------------------------
    def __str__(self):
        '''
        Provide a descriptive string representation of the object:
        '''
        thestr  = ""
        thestr += "StandardMap object:" + self.tag +"\n"
        thestr += "  Plot as filled contours? cont = "+str(self.cont) +"\n"
        thestr += "  Value range:          vrange = "+str(self.vrange) +"\n" #str(self.vrange[0])+","+str(self.vrange[1])+"]" +"\n"
        thestr += "  Value step:           vstep  = "+str(self.vstep) +"\n"
        thestr += "  Value divergence point  vmid = "+str(self.vmid)  +"\n"
        thestr += "  Colour palette name:    cpal = "+self.cpal +"\n"
        thestr += "  Default colour bar label: default_barlabel = "+str(self.default_barlabel) +"\n"
        thestr += "  Preferred unit for data: preferred_unit = "+str(self.preferred_unit)  +"\n"
        thestr += "  Colour bar orientation: bar_orientation = "+str(self.bar_orientation) +"\n"
        thestr += "  Colour bar explicit position [l,b,w,h]: = "+str(self.bar_position) +"\n"
        thestr += "  Extend the colour bar?     extendcolbar = "+self.extendcolbar    +"\n"
        thestr += "  Colour for masked/blank areas: maskcol   = "+str(self.maskcol) +"\n"
        thestr += "  Colour for underflow: undercol = "+str(self.undercol) +"\n"
        thestr += "  Colour for overflow:  overcol  = "+str(self.overcol) +"\n"
        thestr += "  Colour for Figure background: figbackgroundcol = "+str(self.figbackgroundcol) + "\n"
        thestr += "  Figure size (cm):   cmsize  = ["+str(self.cmsize[0])+","+str(self.cmsize[1])+"]\n"
        thestr += "  Figure DPI:         dpi     = "+str(self.dpi) +"\n"
        thestr += "  Figure font size:   fsize   = "+str(self.fsize) +"\n"
        thestr += "  Figure font family: fontfam = "+self.fontfam +"\n"
        thestr += "  Map projection object: proj = "+str(self.proj) +"\n"
        thestr += "  Margins l/r: [marlft,marrgt] = "+str(self.marlft)+","+str(self.marrgt) +"\n"
        thestr += "  Margins t/b: [martop,marbot] = "+str(self.martop)+","+str(self.marbot) +"\n"
        thestr += "  Spacing w/h: [marwsp,marhsp] = "+str(self.marwsp)+","+str(self.marhsp) +"\n"

        if self.contlines is not None:
            thestr += "  Additional contour lines at:    contlines    = "+str(self.contlines) +"\n"
            thestr += "  Additional contour line colour: contlinecol  = "+str(self.contlinecol) +"\n"
            thestr += "  Additional contour line width:  contlinew    = "+str(self.contlinew) +"\n"
            thestr += "  Additional contour line alpha:  conlinealpha = "+str(self.contlinealpha) +"\n"

        if self.countrylcol is not None:
            thestr += "Will plot countries:\n"
            thestr += "  cartopy.feature.NaturalEarthFeature('cultural','admin_0_boundary_lines_land','10m')\n"
            thestr += "  Country border colour: countrylcol = "+str(self.countrylcol) +"\n"
            thestr += "  Country border width:  countrylw   = "+str(self.countrylw) +"\n"
        else:
            thestr += "(not plotting cartopy.feature.NaturalEarthFeature countries)\n"

        if self.regionlcol is not None:
            thestr += "Will plot subnational regions:"
            thestr += "  cartopy.feature.NaturalEarthFeature('cultural','admin_1_states_provinces_lines','10m')\n"
            thestr += "  Region border colour: regionlcol = "+str(self.regionlcol) +"\n"
            thestr += "  Region border width:  regionlw   = "+str(self.regionlw) +"\n"
        else:
            thestr += "(not plotting cartopy.feature.NaturalEarthFeature subnational regions)\n"

        if self.riverslcol is not None:
            thestr += "Will plot rivers:\n"
            thestr += "  cartopy.feature.NaturalEarthFeature('physical','rivers_lake_centerlines','50m')\n"
            thestr += "  Rivers line colour: riverslcol = "+str(self.riverslcol) +"\n"
            thestr += "  Rivers line width:  riverslw   = "+str(self.riverslw) +"\n"
        else:
            thestr += "(not plotting cartopy.feature.NaturalEarthFeature rivers)\n"

        thestr += "  Coastline width:   coastlw    = "+str(self.coastlw) +"\n"
        thestr += "  Coastline colour:  coastlcol  = "+str(self.coastlcol) +"\n"

        thestr += "  Longitude limits: xlims = "+str(self.xlims) +"\n"
        thestr += "  Latitude  limits: ylims = "+str(self.ylims) +"\n"
        thestr += "  Force showing whole globe? showglobal = "+str(self.showglobal) +"\n"
        thestr += "  Longitude grid lines every: dxgrid = "+str(self.dxgrid) +"\n"
        thestr += "  Latitude  grid lines every: dygrid = "+str(self.dygrid) +"\n"
        thestr += "  Longitude grid labels on [bottom,top]? xgridax = "+str(self.xgridax) +"\n"
        thestr += "  Latitude  grid labels on [left,right]? ygridax = "+str(self.ygridax) +"\n"
        
        return thestr
    #-------------------------------------------

    #-------------------------------------------
    def __repr__(self):
        '''
        Ideally this should be a string representation that
        we can give to eval() to reconstruct the object...

        ... but that would be complicated and we're just
        returning self.__str__() instead.
        '''
        return self.__str__()
    #-------------------------------------------

#======================================================



#======================================================
# StandardMap object definitions
#======================================================

# A basic functional StandardMap object for the UK.
# This is unlikely to ever be sufficient on its own without modification!
UKCPBASIC = StandardMap("UKCPbasic",cont=False,vrange=[270,290],vstep=2,
                        cpal="YlOrRd",bar_orientation="horizontal",
                        maskcol=(1,1,1, 1),undercol="magenta",overcol="green",
                        figbackgroundcol=(1,1,1,1),
                        cmsize=[23,18], dpi=94, fsize=12, fontfam="Arial",
                        proj=ccrs.PlateCarree(),
                        marlft=0.03,marrgt=0.97,martop=0.96,marbot=0.06,
                        countrylw=1, countrylcol='grey',
                        regionlw =1,  regionlcol=None,
                        coastlw  =1,   coastlcol="black",
                        dxgrid=5,dygrid=5)

# This object forms the basis of all the variable-specific objects below,
# and provides the figure size/proportions and margins:
UKCPNEAT = StandardMap("UKCPneat",cont=False,vrange=[276,288],vstep=1,vmid=None,
                       cpal="YlOrRd",bar_orientation="vertical",extendcolbar="both",
                       maskcol=(1,1,1, 1),undercol="magenta",overcol="green",
                       figbackgroundcol=(1,1,1, 1),
                       cmsize=[15.5,17], dpi=94, fsize=12, fontfam="Arial",
                       proj=projns.UKCP_OSGB,
                       marlft=0.01,marrgt=1.00,martop=0.99,marbot=0.02,
                       countrylw=1, countrylcol='grey',
                       regionlw =1, regionlcol=None,
                       coastlw  =1,  coastlcol="black", dxgrid=1,dygrid=1,
                       xlims=regs.REG_BI_FULL['lons'], ylims=regs.REG_BI_FULL['lats']
                       )
# Note that with these proportions, setting 
#     marlft=None,marrgt=None,martop=None,marbot=None,
# and thus triggering tight_layout(),
# is fine, but actually results in slightly smaller plots,
# so we'll stick to specifying the margins here.

 
#----------------- VARIABLE-SPECIFIC OBJECTS ---------------------------
# We may want different value ranges for daily/monthly/seasonal data?


# Air temperatures.
UKCP_TEMP = UKCPNEAT.copy()
UKCP_TEMP.tag = "UKCP_temp"
UKCP_TEMP.default_barlabel = "Temperature, $^\circ$C"
UKCP_TEMP.preferred_unit = cf_units.Unit("Celsius")
UKCP_TEMP.cpal = "RdBu_r"
UKCP_TEMP.vrange = [-4.0, 14.0]
UKCP_TEMP.vmid   = 0.0
UKCP_TEMP.vstep  = 2.0


# Temperature anomalies.
# (some would prefer temperature differences/changes to always 
#  be in Kelvin rather than °Celsius. Sticking to °C is clearer though)
# NOTE though, that if you already have a temperature difference in Kelvin,
#      you DO NOT want to do a Cube.convert_units on it (subtracting off 273.15!)
#      but instead just manually override the Cube.units with this unit.
#      This is done automatically in ukcp_common_analysis.common_analysis.make_anomaly()
#      if the preferred_unit is set to the preferred_unit here.
UKCP_TEMP_ANOM = UKCP_TEMP.copy()
UKCP_TEMP_ANOM.tag = "UKCP_temp_anom"
UKCP_TEMP_ANOM.default_barlabel = "Temperature anomaly, $^\circ$C"
UKCP_TEMP_ANOM.preferred_unit = cf_units.Unit("Celsius")
UKCP_TEMP_ANOM.vrange = [-10.0, 10.0]
UKCP_TEMP_ANOM.vmid   = 0.0
UKCP_TEMP_ANOM.vstep  = 1.0





# Precipitation rate.
UKCP_PRECIP = UKCPNEAT.copy()
UKCP_PRECIP.tag = "UKCP_precip"
UKCP_PRECIP.default_barlabel = "Precipitation rate, mm day$^{-1}$"
#KCP_PRECIP.default_barlabel = "Precipitation rate, mm/day"
UKCP_PRECIP.preferred_unit = cf_units.Unit("mm/day")
UKCP_PRECIP.extendcolbar = "max"
UKCP_PRECIP.cpal = "Blues"
UKCP_PRECIP.vrange = [0.0, 8.0]
UKCP_PRECIP.vmid   = None
UKCP_PRECIP.vstep  = 1.0

# Precipitation rate anomalies
#   Note that this is in %, not mm/day!
#   This is done automatically in ukcp_common_analysis.common_analysis.make_anomaly()
#   if the preferred_unit is set to the preferred_unit here.
UKCP_PRECIP_ANOM = UKCP_PRECIP.copy()
UKCP_PRECIP_ANOM.tag = "UKCP_precip_anom"
UKCP_PRECIP_ANOM.preferred_unit = cf_units.Unit("%")
UKCP_PRECIP_ANOM.default_barlabel = "Precipitation rate anomaly, %"
#KCP_PRECIP_ANOM.default_barlabel = "Precipitation rate anomaly, mm day$^{-1}$"
#KCP_PRECIP_ANOM.default_barlabel = "Precipitation rate anomaly, mm/day"
UKCP_PRECIP_ANOM.extendcolbar = "both"
UKCP_PRECIP_ANOM.cpal = "BrBG"
UKCP_PRECIP_ANOM.vrange = [-5.0, 5.0]
UKCP_PRECIP_ANOM.vmid   = 0.0
UKCP_PRECIP_ANOM.vstep  = 1.0





# Wind speed.
UKCP_WIND = UKCPNEAT.copy()
UKCP_WIND.tag = "UKCP_wind"
UKCP_WIND.default_barlabel = "Wind speed, m s$^{-1}$"
#KCP_WIND.default_barlabel = "Wind speed, m/s$"
UKCP_WIND.preferred_unit = cf_units.Unit("m/s")
UKCP_WIND.extendcolbar = "max"
UKCP_WIND.cpal = "Greens"
UKCP_WIND.vrange = [0.0, 15.0]
UKCP_WIND.vmid   = None
UKCP_WIND.vstep  = 2.0

# Wind speed anomalies.
UKCP_WIND_ANOM = UKCP_WIND.copy()
UKCP_WIND_ANOM.tag = "UKCP_wind_anom"
UKCP_WIND_ANOM.default_barlabel = "Wind speed anomaly, m s$^{-1}$"
#KCP_WIND_ANOM.default_barlabel = "Wind speed anomaly, m/s$"
UKCP_WIND_ANOM.extendcolbar = "both"
UKCP_WIND_ANOM.cpal = "PrGn"
UKCP_WIND_ANOM.vrange = [-5.0, 5.0]
UKCP_WIND_ANOM.vmid   = 0.0
UKCP_WIND_ANOM.vstep  = 1.0

#=========================================================================



#=========================================================================
# For the NAE region, the plots will have different proportions.
# One standard plot will be a 4-panel set of maps.
# The general settings for this:
UKCP_NAE_SEAS = UKCPNEAT.copy()
UKCP_NAE_SEAS.tag = "UKCP_NAE_seas"
UKCP_NAE_SEAS.default_barlabel = "unknown"
UKCP_NAE_SEAS.cmsize = [20,13]
UKCP_NAE_SEAS.set_margins(left  = 0.01,  bottom = 0.17,
                          right = 0.99,  top    = 0.99,
                          wspace= 0.03,  hspace = 0.03 )
UKCP_NAE_SEAS.bar_orientation = "horizontal"
UKCP_NAE_SEAS.bar_position = [0.05, 0.10, 0.9, 0.03] #[l,b,w,h]
UKCP_NAE_SEAS.set_xylims(regs.REG_NAE_TEST)
UKCP_NAE_SEAS.cont = True                   # Plot as contours
UKCP_NAE_SEAS.countrylcol=None              # Don't plot country borders
UKCP_NAE_SEAS.coastlw= 0.7                  # Make the coastline a bit thinner
UKCP_NAE_SEAS.dxgrid=10                     # Wider gridlines
UKCP_NAE_SEAS.dygrid=10
UKCP_NAE_SEAS.proj = projns.UKCP_NAE_LATLON        # Simple Plate Carée projection



# Variable-specific versions:
UKCP_NAE_SEAS_MEAN_BIAS_TEMP = UKCP_NAE_SEAS.copy()
UKCP_NAE_SEAS_MEAN_BIAS_TEMP.tag = "UKCP_NAE_seas_temp_bias"
UKCP_NAE_SEAS_MEAN_BIAS_TEMP.default_barlabel = "Temperature bias, $^\circ$C, seasonal mean"
UKCP_NAE_SEAS_MEAN_BIAS_TEMP.preferred_unit = UKCP_TEMP_ANOM.preferred_unit
UKCP_NAE_SEAS_MEAN_BIAS_TEMP.cpal = UKCP_TEMP_ANOM.cpal
# Will probably still want to change these:
UKCP_NAE_SEAS_MEAN_BIAS_TEMP.vrange = [-10,6]
UKCP_NAE_SEAS_MEAN_BIAS_TEMP.vstep  = 1.0
UKCP_NAE_SEAS_MEAN_BIAS_TEMP.vmid   = 0.0


UKCP_NAE_SEAS_MEAN_BIAS_PRECIP = UKCP_NAE_SEAS.copy()
UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.tag = "UKCP_NAE_seas_precip_bias"
UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.default_barlabel = "Precipitation rate bias, %, seasonal mean"
UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.preferred_unit = UKCP_PRECIP_ANOM.preferred_unit
UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.cpal = UKCP_PRECIP_ANOM.cpal
# Will probably still want to change these:
#UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.vrange = [-1,1]
#UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.vstep  = 0.2
#UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.vrange = [-100.0, 360.0]
UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.vrange = [-100.0, 200.0]
UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.vstep  = 20
UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.vmid   = 0.0




UKCP_EUR_SEAS_MEAN_BIAS_TEMP = UKCP_NAE_SEAS_MEAN_BIAS_TEMP.copy()
UKCP_EUR_SEAS_MEAN_BIAS_TEMP.tag = "UKCP_EUR_seas_temp_bias"
UKCP_EUR_SEAS_MEAN_BIAS_TEMP.set_xylims(regs.REG_EUROPE_TIGHT3)
UKCP_EUR_SEAS_MEAN_BIAS_TEMP.proj = projns.UKCP_EUR_LATLON
UKCP_EUR_SEAS_MEAN_BIAS_TEMP.cmsize = [12,13]
UKCP_EUR_SEAS_MEAN_BIAS_TEMP.set_margins(left  = 0.01,  bottom = 0.17,
                                         right = 0.99,  top    = 0.99,
                                         wspace= 0.03,  hspace = 0.03 )
UKCP_EUR_SEAS_MEAN_BIAS_TEMP.vrange = [-10,4]


UKCP_EUR_SEAS_MEAN_BIAS_PRECIP = UKCP_NAE_SEAS_MEAN_BIAS_PRECIP.copy()
UKCP_EUR_SEAS_MEAN_BIAS_PRECIP.tag = "UKCP_EUR_seas_precip_bias"
UKCP_EUR_SEAS_MEAN_BIAS_PRECIP.set_xylims(regs.REG_EUROPE_TIGHT3)
UKCP_EUR_SEAS_MEAN_BIAS_PRECIP.proj = projns.UKCP_EUR_LATLON
UKCP_EUR_SEAS_MEAN_BIAS_PRECIP.cmsize = [12,13]
UKCP_EUR_SEAS_MEAN_BIAS_PRECIP.set_margins(left  = 0.01,  bottom = 0.17,
                                           right = 0.99,  top    = 0.99,
                                           wspace= 0.03,  hspace = 0.03 )
#UKCP_EUR_SEAS_MEAN_BIAS_PRECIP.vrange = [-100.0, 140.0]
UKCP_EUR_SEAS_MEAN_BIAS_PRECIP.vrange = [-80.0, 140.0]




#=========================================================================








#=========================================================================
if __name__=="__main__":
    print "Demonstrating print of UKCPBASIC StandardMap object:"
    print "--------------"
    mysettings = UKCPNEAT.copy()
    print mysettings
    print "--------------"
    print "Done"

#=========================================================================
