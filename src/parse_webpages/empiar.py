from util_etl import get_webpage_soup
import asyncio
from util_etl import remote_xml_metadata_to_dict


def web_metadata_empiar(url):
    
    soup = asyncio.run(get_webpage_soup(url, 1000, 20000))

    # all the useful information is stored in .xml file, so it makes sense to only download that data 
    xml_link = soup.find("a", string=lambda text: text and "Download xml" in text)['href']

    # get public url  
    tag = soup.find(attrs={"public-archive-ftp-url": True})
    ftp_url_all_data = tag.get("public-archive-ftp-url")

    # Cast path to ftp directory
    ftp_url = '/'.join([ftp_url_all_data, xml_link.rstrip('/').split('/')[-1].split('.')[0]])
    
    xml_metadata = remote_xml_metadata_to_dict(xml_link)
    metadata = {'raw_metadata' : xml_metadata, 'download_links' : [ftp_url]}
    
    return metadata

    
