import hyperspy.api as hs
from collections import defaultdict
file_path = 'data/empiar/data/F57-8_test1_3VBSED_slice_0001.dm3'

def get_metadata_dm3(path_to_dm3:str):
    s = hs.load(path_to_dm3)
    metadata = defaultdict(dict)
    metadata['raw_metadata'] = s.metadata.as_dictionary()

    dim_num =len(s.axes_manager._axes)
    metadata['voxel_size'] = [s.axes_manager[i].scale for i in range(0, dim_num,1)]
    metadata['unit'] = [s.axes_manager[i].units for i in range(0, dim_num,1)]
    metadata['offset'] = [s.axes_manager[i].offset for i in range(0, dim_num,1)]
    metadata['dtype'] = str(s.data.dtype)
    metadata['shape'] = list(s.data.shape)

    return metadata 
    

