import zarr
from collections import defaultdict

def get_zarr_attrs(path_to_zarr):
    """Get attributes for zarr group or array

    Args:
        path_to_zarr (str): path to zarr group or array

    Returns:
        dict: attrs of the object
    """
    zarr_obj = zarr.open(path_to_zarr, mode='r')
    if isinstance(zarr_obj, zarr.Group):
        return dict(zarr_obj.attrs)
    else:
        return {
    "shape": zarr_obj.shape,
    "chunks": zarr_obj.chunks,
    "dtype": str(zarr_obj.dtype),
    "order": zarr_obj.order,
    "fill_value": int(zarr_obj.fill_value),
    "compressor": zarr_obj.compressor.get_config() if zarr_obj.compressor else None,
    "filters": [f.get_config() for f in zarr_obj.filters] if zarr_obj.filters else None
    }
        
def get_zarr_metadata(path_to_group):
    group_attrs = get_zarr_attrs(path_to_group)
    array_attrs = get_zarr_attrs('/'.join([path_to_group, 's0']))
    metadata = defaultdict(dict)
    metadata['raw_metadata'] = {'parent_group' : group_attrs, 'array' : array_attrs}
    metadata['shape'] = array_attrs['shape']
    axes =  group_attrs['multiscales'][0]['axes'] 
    metadata['axes'] = [a['name'] for a in axes]
    metadata['unit'] = [a['unit'] for a in axes]
    
    scale_metadata = group_attrs['multiscales'][0]['datasets'][0]
    metadata['voxel_size'] = scale_metadata['coordinateTransformations'][0]['scale']
    metadata['offset'] = scale_metadata['coordinateTransformations'][1]['translation']
    metadata['dtype'] = array_attrs['dtype']
    
    return(metadata)
        

    