import zarr
import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def read_and_store_chunk(index, src_arr, dest_arr):
    slices = tuple(
        slice(d * c, min((d + 1) * c, src_arr.shape[i]))
        for i, (d, c) in enumerate(zip(index, src_arr.chunks))
    )
    chunk = src_arr[slices]
    dest_arr[slices] = chunk
    
def copy_zarr_file(s3_path : str, dest_zarr :str, threads :int, fs):

    root_s3 = zarr.open(fs.get_mapper(s3_path), mode='r')
    zarr_store = zarr.NestedDirectoryStore(dest_zarr)
    root = zarr.group(store=zarr_store)

    for arr in root_s3.arrays(recurse=True):
        src_s3_arr = arr[1]
        parent_group = root.require_group(os.path.split(src_s3_arr.path)[0])
        print(os.path.split(src_s3_arr.path)[0])

        parent_group.attrs.update(root_s3[os.path.split(src_s3_arr.path)[0]].attrs)
        
        dest_arr = parent_group.require_dataset(
            name=src_s3_arr.name,
            shape=src_s3_arr.shape,
            chunks=src_s3_arr.chunks,
            dtype=src_s3_arr.dtype,
            overwrite=True
        )

        grid = [range((dim + c - 1) // c) for dim, c in zip(src_s3_arr.shape, src_s3_arr.chunks)]
        chunk_indices = [(i, j, k) for i in grid[0] for j in grid[1] for k in grid[2]]

        with ThreadPoolExecutor(max_workers=threads) as pool:
            args = zip(chunk_indices, [src_s3_arr] * len(chunk_indices), [dest_arr] * len(chunk_indices))
            results = list(tqdm(pool.map(lambda p: read_and_store_chunk(*p), args), total=len(chunk_indices)))
            
        