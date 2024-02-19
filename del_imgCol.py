
import os
import time 
import datetime as dt
from datetime import datetime, timedelta
import subprocess
import ee 
ee.Initialize()

feature = "projects/global-wetland-watch/assets/features"
for imgCol in ['REM_HydroMERIT', 'REM_HydroRiverV1', 'REM_MERIT_centerline', ]:

    response = subprocess.getstatusoutput(f"earthengine ls {feature}/{imgCol}")
    asset_list = response[1].replace("projects/earthengine-legacy/assets/", "").split("\n")

    if len(asset_list) > 0:
        for asset_id in asset_list:
                    
            filename = os.path.split(asset_id)[-1]
            print(f"{filename}: {asset_id}")

            os.system(f"earthengine rm {asset_id}")