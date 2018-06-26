# -*- coding: utf-8 -*-
import logging

import cf_units
import iris
import numpy as np


log = logging.getLogger(__name__)


def add_mask(datacube, maskcube, comparator=">=", threshold=1):
    """
    Take a cube of data (datacube) and additionally-mask values
    specified using the maskcube, comparator and threshold.

    e.g. comparator=">" and threshold=1
    means that datacube is (additionally) masked where maskcube > 1

    comparator can be a string of ["==","=", ">",">=", "<","<="]
    or any function with signature (x,threshold) where x is an array
    e.g. from the operator package:
    operator.gt, operator.ge, operator.lt, operator.le etc


    So if you have a mask where 1 ==> land, and 0 ==> sea,
    you coud mask out sea points in mycube using
       mycube = common.add_mask(mycube, mask_cube, comparator="<",
           threshold=0.5)
    (i.e. all points with mask_cube < 0.5 would be masked out)


    Note that the mask is in addition to any existing masked values,
    but the mask is added to the cube if none is present to start with.
    """
    # Parse the comparator into a function:
    if type(comparator) is str:
        import operator
        comparators = {"==": operator.eq,
                       "=": operator.eq,
                       ">": operator.gt,
                       ">=": operator.ge,
                       "<": operator.lt,
                       "<=": operator.le}
        try:
            comparator_function = comparators[comparator]
        except KeyError:
            raise UserWarning("Comparator string '" + comparator +
                              "' not recognised:\n" +
                              "Try one of '==','=', '>','>=', '<','<='.\n" +
                              "Failing in common_analysis.py:add_mask()")
    else:
        comparator_function = comparator

    # Create the boolean array that will be the new mask:
    themask = comparator_function(maskcube.data, threshold)

    # Copy the cube to add a mask to it:
    # (so the original cube isn't modified)
    datacube_new = datacube.copy()

    # Add the mask to the data cube:
    try:
        _ = datacube.data.mask.shape
        # If that worked, then the cube already has a mask,
        # and we need to just mask some more values:
        datacube_new.data.mask = datacube.data.mask | themask
    except AttributeError:
        # If there was no mask, we need to make a new one using themask array.
        datacube_new.data = np.ma.masked_array(datacube.data, themask)

    # Done!
    return datacube_new


