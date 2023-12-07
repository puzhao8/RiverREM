
#%%
import os, time
import pystac
import pystac_client
import planetary_computer
from pathlib import Path

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
# tile_name = "Copernicus_DSM_COG_10_N02_00_W072_00"

# loop over each tile, calculate REM, and save 
for tile_name in [
                    # "Copernicus_DSM_COG_10_N10_00_W075_00",
                    # "Copernicus_DSM_COG_10_N10_00_W074_00",
                    # "Copernicus_DSM_COG_10_N05_00_W075_00",
                    # "Copernicus_DSM_COG_10_N03_00_W078_00",
                    # "Copernicus_DSM_COG_10_N03_00_W077_00",
                    # "Copernicus_DSM_COG_10_N06_00_W076_00",
                    # "Copernicus_DSM_COG_10_N05_00_W078_00",  # error happened here
                    
                    "Copernicus_DSM_COG_10_N07_00_W073_00",
                    "Copernicus_DSM_COG_10_N09_00_W076_00",
                    "Copernicus_DSM_COG_10_N09_00_W075_00",
                    "Copernicus_DSM_COG_10_N08_00_W077_00",
                    "Copernicus_DSM_COG_10_N08_00_W075_00",

                ]: # ids:
    print()
    print(tile_name)

    item_url = f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/cop-dem-glo-30/items/{tile_name}_DEM"

    # Load the individual item metadata and sign the assets
    item = pystac.Item.from_file(item_url)
    signed_item = planetary_computer.sign(item)

    # Open one of the data assets 
    asset_href = signed_item.assets["data"].href
    # ds = rioxarray.open_rasterio(asset_href)
    # ds, ds.values

    # derive REM from DEM, and save it to "./outputs/" folder
    # os.mkdir("./outputs")

    SHP_KEY = "FreeFlowRiverV1" # choose centerline source
    SHP_DICT = {
        "OSM": None, # default: only use the longest river.
        'FreeFlowRiverV1': "C:/DHI/River_Networks/FreeFlowRiverV1/FreeFlowRiverV1_RIV_ORD_lte5.shp", # Free Flow River V1
        'HydroRiverV1': "C:/DHI/River_Networks/HydroRiverV1\HydroRivers_v10_sa/HydroRivers_v10_sa.shp", # HydroRiverV1
        "SWORD": "C:/DHI/River_Networks/SWORD_v16_shp/shp/SA/sa_sword_reaches_hb61_v16.shp", # SWORD,
        'RivGraph': "./inputs/Colombia/Colombia_N02_00_W072_00_links.shp", # Surface Water extracted SHP
    }

    if 'OSM' in SHP_KEY: centerline_shp = None
    else: centerline_shp = SHP_DICT[SHP_KEY]
    out_dir = f'./outputs/{SHP_KEY}'

    # make directory
    Path(out_dir).mkdir(exist_ok=True, parents=True)

    # start to make REM
    start_time = time.perf_counter()

    rem_maker = REMMaker(dem=asset_href, tile_name=tile_name, centerline_shp=centerline_shp, out_dir=out_dir)
    rem_maker.make_rem_viz(cmap='Blues', z=8)

    end_time = time.perf_counter()
    print("Elapsed time: ", end_time - start_time)


# TODO
# upload the derived REM tiles as GEE asset of ImageCollection, follow upload_to_gee.py

# %%
