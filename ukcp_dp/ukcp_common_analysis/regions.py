# -*- coding: utf-8 -*-
'''
Common definitions and functions for working with different regions.

You would usually import this module as:

import ukcp_common_analysis.regions  as regs 

--------------------------------------------------------
Contents:

* Region definitions, using dictionaries of lats and lons

* reg_extract() function, to extract a rectangular (lat/lon) region from a cube



* list_keys(): returns a list of the keys available 
               in the attributes dictionary of a shapefile-reader records object.
* list_regions(): returns a list of the values available 
                  in the attributes dictionary of a shapefile-reader records object
                  under the dictionary key provided
                 (e.g. the list of regions in a shapefile)

* list_keys_in_shapefile(): as list_keys() above, but providing a shapefile filename.
* list_regions_in_shapefile(): as list_regions() above, 
                               but providing a shapefile filename.

* get_shapefile_regions() picks particular polygon-based regions 
                          from a given shapefile (provided by filename), 
                          returning a cartopy.io.shapereader.Record object.

* get_cube_shapefileregion_weights() gets the grid cell weights 
                                     for use when applying a shapefile polygon to a cube

* get_cube_shapefileregions_weights(): wrapper to the above for multiple regions
                                       (provided as a list), 
                                       returning a list of weights arrays.

* get_ukcp_shapefile_regions() is a wrapper for the particular cases of 
                               the shapefiles we use for UKCP18. 
                               Always returns a list of cartopy.io.shapereader.Record 
                               objects.

* get_ukcp_regionalaverages() is a wrapper to get regional area-averages 
                              (or whatever statistic) for shapefiles we use in UKCP18.

* get_uk_areaaverage() is a simplified version of get_ukcp_regionalaverages(),
                       demonstrating the UK-average case specifically.
-----------------------------------------------------------------------------------
'''
import sys
import numpy as np
import iris
import iris.analysis.geometry as iag
import cf_units
import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import ukcp_dp.ukcp_standard_plots.map_projections as projns
#==========================================================================



#=========================================================================
# Some simple regional definitions:
# (these used to be in ukcp_standard_plots/standards_class.py)

# Rather than implementing a full region class
# (as in http://fcm9/projects/ClimateImpacts/browser/pbett/MyPython/pbregion_class.py)
# we're keeping it simple here and just using dictionaries.


# Regions covering the British Isles (BI):

# This is a bit tight:
REG_BI_TIGHT = dict(lons=(-11, 2),lats=(50,60)) 

# This is useful for defining plotting boundaries
# (It includes the Shetlands and the Channel Islands)
REG_BI_FULL  = dict(lons=(-11, 3),lats=(49,61))  

# Because of the projection, we probably want to use 
# something a bit bigger when extracting a region of the the data:
REG_BI_DATA = dict(lons=(-15, 5),lats=(48,63))




# Larger-scale regions:

# A test North Atlantic/European region, for GCM evaluation plots:
REG_NAE_TEST     = dict(lons=( -80,40), lats=(10,75) )
REG_NAE_BIG_TEST = dict(lons=(-100,30), lats=( 0,90) )

# A region focusing on Europe, i.e. without so much Atlantic/Africa
REG_EUROPE        = dict(lons=(-30,30), lats=(30,75) )
REG_EUROPE_TIGHT  = dict(lons=(-20,30), lats=(30,75) ) # keeps NAfrica, cuts through Iceland
REG_EUROPE_TIGHT1 = dict(lons=(-25,30), lats=(35,75) ) # Cuts NAfrica, covers Iceland
REG_EUROPE_TIGHT2 = dict(lons=(-25,30), lats=(35,72) ) # Cuts NAfrica, covers Iceland, less sea above Norway
REG_EUROPE_TIGHT3 = dict(lons=(-12,30), lats=(35,72) ) # Cuts NAfrica & Iceland, less sea above Norway


