from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib
import json
import requests
import xmltodict

async def get_webpage_soup(url: str, response_delay : int, timeout : int):
    """Get Soup object of the page 

    Args:
        url (str): web page url

    Returns:
        bs4.BeautifulSoup: web page url
    """
    
    async with async_playwright() as p:
        # slow_mo is important, kep chromium open long enough for the data to load
        browser = await p.chromium.launch(slow_mo=response_delay) 
        page = await browser.new_page()
        await page.goto(url, timeout=timeout)

        body_html = await page.inner_html("body")
        soup = BeautifulSoup(body_html, "html.parser")

        await browser.close()
        return soup
    
def parse_neuroglancer_url(url):
    """return json data stored in neuroglancer url

    Args:
        url (str): neuroglancer link

    Raises:
        ValueError: _description_

    Returns:
        json: json metadata stored in ng link
    """
    if "#!" not in url:
        raise ValueError("Invalid Neuroglancer link format")
    encoded_json = url.split("#!")[-1]
    decoded_json = urllib.parse.unquote(encoded_json)
    regularize = decoded_json.replace("'", '"')
    return json.loads(regularize) 

def remote_xml_metadata_to_dict(url : str):
    """Fetch remote xml metadata and parse it to a dictionary 

    Args:
        url (str): Path to remote xml file

    Returns:
        dict: nested dictionary
    """

    response = requests.get(url)
    response.raise_for_status()
    return xmltodict.parse(response.content)
