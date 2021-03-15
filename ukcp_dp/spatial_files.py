from os import path

from ukcp_sf import get_data_dir


DATA_DIR = get_data_dir()

OVERLAY_ADMIN = path.join(
    DATA_DIR, "ukcp18-uk-land-region-hires", "ukcp18-uk-land-region-hires"
)
OVERLAY_ADMIN_SMALL = path.join(
    DATA_DIR, "ukcp18-uk-land-region-lowres", "ukcp18-uk-land-region-lowres"
)

OVERLAY_COASTLINE = path.join(
    DATA_DIR, "ukcp18-uk-marine-coastline-hires", "ukcp18-uk-marine-coastline-hires"
)
OVERLAY_COASTLINE_SMALL = path.join(
    DATA_DIR, "ukcp18-uk-marine-coastline-lowres", "ukcp18-uk-marine-coastline-lowres"
)

OVERLAY_COUNTRY = path.join(
    DATA_DIR, "ukcp18-uk-land-country-hires", "ukcp18-uk-land-country-hires"
)
OVERLAY_COUNTRY_SMALL = path.join(
    DATA_DIR, "ukcp18-uk-land-country-lowres", "ukcp18-uk-land-country-lowres"
)

OVERLAY_COUNTRY_AGGREGATED = path.join(
    DATA_DIR,
    "ukcp18-uk-land-country-aggregated-hires",
    "ukcp18-uk-land-country-aggregated-hires",
)
OVERLAY_COUNTRY_AGGREGATED_SMALL = path.join(
    DATA_DIR,
    "ukcp18-uk-land-country-aggregated-lowres",
    "ukcp18-uk-land-country-aggregated-lowres",
)

OVERLAY_RIVER = path.join(
    DATA_DIR, "ukcp18-uk-land-river-hires", "ukcp18-uk-land-river-hires"
)
OVERLAY_RIVER_SMALL = path.join(
    DATA_DIR, "ukcp18-uk-land-river-lowres", "ukcp18-uk-land-river-lowres"
)