# Shapefile locations & other metadata:
UKSHAPES = dict(# The countryplus set includes the UK as well as other sub-UK countries:
                countryplus =dict(sourcefile = '/project/ukcp18/shapefiles_uk/BritishIslesPlus',
                                  projection = projns.UKCP_OSGB,
                                  attr_key   = "Region"),
                # This includes 16 subnational administrative regions:
                admin     =dict(sourcefile = '/project/ukcp18/shapefiles_uk/UK_Admin',
                                projection = projns.UKCP_OSGB,
                                attr_key   = "Region"),
                # This includes the 4 constituent countries of the UK,
                # plus the Channel Islands and the Isle of Man
                countries =dict(sourcefile = '/project/ukcp18/shapefiles_uk/BritishIsles',
                                projection = projns.UKCP_OSGB,
                                attr_key   = "Region"),
                # This contains river basin regions:
                riverbasins=dict(sourcefile = '/project/ukcp18/shapefiles_riverbasins/ERC_Catch_Dissolve_NG2',
                                 projection = projns.UKCP_OSGB,
                                 attr_key   = "BASINNAME"),
                # Including the cartopy standard Natural Earth version too,
                # mostly just for reference and comparison.
                ukNaturalEarth=dict(sourcefile = shpreader.natural_earth(resolution='10m',  #'110m',
                                                                         category  ='cultural', 
                                                                         name      ='admin_0_countries'),
                                    attr_key   = "NAME",
                                    projection = ccrs.PlateCarree()),
                )




#=========================================================================







#=========================================================================
def reg_from_cube(acube,
                  lat_keys=["region_latmin","region_latmax"], 
                  lon_keys=["region_lonmin","region_lonmax"], 
                  lat_name="latitude",lon_name="longitude"):
    '''
    Get a region dictionary that describes a given cube.

    Checks the cube attributes first for region data,
    otherwise uses the coord bounds/points.

    May want to include a halo option in future?
    '''
    try:
        lat_lims = [ acube.attributes[lat_keys[0]], acube.attributes[lat_keys[1]] ]
        lon_lims = [ acube.attributes[lon_keys[0]], acube.attributes[lon_keys[1]] ]
    except:
        print "Couldn't get region dictionary from cube attributes, using coords instead."
        latcoord = acube.coord(lat_name)
        loncoord = acube.coord(lon_name)
        #
        if latcoord.has_bounds():
            lat_lims = [latcoord.bounds.min(), latcoord.bounds.max()]
        else:
            lat_lims = [latcoord.points.min(), latcoord.points.max()]
        #
        if loncoord.has_bounds():
            lon_lims = [loncoord.bounds.min(), loncoord.bounds.max()]
        else:
            lon_lims = [loncoord.points.min(), loncoord.points.max()]


    return dict(lons=lon_lims, lats=lat_lims)
#=========================================================================








