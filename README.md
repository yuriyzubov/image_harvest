hello!

The goal of this small project was to investigate the contents of em image data published on several common em image portals:

1. https://idr.openmicroscopy.org/webclient/img_detail/9846137/?dataset=10740

2. https://www.ebi.ac.uk/empiar/EMPIAR-11759/

3. https://www.epfl.ch/labs/cvlab/data/data-em/

4. https://openorganelle.janelia.org/datasets/jrc_mus-nacc-2

5. https://tinyurl.com/hemibrain-ng

The target pipeline should look like this:

1. From the provided url get dataset description and download links.

2. Download datasets in a reasonable time. If possible, utilize multiple threads to reduce the download time. 

3. Get all the metadata from the image files, consolidate and normalize the most common parameters in a table for comparison. 

**Initial setup**

the initial setup requires three things:

1. clean environment with python=3.11

`conda create -n image_harvest python=3.11`

2. install python dependencies from the requirements.txt:

`python3 -m pip install -r requirements.txt`

3. To download some images faster, I utilized `aira2c` cli tool:

    Mac OS: `brew install aria2`

    Ubuntu: `sudo apt install aria2`

**The development process**


**Pre-inspection, before downloading the whole dataset**

First of all, in order to inspect the metadata of the image file, oftentimes there is no need to download the whole dataset.

 For the chunked datasets, metadata is stored in separate files, and the file schema is regularized. I wrote 2 methods - for zarr container (`get_zarr_s3_attrs()`)  and neuroglancer_precomputed (`get_spec_ts()`) that would allow reading metadata files (zarr - .zattrs and .zgroup, neuroglancer_precomputed - info file), without downloading a dataset.

  For files like tiff or dm3, we can read from the bytestream and typically the metadata is stored within the first few MB of the file. I wrote a small `get_remote_tiff_metadata()` method to get tiff tags without downloading the whole dataset. There is no need to download GBs of files to fetch a few KB of text data :)

**Scraping the webpage data**

Some portals contain more information on the webpage than the image file itself, 
so it is good to have some tools to get html data and parse it for the useful dataset information. 

For this step I used combination of PlayWright and BeautifulSoup packages.
I used PlayWright for getting raw html data, and BSoup for parsing the data. 
One important note is that many websites do not load all the data at once, so I had to wait a little bit, for the data to load in the `get_webpage_soup()` method.

Getting the html data, get_webpage_soup() worked well for all of the source portals, but scraping the data with BSoup was on a portal-to-portal basis. 

The way I stored web metadata was:

`{'raw_metadata': dict , 'download_links' : list}`

`hemibrain dataset`: I parsed a neuroglancer link and extracted all json - encoded metadata, and path to datasets. 

`openorganelle`: I parsed the dataset webpage and extracted  ['Acquisition details', 'FIB-SEM parameters'], as well as ng_link to get the source of the image.

`idr data`: I browsed an ftp server according to instructions posted on (IDR) portal to source the location of the output .tiff file.

`epfl`: Scraped the article contents with BSoup and extracted path to .tiff data.

`empiar`: The dataset description comes from xml file, so I parsed html data to get the urls of the xml file and the image data.

I scraped and stored web metadata in `web_metadata.json` by running:

`python3 src/parse_webpages/main_webmetadata.py`

**Downloading the data**

Using the download links stored in `web_metadata.json` we finally can start fetching the image data itself. 

I have three kinds of structures:

1. Monolithic tiff files

2. A directory with dm3 files 

3. Chunked data stored in zarr and ng_precomputed containers.

For the tiff file, my approach was to read the file by byte blocks using multiple requests at once to the ftp server. I wrote a multithreading implementation (example: `download/single_file_parellel.py`), but could not utilize it to the full extent due to the limits on the number of requests to the ftp server (~4 req/s, 3MB per request). The download time for the 150 MB file was `1m52s`, which is comparable with typical browser download times. 

I wanted to speed it up, so I've looked at highly optimized alternatives: `lftp` and `aria2c`.

Lftp gave me a **3x** download boost, but I could only use it with ftp servers. Aria2c allows to fetch data from both ftp and http server, so I used it as the main client for downloading the data (with the same download speeds as lftp).

I wrote thin python wrappers for the cli tools (`single_file.py`, `directory.py`)
to integrate aria2c with my python scripts. When downloading the directory, I first indexed remote directory files and stored in a temporary text file for aria2c to process. 

For the neuroglancer_precomputed hemibrain metadata, the tensor store allows to read the data asynchronously by default, so I only specified source and destination specs, and had to make `get_crop()` asynchronous, since many underlying tensor store methods are async.

The zarr dataset from openorganelle has a group directory structure, but Zarr groups are not included in tensorstore spec. I wrote a custom method that fetches all arrays stored in the source zarr group and copies them with `ThreadPoolExecutor`. One way I think to improve copying of the zarr data is to use tensorestore to copy the zarr array data itself, after zarr group hierarchy is created and all metadata is in place.

