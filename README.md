# SciHUB_downloader
A collection of python routines for downloading Sentinel products from SciHub.

Requires sentinelsat package to run: https://pypi.org/project/sentinelsat/

Username and password for accsess to SciHUB are provided through the `apihub.txt` file in the `userfiles` directory. 

## AUTO-DOWNLOAD OF SENTINEL PRODUCTS
    - auto_dwn_slc.py
    - start_py.bat

The script was set up to run on STROJ for auto-download of Sentinel-1 SLC products. It is automatically run every Friday through the attached batch script. It queries for any new files and proceeds with download.


## Download from the Long-Term-Archive (LTA)
"The Data Hub Service implements the capability of requesting products removed from the online archives but available on the Long Term Archives.

Access to the product URL for data that are no longer available online will automatically trigger the retrieval from the LTA. The actual download can be initiated by the user once the data are restored (within 24 hours).

A user quota on the maximum number of requests per hour per user is set.

Products restored from the long term archives are kept online for a period of at least 3 days. Quota and keeping time will be fine tuned according to the usage patterns to ensure efficient access to the most recent and frequently downloaded data."
https://scihub.copernicus.eu/userguide/LongTermArchive

The retrieval from LTA works in three steps:

  1\ Compile a list of products and save it to a CSV file --> `query_list_LTA.py`

  2\ Trigger retrieval of products from LTA --> `trigger_LTA.py`
  
    - quota for triggering of retrieval is 1 product per 30 min per user
    
    - it can take up to 24 hrs for the product to be retrieved (from my experience usually around 2-3 hrs)
    
    - there is no notification when the product is retrieved, you have to manually check the 'Online' status to find out
    
    - a retrieved product stays online for at least 3 days
 
  3\ Download retrieved products --> `download_LTA.py`
  
    - periodically (every 5 min) checks if the file is already online, and proceeds with download when True

