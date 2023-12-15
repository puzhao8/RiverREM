

#%%
import matplotlib.pyplot as plt
import numpy as np
import rasterio

url_dict = {
    # 'OSM_singleRiver': ".\outputs\Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif",
    'OSM': ".\outputs\OSM\Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif",
    'SWL': ".\outputs\SWORD\Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif",
    'FFR': ".\outputs\FreeFlowRiverV1\Copernicus_DSM_COG_10_N02_00_W072_00_REM.tif",

    'TEST1': ".\outputs\FreeFlowRiverV1\HydroRiver_OSM\Copernicus_DSM_COG_10_N04_00_W078_00_REM.tif",
    "TEST2": ".\outputs\OSM\Copernicus_DSM_COG_10_N04_00_W078_00_REM.tif"
}


rem_dict = {}
for key in url_dict.keys():
    print(key)
    with rasterio.open(url_dict[key], "r") as raster:
        rem_dict[key] = raster.read(1)


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
colors = ["purple", "white", "#0d50a9"]  # The first color is for 0

# Create a new colormap
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

rem_key = 'TEST1'
max_value = 20

rem = rem_dict[rem_key]
print(rem.min(), rem.max())
plt.imshow(rem, cmap=cmap, vmin=-max_value, vmax=max_value)
plt.colorbar()  # Optional, to show the color scale
plt.savefig(url_dict[rem_key].replace('_REM.tif', '_REM_river.png'))

#%% visualize REM difference Map using custorm colormaps
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

rem1, rem2 = rem_dict['CN1'], rem_dict['CN2']

# Define the colors, including one for 0 value
colors = ["blue", "white", "red"]  # The first color is for 0

# Create a new colormap
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

diff = rem1 - rem2
print(diff.min(), diff.max())

plt.imshow(diff, cmap=cmap, vmin=-20, vmax=20)
plt.colorbar()  # Optional, to show the color scale