To download the data I ran this script from the main directory:

`python3 src/download/main_download.py`

**Fetch the image metadata locally**

After downloading the image data, I've used standard python packages for reading the metadata:

1. `tiff : tifffile`

2. `neuroglancer_precomputed : tensorstore`

3. `zarr : zarr-python`

4. `dm3 : hyperspy`

 I stored all the extracted metadata under the 'raw_metadata' key and extracted some crucial image metadata parameters for comparison across 5 different datasets:

The metadata schema is:

`{'shape' : list, 'dtype': str,'unit' : str,'voxel_size' : list[float],'offset' : list[float], 'channels' : int,'raw_metadata' : dict}`

I ran `python3 src/file_metadata/main_metadata.py` to collect and store dataset parameters in `file_metadata.json`

The comparison results for different datasets metadata are shown in this table, plotted with `data_table.ipynb`:


| dataset        | dtype  | unit                                | voxel_size                          | channels | shape               | offset                | axes       |
|----------------|--------|--------------------------------------|--------------------------------------|----------|----------------------|------------------------|------------|
| epfl           | uint8  | [None, None, None]                  | [None, None, None]                  | 1        | [1065, 2048, 1536]   | NaN                    | NaN        |
| idr            | uint8  | [µm, µm, µm]                        | [0.02, 0.02, 0.02]                  | 1        | [184, 1121, 775]     | NaN                    | NaN        |
| empiar         | uint8  | [µm, µm]                            | [0.007998250424861908, 0.007998250424861908] | NaN      | [5500, 5496]         | [-0.0, -0.0]           | NaN        |
| openorganelle  | int16  | [nanometer, nanometer, nanometer]  | [2.96, 4.0, 4.0]                    | NaN      | [564, 2520, 2596]    | [0.0, 0.0, 0.0]        | [z, y, x]  |
| hemibrain      | uint8  | [nm, nm, nm]                        | [8.0, 8.0, 8.0]                     | 1        | [200, 400, 600]      | [10000, 11000, 12000]  | [z, y, x]  |

Epfl tiff file lacks 5nm voxel size within the metadata, which could be parsed from the scraped metadata stored in `web_metadata.json`

The `dm3` file metadata also contained acquisition details, that could be compared to the scraped web metadata from the openorganelle portal.

| Parameter             | OpenOrganelle | EMPIAR                 |
|-----------------------|------------------------------------|-------------------------------|
| **Beam energy**       | 200 eV                             | 1.9 keV             |
| **Beam current**      | 0.22 nA                            | 0.0 nA                        |
| **Scan parameters**   | Scan rate: 0.4 MHz       | Dwell time (s): 5e-07  |
| **Microscope**        | NaN                      | FEI Quanta                    |
| **Magnification**     | NaN                      | 2159.0                         |
| **Bias voltage**      | 500 V                              | NaN                 |
| **Imaging duration**  | 1 day                              | NaN                 |



**Data ingestion**


Typically, volumetric datasets are ~TB in size, and it's not efficient to pass the whole dataset to a ML pipeline. It would make sense to load the data in small blocks to provide a consistent load across multiple CPU/GPUs.

Here is how I think I would implement the data loading software.

First, I'll try to make sure that the data serving is lazily evaluated, i.e. the data block is loaded only when task is being computed. 

Secondly, I would build a task scheduler that spawns worker processes to load/unload the data. It also must check the status of workers, to reassign tasks in case of failure and resource monitoring. 

It really might seem like building the scheduler by implementing a pool of tasks is the way to go to distribute tasks between workers. In cases when each block is independent, that would make perfect sense. However, there are also cases, when each block would depend on the neighboring data, for example - connected component analysis or tiling. Knowing this, I would try to implement a direct acyclical graph approach, as it would allow to avoid data artefacts caused by lack of information exchange between blocks. I also would implement an extra queue to collect failed tasks for a retry.

I think adding a preliminary test run for the few tasks to check the utilization of the GPU is a good idea. There might be a situation when a GPU would sit idle for a substantial time of the compute cycle, expecting the data to load/unload.

Implementing task batching. It is useful to reduce potential direct acyclical graph size, to prevent scheduler overhead.

**Robust validation of the metadata**

I would also add preliminary validation of the image metadata, such as data type, offset, or voxel size to prevent faulty training of ML models. Or another example, data contrast limits should be within a proper range otherwise the image would be too bright or too dark.

**File formats**

I would implement reading/writing of the data from/into the chunked file formats that are designed for parallel tasks. A healthy split of the large image file into many small files could help with parallelization of reading/writing. 

**Extra**

It might be overlooked, but properly designed, intuitive API as well as spending time on distribution infrastructure might also improve development time and adoption rate.

The nature of the hardware, where the data is transferred. If it is a CPU, then everything above stands, but if it is a GPU computation, then block batching must be implemented to reduce transfer time from host to device. If possible, I would also avoid decompressing data on the CPU, and instead serve compressed data to GPU, to reduce amount of transferred data.  




