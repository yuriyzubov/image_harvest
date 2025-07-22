import tifffile
from collections import defaultdict
def get_metadata_tiff(path_to_image):
    """Returns tiff metadata schema {raw_metadata, imagej_metadata, ome_metadata, shape, dtype, channel, voxel_size, unit}

    Args:
        path_to_image (str): path to image

    Returns:
        dict: tiff metadata
    """
    # open the first page to access metadata
    with tifffile.TiffFile(path_to_image) as tif:
        page = tif.pages[0]
        metadata = defaultdict(dict)
        for tag in page.tags.values():
            name, value = tag.name, tag.value
            metadata['raw_metadata'][name] = value

        if tif.is_imagej:
            metadata['imagej_metadata'] = tif.imagej_metadata

        if tif.ome_metadata:
            metadata['ome_metadata'] = tif.ome_metadata
        
        shape = list(page.shape)
        shape.append(len(tif.pages))
        
        # default, minimum set of metadata
        metadata['dtype'] = str(page.dtype)
        metadata['unit'] = [metadata.get('imagej_metadata', {}).get('unit')]*len(shape)
        metadata['voxel_size'] = [metadata.get('imagej_metadata', {}).get('spacing')]*len(shape)
        metadata['channels'] = metadata['raw_metadata']['SamplesPerPixel']
        metadata['shape'] = shape[::-1] # z,y,x order
        return dict(metadata)

    


