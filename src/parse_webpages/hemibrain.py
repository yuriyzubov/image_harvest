import requests
from util_etl import parse_neuroglancer_url

def expand_tinyurl(short_url):
    response = requests.head(short_url, allow_redirects=True)
    return response.url
 
def web_metadata_hemibrain(short_url):
    parsed_ng_data = parse_neuroglancer_url(expand_tinyurl(short_url))
    links_to_datasets = [layer['source'] if isinstance(layer['source'], str) else layer['source']['url'] for layer in parsed_ng_data['layers']]
    metadata = dict()
    metadata['raw_metadata'] = parsed_ng_data
    metadata['download_links'] = links_to_datasets
    
    return metadata
    