def rectify_units(acube, vartag=None, target_unit=None):
    """
    Correct the units of some standard cases in an automatic fashion.

    target_unit is something that can be used by iris.Cube.convert_units(),
    e.g. a string, or a cf_units.Unit object.
    (a good idea might be to provide the preferred_unit component
    of a  ukcp_standard_plots.standards_class.StandardMap object)

    Otherwise, we use vartag (a string, e.g. "tas")
    to determine what variable we've got,
    and attempt to convert the cube to an assumed preferred unit.

    This will probably be modified in future if it becomes clear that
    the vartag--unit mapping is generally useful.
    """
    PREFERRED_UNITS = dict(tas=cf_units.Unit("Celsius"),
                           ts=cf_units.Unit("Celsius"),
                           pr=cf_units.Unit("mm/day"),
                           # soil moisture content in a layer 8223
                           mrso=cf_units.Unit("1"),
                           windspeed=cf_units.Unit("m/s"))

    # HANDLED_VARTAGS = PREFERRED_UNITS.keys()

    if target_unit is None:
        if vartag is None:
            # figure out what variable we have...
            vartag = _guess_vartag(acube)

        if vartag not in PREFERRED_UNITS.keys():
            log.warn("vartag {} found, but target_unit not provided;".format(
                vartag))
            log.warn("vartag not in list of known preferred units {}".format(
                PREFERRED_UNITS.keys()))
            raise UserWarning("Unable to convert units.")

        # Now we can figure out the preferred unit of this variable:
        target_unit = PREFERRED_UNITS[vartag]
    else:
        # We just need to make sure the target_unit is a Unit object:
        if type(target_unit) is str:
            target_unit = cf_units.Unit(target_unit)

    # Now we know the variable and therefore the target unit,
    # we can apply it.

    # Handle some special cases first:
    WATER_DENSITY = iris.coords.AuxCoord(1000.0, units=cf_units.Unit('kg m-3'))
    ONE_METRE = iris.coords.AuxCoord(1.0,   units=cf_units.Unit('m'))
    # (1m = 1 m³/m² for convenience)

    if (acube.units.is_convertible("kg m^-2 s^-1") and
            target_unit.is_convertible("m/s")):
        # WARNING WE'RE ASSUMING IT'S **PRECIPITATION** MASS FLUX
        #         RATHER THAN SOME OTHER kg/m²/s THING - THIS COULD BE RISKY

        # Short-circuit a special, common case:
        # (NOT ACTUALLY SURE THIS IS FASTER THAN DOING IT EXPLICITLY...)
        if acube.units == cf_units.Unit("kg m^-2 s^-1"):
            log.debug("Precip mass flux in kg/m²/s  with target compatible "
                      "with m/s detected;")
            log.debug("Doing short-cut unit conversion")
            # precip mass flux data in kg/m²/s is numerically equivalent
            # to precip volume flux data in mm/s.
            # So just override the current units
            # without explicitly dividing by water density.
            acube.units = cf_units.Unit("mm/s")
            # The final call to convert_units will change it from mm/s to
            # mm/day (or whatever)

        else:
            log.debug("Precip mass flux detected; dividing by water density "
                      "to get volume flux")
            # This can take a while to explcitly do the division,
            # as Biggus will be forced to load the whole cube into memory.
            acube = acube / WATER_DENSITY

        # Tidy up:
        acube.standard_name = "lwe_precipitation_rate"
        acube.long_name = "precipitation rate"

    if (acube.units.is_convertible("kg m^-2") and
            target_unit.is_convertible("1")):
        # WARNING WE'RE ASSUMING IT'S **SOIL MOISTURE** CONTENT
        #         RATHER THAN SOME OTHER kg/m² THING - THIS COULD BE RISKY
        log.debug("Soil moisture content detected, dividing by water areal "
                  "mass density")
        # soil moisture is given as an areal mass density, kg/m²
        # We need it as a fraction of the areal mass density of water
        # [mass per unit area]
        # (Mass density of Water ρw = 1000 kg/m³, so if we have a m³ of water,
        #  then its mass per unit area is ρw × (1 m³/m²) = 1000×1 kg/m²)
        acube = (acube / ONE_METRE) / WATER_DENSITY
        # (note we can only multiply/divide Cubes and Coords, NOT Coords and
        # Coords!
        # Tidy up:
        acube.standard_name = "volume_fraction_of_water_in_soil"
        # See http://cfconventions.org/Data/cf-standard-names/43/build/
        #    cf-standard-name-table.html
        # I think this is right, but I'm a bit unsure.

        # It's a bit clunky though, so specify a long_name too:
        acube.long_name = "soil_moisture_fraction"
        # (RM originally used 'soil_moisture_dimless')

    # Hopefully all other cases will "just work":
    acube.convert_units(target_unit)

    return acube


def _guess_vartag(acube):
    """
    Try to guess what variable tag is appropriate for a cube
    (e.g. "tas" for near-surface air temperature)

    If the data is set up correctly then it should never be used!
    It has a place currently because this code uses a temporary
    variable ID system (vartags),
    whereas in future we'll use the variable IDs from the CEDA
    controlled vocabs, which will correspond to the netCDF/cube var_name.
    """
    VARTAG_CLUES = dict(tas="temperature", ts="temperature",
                        pr="precip",
                        windspeed="wind")
    # Go through the keys in VARTAG_CLUES,
    # testing the cube name for those clues...
    thevartag = None
    for vartag, aclue in VARTAG_CLUES.items():
        if aclue in acube.standard_name:
            thevartag = vartag
            break

    if thevartag is None:
        msg = ("Variable tag cannot be identified using standard name "
               "'{name}', from the list of {tags}".format(
                   name=acube.standard_name, tags=VARTAG_CLUES.keys()))
        log.warn(msg)

    return thevartag