#=========================================================================
def reg_extract(acube,reg_dict=None,reg_lons=None,reg_lats=None, 
                guess_bounds=True, check_mask=True):
    '''
    Simple function to extract a rectangular (lat/lon) region.
    (an older version was in ukcp_standard_plots/mapper.py)

    Provide a dictionary with keys that start with "lat" and "lon",
    OR provide two arrays/lists/tuples, reg_lons & reg_lats.

    In any case, 2 lats and 2 lons should be provided,
    specifying the limits of the box to extract.

    Because the extracted region can differ if the coords have bounds or not,
    we always guess bounds by default if they're not present.
    (The guess_bounds argument can be used to override this behaviour)
    

    The cube.intersection operation loses any mask on the data
    if the extracted region happened to be entirely unmasked.   :(
    So we check to see if the cube data was a masked array,
    and if so, create a new (unmasked) mask for the regional cube,
    with no elements masked.
    
    This might not be ideal because checking requires accessing the data payload,
    which might not fit in memory.
    On the other hand, waiting to access the cube data until 
    AFTER extracting the region means it might fit in memory.
    So, there's an option to not check for a mask.
    You can always add a new mask later using common_analysis.add_mask()
    '''
    #---------------------------------------------
    if reg_dict is not None:
        lons = reg_dict["lons"]
        lats = reg_dict["lats"]
        if reg_lons is not None:
            print "In reg_extract, ignoring reg_lons because reg_dict has been provided!"
        if reg_lats is not None:
            print "In reg_extract, ignoring reg_lats because reg_dict has been provided!"
    else:
        try:
            lons = reg_lons
        except NameError:
            raise UserWarning("Longitudes not provided in reg_extract()!")

        try:
            lats = reg_lats
        except NameError:
            raise UserWarning("Latitudes not provided in reg_extract()!")
    #---------------------------------------------


    #---------------------------------------------
    # We'll get a different result if the Cube does or doesn't
    # have lat/lon bounds.
    # For consistency, we always guess bounds by default if they're not there.
    coordnames = ['latitude','longitude']
    for coordname in coordnames:
        if not acube.coord(coordname).has_bounds():
            if guess_bounds:
                print "Note: cube didn't have "+coordname+" bounds, guessing them..."
                acube.coord(coordname).guess_bounds()
            else:
                print "WARNING: cube didn't have "+coordname+" bounds!"
                print"          extracted region will be different than if they'd been there!"
    #---------------------------------------------


    #---------------------------------------------
    # Extract the region:
    lon_extent = iris.coords.CoordExtent(acube.coord('longitude'), lons[0], lons[1] )
    lat_extent = iris.coords.CoordExtent(acube.coord('latitude' ), lats[0], lats[1] ) #,[1] )
    dhere = acube.intersection(lon_extent,lat_extent)
    #---------------------------------------------


    #---------------------------------------------
    if check_mask:
        # If acube had a mask,
        # but the requested region was entirely unmasked,
        # then .intersection drops the .mask component!
        # So we recover it here:
        if isinstance(acube.data,np.ma.core.MaskedArray):
            if not isinstance(dhere.data, np.ma.core.MaskedArray):
                print "   Warning: Mask lost when getting region by intersection."
                print "            Regenerating mask, assuming region was not masked..."
                sys.stdout.flush()
                mask = np.full(np.size(dhere.data), False).reshape(dhere.data.shape)
                dhere.data = np.ma.array(dhere.data, mask=mask)
    #---------------------------------------------


    #---------------------------------------------
    # Add the extracted region as attribute metadata, 
    # for ease of re-use later.
    # Note we can't save dicts or lists in the attributes of netCDF files
    # (even though they are allowed in the iris Cube object)
    dhere.attributes["region_latmin"] = lats[0]
    dhere.attributes["region_latmax"] = lats[1]
    dhere.attributes["region_lonmin"] = lons[0]
    dhere.attributes["region_lonmax"] = lons[1]
    #---------------------------------------------

    return dhere
#=========================================================================






#=========================================================================
def list_keys(records):
    '''
    Simple utility function to return a list of 
    the keys available for the attributes dictionary
    of the given shapefile reader records object.

    This can be handy to find out how to access 
    the regions available in a given shapefile.
    '''
    reg = records.next()
    return reg.attributes.keys()
#------------------------------------------------------------------------


#------------------------------------------------------------------------
def list_regions(records, key):
    '''
    Simple utility function to return a list of 
    the values available from the attributes
    of the given shapefile reader records object,
    under the attribute key provided.

    This can be handy to list the regions available 
    in a given shapefile.
    '''
    return [rec.attributes[key] for rec in records]
#--------------------------------------------------------------------




#--------------------------------------------------------------------
def list_keys_in_shapefile(shapefile):
    '''
    Wrapper for even simpler probing of a shapefile:
    Just provide the shape file name (string),
    and it returns a list of keys to the attributes dictionary.
    '''
    regfileReader = shpreader.Reader(shapefile)
    return list_keys(regfileReader.records() )
