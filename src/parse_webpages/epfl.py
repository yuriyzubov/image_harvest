from util_etl import get_webpage_soup
import asyncio


def web_metadata_epfl(url : str):
    soup = asyncio.run(get_webpage_soup(url))
    post = soup.find("article", id="post-2138", class_="post-2138")

    # scrap useful data
    metadata = dict()
    data_section = post.find("h3", id="data")
    metadata['dataset_description'] = data_section.find_next("p").text.strip()
    download_links = []
    for a in post.find_all("a", href=True):
        href = a['href']
        if any(href.lower().endswith(f".{item}") for item in ['zarr', 'n5', 'tiff', 'mrc', 'tif']):
            download_links.append(href.strip())
            
    metadata['download_links'] = download_links
    return metadata




