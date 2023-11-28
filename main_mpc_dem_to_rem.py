
#%%

import pystac
import pystac_client
import planetary_computer

import rioxarray
import xarray as xr
from prettyprinter import pprint

from riverrem.REMMaker import REMMaker

# # create a Region of Interest (roi) in https://geojson.io/ or other platform, copy and paster coordinates
# roi = dict(type = "Polygon", coordinates = [...])

# Geometry of Colombia Country
minlon, minlat, maxlon, maxlat = -79.70677443301699, -3.635295809423141, -67.29293287446059, 12.831456778731706
roi = dict(type = "Polygon", coordinates = [[[minlon, minlat], [minlon, maxlat], [maxlon, maxlat], [maxlon, minlat], [minlon, minlat]]])

# Planetary computer's STAC URL
URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
catalog = pystac_client.Client.open(URL)

# query by geometry
items = catalog.search(
    intersects=roi,
    collections=["cop-dem-glo-30"]
    ).item_collection()

# get the list of queried tiles 
ids = [item['id'][:-4] for item in items.to_dict()['features']]
print(f"The total number of dem tiles: {len(ids)}")
pprint(ids)

#%%
tile_name = "Copernicus_DSM_COG_10_N02_00_W072_00"

# loop over each tile, calculate REM, and save 
for tile_name in [tile_name]: # ids:
    print()
    print(tile_name)

    item_url = f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/cop-dem-glo-30/items/{tile_name}_DEM"

    # Load the individual item metadata and sign the assets
    item = pystac.Item.from_file(item_url)
    signed_item = planetary_computer.sign(item)

    # Open one of the data assets 
    asset_href = signed_item.assets["data"].href
    # ds = rioxarray.open_rasterio(asset_href)
    # ds
    # ds.values

    # derive REM from DEM, and save it to "./outputs/" folder
    rem_maker = REMMaker(dem=asset_href, tile_name=tile_name, out_dir='./outputs')
    rem_maker.make_rem_viz(cmap='Blues', z=8)


# TODO
# upload the derived REM tiles as GEE asset of ImageCollection, follow upload_to_gee.py

# %%
