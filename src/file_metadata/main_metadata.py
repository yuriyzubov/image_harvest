from tiff_meta import get_metadata_tiff
from dm3_meta import get_metadata_dm3
from zarr_meta import get_zarr_metadata
from ts_meta import get_ts_metadata
import os
import asyncio
import json

if __name__ == "__main__":

    out_dir = os.path.abspath('./data')
    tiff_data = {'epfl' : "volumedata.tif", "idr" : "Figure_S3B_FIB-SEM_U2OS_20x20x20nm_xy.tif"}
    metadata = {k : get_metadata_tiff(os.path.join(out_dir, k, v)) for k,v in tiff_data.items()}

    path_to_dm3 = os.path.join(out_dir, 'empiar/11759/data/F57-8_test1_3VBSED_slice_0000.dm3')
    metadata['empiar'] =  get_metadata_dm3(path_to_dm3)
    metadata['openorganelle'] = get_zarr_metadata(os.path.join(out_dir, 'openorganelle/jrc_mus-nacc-2.zarr'))

    ds_path = os.path.join(out_dir, 'hemibrain/hemibrain_crop')
    driver = 'neuroglancer_precomputed'
    metadata['hemibrain'] = asyncio.run(get_ts_metadata(ds_path, driver))
    print(metadata)
    # store metadata in json file:
    with open("../../file_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

