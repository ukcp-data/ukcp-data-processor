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

OVERLAY_COUNTRY_ENGLAND_AND_WALES = path.join(
    DATA_DIR,
    "ukcp18-uk-land-country-england_and_wales-hires",
    "ukcp18-uk-land-country-england_and_wales-hires",
)
OVERLAY_COUNTRY_ENGLAND_AND_WALES_SMALL = path.join(
    DATA_DIR,
    "ukcp18-uk-land-country-england_and_wales-lowres",
    "ukcp18-uk-land-country-england_and_wales-lowres",
)

OVERLAY_COUNTRY_UNITED_KINGDOM = path.join(
    DATA_DIR,
    "ukcp18-uk-land-country-united_kingdom-hires",
    "ukcp18-uk-land-country-united_kingdom-hires",
)
OVERLAY_COUNTRY_UNITED_KINGDOM_SMALL = path.join(
    DATA_DIR,
    "ukcp18-uk-land-country-united_kingdom-lowres",
    "ukcp18-uk-land-country-united_kingdom-lowres",
)

OVERLAY_RIVER = path.join(
    DATA_DIR, "ukcp18-uk-land-river-hires", "ukcp18-uk-land-river-hires"
)
OVERLAY_RIVER_SMALL = path.join(
    DATA_DIR, "ukcp18-uk-land-river-lowres", "ukcp18-uk-land-river-lowres"
)
