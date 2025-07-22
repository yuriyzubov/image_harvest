import asyncio
import tensorstore as ts
import numpy as np
import random
from tqdm.asyncio import tqdm_asyncio
import os

async def copy_crop(src_spec,
                    dest_path :str,
                    crop_coords : str,
                    crop_shape : list,
                    chunk_size : list):
    """Copying cropped data from a ng_precomputed dataset

    Args:
        src_spec (_type_): tensor store spec of the original dataset
        dest_path (str): local path to store 
        crop_coords (str) : ROI coords
        crop_shape (list): ROI shape
        chunk_size (list): output chunking
    """
    # Open source ng-precomputed dataset
    src = await ts.open(src_spec, open=True, read=True)
    spec_in = src.spec().to_json()
    scale_meta = spec_in.get('scale_metadata', {})

    resolution = [int(res) for res in scale_meta.get('resolution', None)]
    z0, y0, x0 = crop_coords
    crop = await src[z0:z0+crop_shape[0], y0:y0+crop_shape[1], x0:x0+crop_shape[2]].read()
    crop = np.asarray(crop)

    spec_dest = {
        'driver': spec_in.get('driver'),
        'kvstore': {'driver': 'file', 'path': dest_path},
        'scale_index': 0,
        'scale_metadata': {
            'key': '0',
            'encoding': spec_in['scale_metadata']['encoding'],
            'resolution': resolution,
            'voxel_offset': [z0, y0, x0],
            'size': crop.shape[:-1],
        },
        'dtype': str(crop.dtype),
        'create': True,
        'open': True
    }
    
    dst = await ts.open(spec_dest,
                        chunk_layout=ts.ChunkLayout(
                        grid_origin = [z0, y0, x0, 0],
                        chunk_shape =chunk_size.extend([1]) # x,y,z,c=1
                        ),
                        domain=ts.IndexDomain(
        inclusive_min=[z0, y0, x0, 0],
        shape=crop.shape))
    await dst.write(crop)
    print(f"Crop saved at: {dest_path}")
    print(f"Voxel offset (z, y, x): ({z0}, {y0}, {x0})")