#--------------------------------------------------------------------
def list_regions_in_shapefile(shapefile, key):
    '''
    Wrapper for even simpler probing of a shapefile:
    Just provide the shape file name (string)
    and a key to its attributes dictionary,
    and it returns a list of all available records in the file.
    '''
    regfileReader = shpreader.Reader(shapefile)
    return list_regions(regfileReader.records(), key)
#=========================================================================








#=========================================================================
def get_shapefile_regions(sourcefile, attr_key, attr_vals,
                          projection=None,projection_key='projection_forUKCP',
                          verbose=False):
    '''
    Get a list of shapefile polygon-based regions
    (i.e.   cartopy.io.shapereader.Record   objects)
    for use in calculating grid cell weights 
    for area-averaging (or whatever) later.
    
    sourcefile is a string giving the file/directory of the shapefiles.
    This can be returned from a function,
    e.g. cartopy.io.shapereader.natural_earth(resolution= '10m',
                                              category  = 'cultural', 
                                              name      = 'admin_0_countries')
    
    attr_key is a string specifying the key in the attribute dictionary
    to use when picking out shape in the shapefile to include.
    This will usually be something like "name",
    but there are often many name-like fields
    and you have to make sure you're picking the most appropriate one
    for your shapefile.

    attr_vals is a list of values (usually strings)
    that are in the attributes dictionary of the shapefile
    under the key specified.
    Note that ALL the values must be found in the shapefile to proceed.

    Cartopy can't interpret the projection of a shapefile,
    so we usually have to impose it by hand.
    We'll do this by adding it as an attribute to the returned shapefile objects,
    with the key name given by projection_key.

    This is a rather general function.
    There is a wrapper for standard UKCP18 requests below,
    called   get_ukcp_shapefile_regions().
    '''

    if verbose: print "Reading shapefile ",sourcefile,"..." ; sys.stdout.flush()
    # Create the shapefile Reader object:
    regfileReader = shpreader.Reader(sourcefile)

    try:
        if attr_vals is None:
            print "All available regions selected. These are:"
            attr_vals = list_regions(regfileReader.records(), attr_key)
            print "   "+"\n   ".join(attr_vals)           
            sys.stdout.flush()

        # Note that this DOESN'T preserve the ordering given in attr_vals!
        selected_regions = [rec for rec in regfileReader.records() \
                                if rec.attributes[attr_key] in attr_vals]


    except KeyError:
        print "Failed to extract shapefile regions using key ",attr_key
        print "Available keys in the shapefile are:"
        print "\t".join(sorted( list_keys(regfileReader.records()) ))
        #reg = regfileReader.records().next()
        #print "\t".join(sorted(reg.attributes.keys()))
        sys.stdout.flush()
        raise KeyError()
    
    if len(selected_regions) != len(attr_vals):
        print "Failed to return a region for all requested attribute values!"
        print "Found ",len(selected_regions)," regions:",
        print "\n".join([aregion.attributes[attr_key] for aregion in selected_regions])
        print "But you requested ",attr_vals
        print 
        print "Available regions:"
        print "\n".join(list_regions(regfileReader.records(), attr_key))
        sys.stdout.flush()
        raise UserWarning("Region mismatch")
                        



    if projection is not None:
        if verbose:
            print "Imposing projection "+str(projection)+" on the shapefile regions..."
            sys.stdout.flush()
        for reg in selected_regions:
            reg.attributes[projection_key] = projection

    return selected_regions
#=========================================================================











