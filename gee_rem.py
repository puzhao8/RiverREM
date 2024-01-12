#%% 

# RiverREM in GEE: https://code.earthengine.google.com/797ba7d668ea39c18a6b57b48b6c0b70
# REM Comparison in GEE: https://code.earthengine.google.com/74904fad6e0ff695d46dc9f25656976e
# River Network Comparion: https://code.earthengine.google.com/8bcd31f882bf5fa163094cbe8d8ff683
# Understand IDW: https://code.earthengine.google.com/ed68f36c3d2f5f205e7e1a36f702fd42
# Testbed in GEE: https://code.earthengine.google.com/7de12fb47debdc1fb64c25b9ff95a995

import ee
# ee.Authenticate()
ee.Initialize()

def detrend_DEM_to_REM(aoi, riverNetwork='HydroRiverV1', bufferSize=1e4, idwRange=5e4):
    demImgCol = ee.ImageCollection("COPERNICUS/DEM/GLO30")
    aoi_buffered = aoi.buffer(idwRange).bounds()

    if 'HydroRiverV1' == riverNetwork:
        # // filter stream network to aoi
        river_networks = ee.FeatureCollection("WWF/HydroSHEDS/v1/FreeFlowingRivers")
        aoi_network = (river_networks.filterBounds(aoi_buffered)
                            .filter(ee.Filter.lte("RIV_ORD", 6))
                )

        # // convert the vertices of the stream network lines to 
        # // a FeatureCollection of points
        # // these will be used to sample elevation values along
        # // the stream network and interpolate 
        def create_points(pt): return  ee.Feature(ee.Geometry.Point(pt))
        def line_to_points(line): return ee.List(line).map(create_points)
        network_nodes = ee.FeatureCollection(aoi_network.geometry().coordinates().map(line_to_points).flatten())

    # MERIT-Based Sampling
    if 'MERIT_centerline' == riverNetwork:
        MERIT = ee.Image('MERIT/Hydro/v1_0_1')
        riverMask =  MERIT.select('wth').updateMask(MERIT.select('wth').gt(0)).int().rename('mask') # MERIT Centerline
        network_nodes = riverMask.stratifiedSample(
            numPoints = 1e4,
            classBand = 'mask',
            region = aoi_buffered,
            scale = 100,
            geometries = True,
        ) #// Replace NUMBER_OF_POINTS with the number of points you want

        # network_nodes = network_nodes.merge(merit_nodes)

    if 'JRC_GSW' == riverNetwork:
        GSW = ee.Image('JRC/GSW1_4/GlobalSurfaceWater')
        riverMask =  GSW.select('max_extent').mask(GSW.select('max_extent')).rename('mask') #// MERIT Centerline
        network_nodes = riverMask.stratifiedSample(
            numPoints = 2e4,
            classBand = 'mask',
            region = aoi_buffered,
            scale = 100,
            geometries = True,
        ) #// Replace NUMBER_OF_POINTS with the number of points you want
        
    # // combine mean and stdDev reducers to calculate regional stats
    # // need this for the IDW interpolation
    reducers = ee.Reducer.mean().combine(ee.Reducer.stdDev(), None, True)

    # // calculate AOI mean and stdDev
    demImgCol_ = demImgCol.filterBounds(aoi.buffer(bufferSize).bounds())
    aoi_9x = ee.FeatureCollection(demImgCol_.toList(demImgCol_.size()).map(lambda x: ee.Feature(ee.Image(x).geometry()))).union().geometry()
    
    demImgCol_ = demImgCol.filterBounds(aoi_9x)
    aoi_25x = ee.FeatureCollection(demImgCol_.toList(demImgCol_.size()).map(lambda x: ee.Feature(ee.Image(x).geometry()))).union().geometry()

    dem = demImgCol_.mosaic().select('DEM').rename("elevation")
    aoi_stats = dem.reduceRegion(
        reducer = reducers,
        geometry = aoi_25x,
        scale = 30,
        bestEffort = True,
    )

    # // sample the elevation values from dem at every vertex
    # // from the stream network
    node_elv = dem.sampleRegions(
        collection= network_nodes,
        scale= 30,
        geometries= True
    )

    # // interpolate the elevation values from the stream
    # // this will create an image 
    elv_interp = node_elv.inverseDistance(
        range = idwRange, # 5000 for max 5km range, and 5e4 for max 50km range
        propertyName = "elevation", 
        mean =  aoi_stats.get("elevation_mean"), 
        stdDev =  aoi_stats.get("elevation_stdDev"),
        gamma = 0.75,
        reducer = ee.Reducer.mean()
    )

    # // calculate the relative elevation from the 
    # // interpolated stream values
    rem = dem.subtract(elv_interp)

    return rem

def detrend_dem_by_subtracting_local_minimum(aoi, radius=200):
    # // calculate AOI mean and stdDev
    dem = demImgCol.filterBounds(aoi.buffer(1000).bounds()).mosaic().select('DEM').rename("elevation")

    localMin = dem.focalMin(radius=radius, kernelType='circle', units='pixels') # 200 * 30 = 6000
    rem_localMin = dem.subtract(localMin)
    return rem_localMin



#%% main scripts


""" Configuration """
print('-----------------------------------------------------------------------')
riverNetwork = 'JRC_GSW' # HydroRiverV1, MERIT_centerline, JRC_GSW, 
dstImgCol = f"projects/global-wetland-watch/assets/features/REM_{riverNetwork}_V1"

print(riverNetwork)
print(dstImgCol)
print('------------------------------------------------------------------------')


""" Dataset """
# Country Boundaries
FAO = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0")
Colombia = FAO.filter(ee.Filter.eq("ADM0_NAME", "Colombia"))

# DEM
demImgCol = ee.ImageCollection("COPERNICUS/DEM/GLO30")
dem_tiles = demImgCol.filterBounds(Colombia)
tile_list = sorted(dem_tiles.aggregate_array("system:index").getInfo())
print(f"tile size: {len(tile_list)}")

# tile_name = tile_list[0]
tile_list = [f"N0{lat}_00_W0{lon}_00" for lat in [4,5] for lon in [73, 74]]


import os, subprocess
asset_list = subprocess.getstatusoutput(f"earthengine ls {dstImgCol}")[-1].split('\n')
asset_ids = [os.path.split(asset_id)[-1] for asset_id in asset_list]


# # remove from list if a tile REM has already been uploaded. 
if False:
    tile_list = [tile_name for tile_name in tile_list if tile_name not in asset_ids]

print(f"len tile: {len(tile_list)}")

# Tile-Wise REM Generation
for idx, tile_name in enumerate(tile_list):
    assetId = f"{dstImgCol}/{tile_name}"
    print(f"idx: {idx}, asset_id: {assetId}")

    if tile_name not in asset_ids:

        tile = (ee.ImageCollection("COPERNICUS/DEM/GLO30")
                    .filter(ee.Filter.eq("system:index", tile_name))
                    .first())
        
        aoi = tile.geometry()

        rem = detrend_DEM_to_REM(aoi=aoi, riverNetwork=riverNetwork)
        # rem = detrend_dem_by_subtracting_local_minimum(aoi=aoi, radius=200)

        ee.batch.Export.image.toAsset(
            image = rem, 
            assetId = assetId,
            description = tile_name,
            region = aoi,
            crs = "EPSG:4326",
            scale = 30,
        ).start()

# %%