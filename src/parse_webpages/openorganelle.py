import asyncio
from util_etl import get_webpage_soup, parse_neuroglancer_url
from collections import defaultdict

def get_image_metadata(soup, tag, header_text):
    """return open_organelle image metadata in a structured dict 

    Args:
        soup (bs4.BeautifulSoup): web page html stored as soup object
        tag (str): html tag to search against
        header_text (str): header text

    Returns:
        _type_: _description_
    """
    param_header = soup.find(tag, string=header_text)
    if param_header:
        # Find the parent <div> that wraps the <h6> and its following <p> tags
        container = param_header.find_parent('div')
        # Find all <p> tags that belong to div container
        paragraphs = container.find_all('p')

        # Print them as key-value pairs
        metadata = {}
        for p in paragraphs:
            if 'http' in p.text:
                key, value = p.text.split('http', 1)
                value = 'http' + value 
            elif ':' in p.text:
                key, value = p.text.split(':', 1)
            metadata[key.replace(' ', '_')] = value
        return metadata

def web_metadata_openorg(url):
    soup = asyncio.run(get_webpage_soup(url, 1000, 10000))
    raw_metadata = defaultdict(dict)
    header_names = ['Acquisition details', 'FIB-SEM parameters']
    for hn in header_names:    
        raw_metadata[hn] = get_image_metadata(soup, 'h6', hn)

    # Fetch and parse neuroglancer link
    ng_link = soup.find("a", href=lambda href: href and "neuroglancer-demo.appspot.com" in href)['href']
    ng_url = ng_link.replace('%22white%22', '%5C%22white%5C%22').replace('_', '%2C')
    parsed_ng_data = parse_neuroglancer_url(ng_url)
    
    # Collect ng lings
    links_to_datasets = []
    for layer in parsed_ng_data['layers']:
        if isinstance(layer['source'], str):
            url = layer['source']
        else:
            url = layer['source']['url']
        links_to_datasets.append(url.replace(',', '_'))
        
    metadata = dict()
    metadata = {'raw_metadata' : raw_metadata, 'download_links' : links_to_datasets}
    return metadata
