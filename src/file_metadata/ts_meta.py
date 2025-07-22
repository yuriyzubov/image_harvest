import os
from collections import defaultdict
import asyncio

def path_to_tensorstore_spec(path : str,
                             driver : str = "neuroglancer_precomputed"):
    """Convert path to a dataset to a tensorstore spec

    Args:
        path (_type_): _description_
        driver (str, optional): _description_. Defaults to "neuroglancer_precomputed".

    Returns:
        _type_: _description_
    """
    from urllib.parse import urlparse
    parsed = urlparse(path)

    if path.startswith("gs://"):
        bucket, path = parsed.netloc, parsed.path.lstrip('/')
        kvstore = {"driver": "gcs", "bucket": bucket}
    elif path.startswith("s3://"):
        bucket, path = parsed.netloc, parsed.path.lstrip('/')
        kvstore = {"driver": "s3", "bucket": bucket}
    elif path.startswith("file://"):
        path = parsed.path
        kvstore = {"driver": "file", "path": path}
    else:
        # local path
        kvstore = {"driver": "file", "path": path}
        path = ""

    return {
        "driver": driver,
        "kvstore": kvstore,
        "path": path
    }

async def get_spec_ts(path_to_dataset : str,
                      driver : str):
    """Read neuroglancer metadata

    Args:
        path_to_dataset (str): path to dataset (on s3, gcs, or local)
        driver (str): neuroglancer_precomputed, zarr2, zarr3, n5
    """
    import tensorstore as ts
    
    spec = path_to_tensorstore_spec(path_to_dataset, driver)
    store = await ts.open(spec, open=True, read=True)
    return store.spec().to_json()

async def get_ts_metadata(ds_path, driver):
    ts_metadata = await get_spec_ts(ds_path, driver)
    metadata = defaultdict(dict)
    metadata['raw_metadata'] = ts_metadata
    
    scale = ts_metadata['scale_metadata']
    metadata['shape'] = scale['size']
    metadata['dtype'] = ts_metadata['dtype']
    metadata['voxel_size'] = scale['resolution']
    metadata['unit'] = ['nm']*len(scale['size'])
    metadata['channels'] = ts_metadata['multiscale_metadata']['num_channels']
    metadata['offset'] = scale['voxel_offset']
    metadata['axes'] = ['z', 'y', 'x']
    return dict(metadata)


    