#=========================================================================
def get_cube_shapefileregion_weights(cube, shapefile_region, 
                                     projection_key='projection_forUKCP', 
                                     lat_name="latitude",lon_name="longitude",
                                     weightfn="area", mask=None,
                                     take_cube_shape=True, verbose=False):
    '''
    Get an array containing the weights in the grid cells of a cube
    of how much of each cell is included within a polygon 
    given by a SINGLE shapefile_region.
    (e.g. 0.0 => not in the polygon
          1.0 => entirely within the polygon
          0.5 => half-in, half-out )
    [This does *NOT* give the fraction of the polygon covered in the cell]

    (Use the wrapper get_cube_shapefileregions_weights() below
     to produce a list of arrays for the weights for a list of shapefile_regions.)

    These cell-fraction weights are then optionally FURTHER weighted 
    using either iris.analysis.cartography.area_weights             (weightfn="area")
              or iris.analysis.cartography.cosine_latitude_weights  (weightfn="coslat")
     see http://scitools.org.uk/iris/docs/latest/iris/iris/analysis/cartography.html )
    (or not at all, if weightfn=None)
    Note that the cube MUST have "latitude" and "longitude" coords
    (i.e. on a lat/lon grid) to use the "area" or "coslat" options!

    The result will then be suitable for applying to e.g. weighted means
    to get a shapefile-based regional average.

    The polygon is projected into the projection of the cube data.

        
    Supply a mask (boolean array of the right shape)
    to additionally exclude particular cells absolutely.
    (Remember the mask=True cells are EXcluded, not included!!)
        
    This will not turn the weights array into a masked array,
    but will just set the weights in those cells to zero,
    as an override.

        
    Note that the cube does not have to be solely spatial here:
    The spatial component (the slice with coords lat_name and lon_name)
    will be used to get the weights/
      
    If take_cube_shape=True, then the weights array 
    will be broadcasted back up to the full shape of the cube, 
    rather than just its spatial component.
    Note that this is just a VIEW of the spatial weights array,
    so doesn't take any time to make, nor additional memory to store.
    '''
    import shapely  # needed to catch an error
    #-----------------------------------------------------------------------
    weight_options = ["area","coslat",None]
    if weightfn not in weight_options:
        raise UserWarning("Weight function option '" + str(weightfn)+ \
                              "' not recognised.\nUse one of"+str(weight_options) )
    if weightfn is not None:
        if lat_name != "latitude" or lon_name != "longitude":
            raise UserWarning("Extra weights selected, but coords are not latitude & longitude!")

    #----------------------------------------------
    # First, project the polygon (if necessary):
    cubeproj  = cube.coord_system().as_cartopy_projection()
    shapefproj= shapefile_region.attributes[projection_key]

    if shapefproj != cubeproj:
        if verbose:
            print "   Note: Re-projecting polygon from "+str(shapefproj)+" to "+str(cubeproj)+"..."
            sys.stdout.flush()
        shape_geometry = cubeproj.project_geometry(shapefile_region.geometry, 
                                                   src_crs=shapefproj         )
    else:
        shape_geometry = shapefile_region.geometry

    # And make sure the cube's lat & lon coords have bounds:
    for coordname in [lat_name,lon_name]:
        if not cube.coord(coordname).has_bounds():
            print "Warning: cube didn't have "+coordname+" bounds, guessing them..."
            cube.coord(coordname).guess_bounds()
    #--------------------------------------------------------

    #--------------------------------------------------------
    # Now, do the work:
    spatial_cube = cube.slices([lat_name,lon_name]).next()
    print "   Getting weights..." ; sys.stdout.flush()
    try:
        weights = iag.geometry_area_weights(spatial_cube, shape_geometry, normalize=True)
        # normalize=True means the numbers are between 0 & 1 (fractions of grid cell)
        # rather than between 0 and the 'area' of a grid cell (in deg² or whatever).
        # This is important because iag.geometry_area_weights() 
        # assumes FLAT, EUCLIDIAN GEOMETRY - we have to account for 
        # variable grid cell sizes next...
        #
        # iag.geometry_area_weights needs "one, and only one, coordinate for each of the x and y axes."
    except shapely.geos.TopologicalError as cause:
        print "##### Failed to get weights, with a shapely.geos.TopologicalError: ",cause
        raise UserWarning("The shapefile should probably be fixed before proceeding.")
        #print "##### Proceeding with weights as NaNs..."
        #weights = np.full(spatial_cube.data.shape, np.nan)

    if weightfn is not None:
        print "   Getting additional weights..." ; sys.stdout.flush()
        if weightfn=="area":
            extraweights = iris.analysis.cartography.area_weights(cube, normalize=False)
        if weightfn=="coslat":
            extraweights = iris.analysis.cartography.cosine_latitude_weights(cube)
        # Apply them together:
        fullweights = weights * extraweights

    else:
        # No extra weighting
        fullweights = weights 


    # Allow a mask to override the weights where masked:
    if mask is not None:
        fullweights[mask] = 0.0
        # This will fail if mask is not the right size/shape for weights.
        # This is the intent, but you might want to replace this
        # with a try/except thing, the exception being:
        #   print "Messed up when saying weights[mask] = 0.0 in pbregion_class.py."
        #   import code ; code.interact(local=locals())   ## DEBUG ##


    if take_cube_shape:
        print "   Broadcasting up to match cube shape..." ; sys.stdout.flush()
        final_weights = np.broadcast_arrays(fullweights,cube.data)[0]
    else:
        final_weights = fullweights
    
    return fullweights
