import logging

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from ukcp_dp.constants import UKCP_OSGB
from ukcp_dp.spatial_files import (
    OVERLAY_ADMIN,
    OVERLAY_COUNTRY,
    OVERLAY_RIVER,
    OVERLAY_COUNTRY_SMALL,
    OVERLAY_RIVER_SMALL,
    OVERLAY_ADMIN_SMALL,
)


LOG = logging.getLogger(__name__)


def reg_from_cube(
    acube,
    lat_keys=["region_latmin", "region_latmax"],
    lon_keys=["region_lonmin", "region_lonmax"],
    lat_name="latitude",
    lon_name="longitude",
):
    """
    Get a region dictionary that describes a given cube.

    Checks the cube attributes first for region data,
    otherwise uses the coord bounds/points.

    May want to include a halo option in future?
    """
    try:
        lat_lims = [acube.attributes[lat_keys[0]], acube.attributes[lat_keys[1]]]
        lon_lims = [acube.attributes[lon_keys[0]], acube.attributes[lon_keys[1]]]
    except:
        LOG.debug(
            "Couldn't get region dictionary from cube attributes, using "
            "coords instead."
        )
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


def get_ukcp_shapefile_regions(regionset, region_names=None, hi_res=True):
    """
    Wrapper to get_shapefile_regions,
    for the different standard shapefiles used in the UKCP18 project.

    regionset is a string, converted to lower-case automatically,
    corresponding to one of the keys in the UKSHAPES dictionary
    (e.g. "countryplus", "admin", "countries", "riverbasins")

    region_names is an optional list of strings.
    Leave this as None for the default:
        bring back all regions in the shapefiles.
    Or provide a list of strings to be used to pull out
    just those selected regions from the shapefile.

    Note this ALWAYS returns a LIST of cartopy.io.shapereader.Record objects
    -- if len(region_names)=1,  you'll probably want to just take element [0].
    """
    regionset = regionset.lower()
    try:
        regiondata = UKSHAPES[regionset]
    except KeyError:
        LOG.error(
            "regionset was %s but it must be one of %s",
            regionset,
            "  ".join(UKSHAPES.keys()),
        )
        raise KeyError()

    if hi_res:
        sourcefile = regiondata["sourcefile"]
    else:
        sourcefile = regiondata["low_res"]
    projection = regiondata["projection"]
    attr_key = regiondata["attr_key"]

    shapefregs = _get_shapefile_regions(
        sourcefile=sourcefile,
        attr_key=attr_key,
        attr_vals=region_names,
        projection=projection,
    )
    return shapefregs


# Shapefile locations & other metadata:
UKSHAPES = dict(
    # This includes 16 subnational administrative regions:
    region=dict(
        sourcefile=OVERLAY_ADMIN,
        low_res=OVERLAY_ADMIN_SMALL,
        projection=UKCP_OSGB,
        attr_key="geo_region",
    ),
    # This includes the 4 constituent countries of the UK,
    # plus the Channel Islands and the Isle of Man
    country=dict(
        sourcefile=OVERLAY_COUNTRY,
        low_res=OVERLAY_COUNTRY_SMALL,
        projection=UKCP_OSGB,
        attr_key="geo_region",
    ),
    # This contains river basin regions:
    river=dict(
        sourcefile=OVERLAY_RIVER,
        low_res=OVERLAY_RIVER_SMALL,
        projection=UKCP_OSGB,
        attr_key="geo_region",
    ),
)


def _get_shapefile_regions(
    sourcefile,
    attr_key,
    attr_vals,
    projection=None,
    projection_key="projection_forUKCP",
):
    """
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
    We'll do this by adding it as an attribute to the returned shapefile
    objects, with the key name given by projection_key.

    This is a rather general function.
    There is a wrapper for standard UKCP18 requests below,
    called   get_ukcp_shapefile_regions().
    """

    LOG.debug("Reading shapefile %s", sourcefile)
    # Create the shapefile Reader object:
    regfileReader = shpreader.Reader(sourcefile)

    try:
        if attr_vals is None:
            LOG.debug("All available regions selected")
            attr_vals = _list_regions(regfileReader.records(), attr_key)

        # Note that this DOESN'T preserve the ordering given in attr_vals!
        selected_regions = [
            rec
            for rec in regfileReader.records()
            if rec.attributes[attr_key] in attr_vals
        ]

    except KeyError:
        LOG.error("Failed to extract shapefile regions using key %s", attr_key)
        LOG.error("Available keys in the shapefile are:")
        LOG.error("\t".join(sorted(_list_keys(regfileReader.records()))))
        raise KeyError()

    if len(selected_regions) != len(attr_vals):
        LOG.warning("Failed to return a region for all requested attribute " "values!")
        LOG.warning("Found %s regions:", len(selected_regions))
        LOG.warning(
            "\n".join([aregion.attributes[attr_key] for aregion in selected_regions])
        )
        LOG.warning("But you requested %s", attr_vals)
        LOG.warning("Available regions:")
        LOG.warning("\n".join(_list_regions(regfileReader.records(), attr_key)))
        raise UserWarning("Region mismatch")

    if projection is not None:
        LOG.debug("Imposing projection %s on the shapefile regions", projection)
        for reg in selected_regions:
            reg.attributes[projection_key] = projection

    return selected_regions


def _list_keys(records):
    """
    Simple utility function to return a list of
    the keys available for the attributes dictionary
    of the given shapefile reader records object.

    This can be handy to find out how to access
    the regions available in a given shapefile.
    """
    reg = records.next()
    return list(reg.attributes)


def _list_regions(records, key):
    """
    Simple utility function to return a list of
    the values available from the attributes
    of the given shapefile reader records object,
    under the attribute key provided.

    This can be handy to list the regions available
    in a given shapefile.
    """
    return [rec.attributes[key] for rec in records]
