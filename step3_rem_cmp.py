

#%%
import matplotlib.pyplot as plt
import numpy as np
import rasterio

osm_singleRiver = ".\outputs\Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif"
url_osm = ".\outputs\OSM\Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif"
url_swl = ".\outputs\SWORD\Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif"
url_ffr = ".\outputs\FreeFlowRiverV1\Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif"


with rasterio.open(url_osm, "r") as raster:
    rem_osm = raster.read(1)

with rasterio.open(url_ffr, "r") as raster:
    rem_ffr = raster.read(1)

with rasterio.open(url_swl, "r") as raster:
    rem_swl = raster.read(1)

#%%
# import matplotlib.pyplot as plt

# num_of_bins = 100
# fig, ax = plt.subplots()
# ax.hist(rem_singleRiver, bins=num_of_bins, edgecolor='black', alpha=0.3)
# ax.hist(rem_osm, bins=num_of_bins, edgecolor='black', alpha=0.3)
# plt.show()

# REM = DEM - RiverDEM_interpolated

#%% visualize DEM map using custorm colormaps
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Define the colors, including one for 0 value
colors = ["purple", "white", "green"]  # The first color is for 0

# Create a new colormap
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

rem = rem_swl
print(rem.min(), rem.max())
plt.imshow(rem, cmap=cmap, vmin=-20, vmax=20)
plt.colorbar()  # Optional, to show the color scale

#%% visualize REM difference Map using custorm colormaps
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

rem1, rem2 = rem_ffr, rem_osm

# Define the colors, including one for 0 value
colors = ["blue", "white", "red"]  # The first color is for 0

# Create a new colormap
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

diff = rem1 - rem2
print(diff.min(), diff.max())

plt.imshow(diff, cmap=cmap, vmin=-20, vmax=20)
plt.colorbar()  # Optional, to show the color scale

