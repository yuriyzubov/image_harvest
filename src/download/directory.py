import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from urllib.parse import urlparse
import os
import subprocess


def list_files_recursive(base_url, delay=0.01):
    """Recursively list files within ftp directory

    Args:
        base_url (_type_): _description_
        delay (float, optional): _description_. Defaults to 0.01.

    Returns:
        list: file urls
    """
    file_urls = []
    visited = set()
    print('Indexing files in the directory...')
    # Normalize base for comparison
    base_url = base_url.rstrip("/") + "/"
    parsed_base = urlparse(base_url)
    base_path = parsed_base.path if parsed_base.path.endswith('/') else parsed_base.path + '/'
    def crawl(url):
        if url in visited:
            return
        visited.add(url)

        time.sleep(delay)
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception as e:
            print(f"Failed to access {url}: {e}")
            return

        soup = BeautifulSoup(resp.text, "html.parser")

        for link in soup.find_all("a"):
            href = link.get("href")
            if not href or href.startswith("?") or href.startswith("#"):
                continue

            full_url = urljoin(url, href)
            parsed = urlparse(full_url)

            # Make sure the only files within base dir are listed
            if not parsed.path.startswith(base_path):
                continue

            if href.endswith('/'):
                crawl(full_url)
            else:
                file_urls.append(full_url)

    crawl(base_url)
    print("Finished indexing.")
    return file_urls

# store links and relative paths
def aria2c_list(file_list : list,
              out_file : str,
              base_url : str,
              output_dir : str):
    """List all files in a temp_file, for aria2c

    Args:
        file_list (list): _description_
        out_file (str): _description_
        base_url (str): _description_
        output_dir (str): _description_
    """
    
    with open(out_file, "w") as fout:
        for url in file_list:
            url = url.strip()
            rel_path = url.replace(base_url, '').strip('/').split('/')
            base_dir = base_url.strip('/').split('/')[-1]
            dir_path = os.path.join(output_dir,base_dir) if len(rel_path) == 1 else os.path.join(output_dir, base_dir) + '/' + '/'.join(rel_path[:-1])

            fout.write(url + '\n')
            fout.write(f"  dir={dir_path}\n")
            
def download_dir_aria2c(input_file, connections = 8, splits = 8):
    """downoload a directory from a remote server

    Args:
        url (str): path to directory
        connections (int, optional): Connections to a server. Defaults to 4.
        splits (int, optional): To how many splits to fractionalize the file when downloading it in parallel. Defaults to 4.
    """
    
    cmd = [
        "aria2c",
        "-x", str(connections),
        "-s", str(splits),
        "--input-file", input_file,
        "--continue", "true",
        "--auto-file-renaming=false",
        "--allow-overwrite=true",
        "; quit"
    ]
    result = subprocess.run(cmd, text=True)

    return result