#=========================================================================












#=========================================================================
def get_cube_shapefileregions_weights(cube, shapefile_regions, 
                                      projection_key='projection_forUKCP', 
                                      lat_name="latitude",lon_name="longitude",
                                      weightfn="area", mask=None,
                                      take_cube_shape=True, verbose=False):
    '''
    Wrapper to get_cube_shapefileregion_weights(), returning a LIST of arrays
    containing the weights in the grid cells of a cube
    of how much of each cell is included within a polygon 
    given by each shapefile_region in the list shapefile_regions.

    (each shapefile_region is a cartopy.io.shapereader.Record object
     e.g. returned by get_shapefile_regions() )
    
    All options are passed through to get_cube_shapefileregion_weights().

    '''
    allregion_weights = []
    nregions = len(shapefile_regions)
    for i, aregion in enumerate(shapefile_regions):
        print "Processing region ",i+1,"/",nregions
        print "   Attributes: ",aregion.attributes
        sys.stdout.flush()
        thisregion_weights = get_cube_shapefileregion_weights(cube, aregion,
                                                              projection_key=projection_key,
                                                              lat_name=lat_name,
                                                              lon_name=lon_name,
                                                              weightfn=weightfn, 
                                                              mask=mask,
                                                              take_cube_shape=take_cube_shape,
                                                              verbose=verbose)
        allregion_weights.append(thisregion_weights)

    return allregion_weights
#=========================================================================

















#=========================================================================
# Wrappers to easily get UK/regional averages:


#-------------------------------------------------------------------------
def get_ukcp_shapefile_regions(regionset, region_names=None):
    '''
    Wrapper to get_shapefile_regions, 
    for the different standard shapefiles used in the UKCP18 project.
    
    regionset is a string, converted to lower-case automatically,
    corresponding to one of the keys in the UKSHAPES dictionary
    (e.g. "countryplus", "admin", "countries", "riverbasins")

    region_names is an optional list of strings.
    Leave this as None for the default:  bring back all regions in the shapefiles.
    Or provide a list of strings to be used to pull out
    just those selected regions from the shapefile.

    Note this ALWAYS returns a LIST of cartopy.io.shapereader.Record objects
    -- if len(region_names)=1,  you'll probably want to just take element [0].
    '''
    regionset = regionset.lower()
    try:
        regiondata = UKSHAPES[regionset]
    except KeyError:
        print "regionset was "+str(regionset)+" but it must be one of "+"  ".join(UKSHAPES.keys())
        sys.stdout.flush()
        raise KeyError()


    sourcefile = regiondata['sourcefile']
    projection = regiondata['projection']
    attr_key   = regiondata['attr_key']
    if regionset == "ukNaturalEarth":
        region_names = ["United Kingdom"]

    shapefregs = get_shapefile_regions(sourcefile=sourcefile, attr_key=attr_key,
                                       attr_vals=region_names,
                                       projection=projection )
    return shapefregs
