from openorganelle import web_metadata_openorg
from hemibrain import web_metadata_hemibrain
from epfl import web_metadata_epfl
from empiar import web_metadata_empiar
import json
if __name__ == "__main__":
        out_json= './reference_metadata/web_metadata.json'
        print('Collecting metadata from web-pages...')
        web_metadata = {'openorganelle': web_metadata_openorg('https://openorganelle.janelia.org/datasets/jrc_mus-nacc-2/'),
                'hemibrain' : web_metadata_hemibrain('https://tinyurl.com/hemibrain-ng'),
                'epfl' : web_metadata_epfl('https://www.epfl.ch/labs/cvlab/data/data-em/'),
                'empiar' : web_metadata_empiar('https://www.ebi.ac.uk/empiar/EMPIAR-11759/'),
                'idr' : {'raw_metadata' : {}, 'download_links' : ['https://ftp.ebi.ac.uk/pub/databases/IDR/idr0086-miron-micrographs/20200610-ftp/experimentD/Miron_FIB-SEM/Miron_FIB-SEM_processed/Figure_S3B_FIB-SEM_U2OS_20x20x20nm_xy.tif']}
                }

        # store metadata in a json file:
        print(f'Storing web-sourced metadata in {out_json}')
        with open(out_json, 'w') as f:
                json.dump(web_metadata, f, indent=2)
