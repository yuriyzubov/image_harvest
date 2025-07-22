from single_file import download_file_aria2c
from copy_zarr import copy_zarr_file
from directory import download_dir_aria2c, aria2c_list, list_files_recursive
from tensorstore_arr import copy_crop
import json
import os
import s3fs
import asyncio
from urllib.parse import urlparse


def download_data(download_links : dict, output_dir : str):
    for src in download_links:
        
        print("##################")    
        print(f"DOWNLOADING: {download_links[src]}")
        
        dest = os.path.join(os.path.abspath(output_dir), src)
        if src in 'idr':
            download_file_aria2c(download_links[src], dest, 4, 4)
        elif src in 'epfl':
            download_file_aria2c(download_links[src], dest, 16, 16)
        if src=='empiar':
            # index files in a remote directory
            file_list = list_files_recursive(download_links[src])
            list_of_files = 'aria2c_input.txt'
            aria2c_list(file_list, list_of_files, download_links[src], dest)
            download_dir_aria2c(list_of_files, 8, 8)
            os.remove(list_of_files)
        elif src=='openorganelle':
            fs = s3fs.S3FileSystem(anon=True)
            parsed = urlparse(download_links[src])
            s3_path = parsed.path.lstrip('/')
            dest_name = "jrc_mus-nacc-2.zarr"
            threads = 12 
    
            copy_zarr_file(s3_path, os.path.join(dest, dest_name), 12, fs)
        elif src=='hemibrain': 
            crop_shape = (200, 400, 600)
            chunk_size = [64, 64, 64]
            local_path = os.path.join(dest,"hemibrain_crop") # should be absoulute path to dataset
            crop_coords = [10000, 11000, 12000]

            # define spec
            parsed = urlparse(download_links[src])
            bucket, path = parsed.path.strip('/').split(os.sep, 1)
            src_spec = {
                "driver": "neuroglancer_precomputed",
                "kvstore": {"driver": "gcs", "bucket": bucket},
                "path": path
                }
            
            asyncio.run(copy_crop(src_spec, local_path, crop_coords, crop_shape, chunk_size))

if __name__ == "__main__":
    output_dir = '../../data/'    
    os.makedirs(output_dir, exist_ok=True)
    print(os.path.abspath(output_dir))

    # get datasets to download
    with open("../../web_metadata.json", "r") as f:
        metadata = json.load(f)    
    download_links = {k : v['download_links'][0] for k,v in metadata.items()}

    print("Datasets to download: ",  download_links)
    download_data(download_links, output_dir)
        