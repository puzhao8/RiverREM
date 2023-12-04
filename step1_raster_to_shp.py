#%%
import numpy as np
import rasterio
from rasterio.mask import mask

# get ROI from DEM or REM tiles
with rasterio.open("./outputs/Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif") as ref_raster:
    ref_bounds = ref_raster.bounds

clip_geom = [{'type': 'Polygon', 'coordinates': [[(ref_bounds.left, ref_bounds.bottom), (ref_bounds.right, ref_bounds.bottom), (ref_bounds.right, ref_bounds.top), (ref_bounds.left, ref_bounds.top), (ref_bounds.left, ref_bounds.bottom)]]}]
print(clip_geom)

#%%

# Open the raster to be clipped: Surface Water Mask Layer for Colombia
with rasterio.open("./inputs/colombia_wetland_potential_WGS84.tif") as raster:
    out_image, out_transform = mask(raster, clip_geom, crop=True)
    out_meta = raster.meta.copy()

#%%

# read clipped raster, and conduct processing to extract open water mask (1: open water)
with rasterio.open('./inputs/colombia_wetland_potential_wgs84_clipped.tif', "r") as raster:
    band = raster.read(1)
    band = (band == 1).astype(np.uint8) 
    out_meta = raster.meta.copy()

# Modify the metadata
out_meta.update({"driver": "GTiff",
                 "height": raster.shape[0],
                 "width": raster.shape[1],
                 "transform": raster.transform})


# Write the modified raster to a new file
with rasterio.open('./inputs/colombia_wetland_potential_river.tif', "w", **out_meta) as dest:
    dest.write(band, 1)


# #%%
# with rasterio.open(
#     './inputs/new.tif',
#     'w',
#     driver='GTiff',
#     height=Z.shape[0],
#     width=Z.shape[1],
#     count=1,
#     dtype=Z.dtype,
#     crs='+proj=latlong',
#     transform=Z.transform,
# ) as dst:
#     # processing here


#     # save
#     dst.write(Z, 1)

#%% River to Graph

from rivgraph.classes import delta
import matplotlib.pyplot as plt

# Define the path to the georeferenced binary image.
mask_path = "./inputs/colombia_wetland_potential_river.tif"

# Results will be saved with this name
name = 'Colombia_N02_00_W072_00' 

# Where do you want to store the results? This folder will be created if it doesn't exist.
results_folder = './inputs/Colombia/'

# Boot up the delta class! We set verbose=True to see progress of processing.
colville = delta(name, mask_path, results_folder=results_folder, verbose=True) 

# The mask has been re-binarized and stored as an attribute of colville:
plt.imshow(colville.Imask)

#%%
# Simply use the skeletonize() method.
colville.skeletonize()

# After running, colville has a new attribute: Iskel. Let's take a look.
plt.imshow(colville.Iskel)

#%%
# We use the write_geotiff() method with the "skeleton" option.
colville.to_geotiff('skeleton')

#%%

# Simply use the compute_network() method.
colville.compute_network()

# Now we can see that the "links" and "nodes" dictionaries have been added as colville attributes:
links = colville.links
nodes = colville.nodes
print('links: {}'.format(links.keys()))
print('nodes: {}'.format(nodes.keys()))

colville.plot('network')


#%%

# * links.shp is the desired file
colville.to_geovectors('network', ftype='shp') # ftype can be either 'shp' or 'json'

# Let's see where the network geovector files were written:
print(colville.paths['links'])
print(colville.paths['nodes'])



# #%%

# # Note that if the shoreline and inlet nodes shapefiles are in the path_results path, we do not need to specify their locations:
# # colville.prune_network()

# # However, our files are one directory up, so we need to point to them.
# colville.prune_network(path_shoreline='data/Colville_delta/Colville_shoreline.shp', path_inletnodes='data/Colville_delta/Colville_inlet_nodes.shp')

# # Now that we've pruned, we should re-export the network:
# colville.to_geovectors()
# # Note that this time we didn't specify the arguments; by default 'network' will be exported as type 'json'.
