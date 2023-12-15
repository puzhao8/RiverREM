
#%% 

import rasterio
import numpy as np
import matplotlib.pyplot as plt

url = f"C:\DHI\RiverREM\outputs\FreeFlowRiverV1/add_endpnts\Copernicus_DSM_COG_10_N04_00_W078_00_centerline.tif"
# Open the raster file
with rasterio.open(url) as src:
    raster = src.read(1)  # Read the first band
    affine = src.transform

#%%

# Get coordinates and values
coordinates = np.array([(j, i) for j in range(raster.shape[1]) for i in range(raster.shape[0])])
values = raster.flatten()


# Filter out nodata values if necessary
nodata = src.nodatavals[0]
if nodata is not None:
    mask = values != nodata
    coordinates = coordinates[mask]
    values = values[mask]

mask = (values == 1)
coordinates = coordinates[mask]
values = values[mask]

#%%

from scipy.spatial.distance import cdist

def idw_interpolation(x, y, z, xi, yi, power=2):
    # Create a meshgrid for the output raster
    xi, yi = np.meshgrid(xi, yi)

    # Calculate distances between input points and output points
    distances = cdist(np.column_stack((x, y)), np.column_stack((xi.flatten(), yi.flatten())))

    # Inverse distance weighting
    weights = 1.0 / distances**power
    weights[distances == 0] = 0
    interpolated_values = np.sum(weights * z[:, None], axis=0) / np.sum(weights, axis=0)

    return interpolated_values.reshape(xi.shape)


x_coords, y_coords = coordinates[:, 0], coordinates[:, 1]
x_range = np.linspace(x_coords.min(), x_coords.max(), raster.shape[1])
y_range = np.linspace(y_coords.min(), y_coords.max(), raster.shape[0])

# Interpolate using IDW
interpolated_raster = idw_interpolation(x_coords, y_coords, values, x_range, y_range)


#%%

# var vis_viswth = {
#   bands: ['viswth'],
#   min: 1,
#   max: 3000,
#   palette: ['cae9ff','6cadff','2063ff','b60000'],
# };

# Map.addLayer(dataset.mask(dataset.select('viswth').gte(1)), vis_viswth, 'River width');