#-------------------------------------------------------------------------
    





#-------------------------------------------------------------------------
def get_ukcp_regionalaverages(acube, regionset, region_names=None, weights=None,
                              weightfn="area", mask=None,
                              operation=iris.analysis.MEAN,
                              lat_name="latitude",lon_name="longitude",
                              verbose=True):
    '''
    Wrapper for getting regional area-averages for UKCP18.
    
    regionset is a string, converted to lower-case automatically,
    corresponding to one of the keys in the UKSHAPES dictionary
    (e.g. "countryplus", "admin", "countries", "riverbasins")
    
    region_names is an optional list of strings.
    Leave this as None for the default:  bring back all regions in the shapefiles.
    Or provide a list of strings to be used to pull out
    just those selected regions from the shapefile.

    If you have already computed the regional weights, 
    then they can be provided here to save time.
    
    The results are output as a tuple of:
       * a CubeList (one cube per region),
       * and a list of arrays of weights

    We don't guarentee the order of regions with the CubeList and list-of-weights,
    but they will both be in the same order, 
    and the Cubes will contain the necessary metadata to identify the region.
    
    '''
    print "Reading shapefile..."
    regs = get_ukcp_shapefile_regions(regionset, region_names=region_names)
    
    if weights is None:
        print "Getting weights..."
        weights = get_cube_shapefileregions_weights(acube, regs, 
                                                    projection_key='projection_forUKCP', 
                                                    lat_name=lat_name, lon_name=lon_name,
                                                    weightfn=weightfn, mask=mask,
                                                    take_cube_shape=True, verbose=verbose)
    else:
        print "Using weights provided..."
    


    print "Getting area statistics:"
    theCL = iris.cube.CubeList()
    reg_key = UKSHAPES[regionset]["attr_key"]
    # This relies on the list of weights being in the same order as the regs list.
    for i,aregion in enumerate(regs):
        reg_cube = acube.collapsed([lon_name,lat_name], operation, weights=weights[i] )
        reg_cube.attributes["region_set"] = regionset
        reg_cube.attributes["region_name"]= aregion.attributes[reg_key]
        theCL.append(reg_cube)


    return (theCL, weights)
#-------------------------------------------------------------------------







#-------------------------------------------------------------------------
def get_uk_areaaverage(acube):
    '''
    Wrapper getting the area-average for the UK.
    Note that in practice, you might want additional statistics
    (e.g. standard deviation)
    so it would be better to do the reading and calculation of weights
    once only, and re-use them.
    
    So this is an example function more than anything!
    '''
    print "Reading shapefile..."
    #reg = get_uk_shapefile_region()
    #reg = get_ukcp_shapefile_regions("uk")[0]

    # An alternative would be to use the Natural Earth shapefiles:
    #reg = get_ukcp_shapefile_regions("ukNaturalEarth")[0]
    # but this is our standard approach:
    reg = get_ukcp_shapefile_regions("countryplus", region_names=["UK"])[0]

    print "Getting weights..."
    weights = get_cube_shapefileregion_weights(acube, reg, weightfn="area",
                                               mask=None,take_cube_shape=True)

    print "Getting area-average:"
    area_average = acube.collapsed(['longitude','latitude'],iris.analysis.MEAN,weights=weights)
    
    return area_average
#=========================================================================








#=========================================================================
if __name__=="__main__":
    print "Testing regions.py module from ukcp_common_analysis package:"
    print "--------------"
    print "(no tests set up yet)"
    print "--------------"
    print "Done"

#=========================================================================
