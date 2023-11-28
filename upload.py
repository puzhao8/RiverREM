# This code should be run in python environment, requires earthengine-api, gcoud etc.
# Please contact PUZH@dhigroup.com if you encounter any problem with this script.

import zipfile, os
from pathlib import Path


''' batch upload local geotiffs to GEE '''
# create an asset of ImageCollection in GEE, and bucket in GCP
eeImgCol = 'projects/dhi-wetlands-403206/assets/GWL_FCS30_2020' # asset folder in GEE asset
gs_dir = 'gs://gwl_fcs30_2020/GWL_FCS30_Extracted' # Google Storage Folder

# specify data folder
data_dir = Path(r"C:\Users\puzh\Downloads\GWL_FCS30") # local ZIP data folder
out_dir = Path(r"C:\Users\puzh\Downloads\GWL_FCS30\GWL_FCS30_Extracted") # extracted folder

# # extract zip into the same folder
if False: 
    for filename in os.listdir(data_dir):
        if filename.endswith('.zip'):
            print(filename)

            with zipfile.ZipFile(data_dir / filename,"r") as zip_ref:
                zip_ref.extractall(out_dir)
                
# upload all geotiff into Google Cloud Storage (GS)
os.system(f"gsutil -m cp -r {out_dir} {gs_dir}/")

def upload_image_into_gee_from_gs(filename):
    ''' upload image into GEE from Google Cloud Storge'''

    asset_id = f'{eeImgCol}/{filename[:-4]}'
    # print(f'{index}: {asset_id}')
    os.system(f"earthengine upload image --force --asset_id={asset_id} --pyramiding_policy=sample --nodata_value=0 {gs_dir}/{filename}")


# batch upload from GS
items = [file for file in os.listdir(Path(out_dir)) if file.endswith('.tif')]
for filename in items:
    upload_image_into_gee_from_gs(filename)