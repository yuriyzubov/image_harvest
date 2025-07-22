import requests
import s3fs
import zarr
from tifffile import TiffFile


def get_remote_tiff_metadata(url : str, range_end : int):
    """Returns tiff metadata stored at the beginning of the file.
        use it to preliminary inspect the metadata, before downloading the whole data

    Args:
        url (str): Path to tiff file
        range_end (int): Range in bytes to read from the beginning of the file. 

    Returns:
        dict: returns dict (tag_name : tag_value)
    """
    
    import io
    headers = {'Range': f'bytes=0-{range_end}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Try to open the partial file
    with TiffFile(io.BytesIO(response.content)) as tif:
        page = tif.pages[0]
        return {tag.name: tag.value for tag in page.tags.values()}
    

def remote_xml_metadata(url : str):
    """Fetch remote xml metadata and parse it to a dictionary 

    Args:
        url (str): Path to remote xml file

    Returns:
        dict: nested dictionary
    """
    import xmltodict

    response = requests.get(url)
    response.raise_for_status()
    return xmltodict.parse(response.content)


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
        path_to_dataset (_type_): path to dataset (on s3, gcs, or local)
        driver (_type_): neuroglancer_precomputed, zarr2, zarr3, n5
    """
    import tensorstore as ts
    
    spec = path_to_tensorstore_spec(path_to_dataset, driver)
    store = await ts.open(spec, open=True, read=True)
    return store.spec().to_json()

def get_zarr_s3_attrs(s3_path):
    fs = s3fs.S3FileSystem(anon=True)
    store = s3fs.S3Map(root=s3_path.replace('s3://', ''), s3=fs, check=False)
    zarr_obj = zarr.open(store, mode='r')
    if isinstance(zarr_obj, zarr.Group):
        return dict(zarr_obj.attrs)
    else:
        return {
    "shape": zarr_obj.shape,
    "chunks": zarr_obj.chunks,
    "dtype": str(zarr_obj.dtype),
    "order": zarr_obj.order,
    "fill_value": zarr_obj.fill_value,
    "compressor": zarr_obj.compressor.get_config() if zarr_obj.compressor else None,
    "filters": [f.get_config() for f in zarr_obj.filters] if zarr_obj.filters else None
    }

        





    
