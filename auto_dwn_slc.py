# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 14:58:32 2019

@author: Nejc Coz
@copyright: ZRC SAZU (Novi trg 2, 1000 Ljubljana, Slovenia)

IMPORTANT: Set your SciHUB account credentials in apihub.txt!

- The script downloads Sentinel products based on a query.
- Only works for 'Online' products. Archived products (in LTA) have to be
retrieved and downloaded using the *_LTA.py scripts instead.
"""

import logging
import sys
from os import walk
from datetime import datetime
from collections import OrderedDict
from shapely.geometry import box
from sentinelsat import SentinelAPI, InvalidChecksumError, SentinelAPILTAError
# from sentinelsat import read_geojson, geojson_to_wkt


def main(dwndir, logpath, apipath, qp):
    # Configure file for logging
    # ==========================
    logging.basicConfig(
        filename=logpath,
        format='%(asctime)s:%(module)s:%(levelname)s: %(message)s',
        level=logging.INFO
    )
    with open(logpath, "a") as f:
        loghead = f"\nStarting a new session\n{datetime.now()}\n" + 26 * "=" + "\n"
        f.write(loghead)
    logging.info('Started auto_dwn_slc.py')

    # Read password file
    # ==================
    try:
        with open(apipath) as f:
            (usrnam, psswrd) = f.readline().split(" ")
            if psswrd.endswith("\n"):
                psswrd = psswrd[:-1]
    except IOError:
        logging.error("Error reading the password file!")
        sys.exit("Error reading the password file!")

    # Connect to API using <username> and <password>
    # ===============================================
    print("Connecting to SciHub API...")
    api = SentinelAPI(usrnam, psswrd, "https://scihub.copernicus.eu/dhus")

    # Search by SciHub query keywords
    # ===============================
    products = api.query(qp['footprint'],
                         beginposition=(qp['strtime'], qp['endtime']),
                         endposition=(qp['strtime'], qp['endtime']),
                         platformname=qp['platformname'],
                         producttype=qp['producttype'])

    # Create list of files for download
    # =================================
    fresh_products = []
    for item_key in products.keys():
        item = products[item_key]
        fresh_products.append(item['title'])

    # List of already downloaded items
    already_downloaded = []

    # r=root, d=directories, f=files
    for r, d, f in walk(dwndir):
        for file in f:
            if ".zip" in file and ".incomplete" not in file:
                already_downloaded.append(file[:-4])

    # Find all files that haven not been downloaded yet (by filename)
    new_files = set(fresh_products) - set(already_downloaded)
    for_download = list(new_files)

    # Get UUID-s of the files for download
    uuid_list = []
    for item_key in products.keys():
        item = products[item_key]
        if item['title'] in for_download:
            uuid_list.append(item['uuid'])

    # Download files from the list
    # ============================
    # Check if there were any new files found, otherwise skip download
    if len(uuid_list) > 0:
        logging.info("{len(uuid_list)} files selected for download!")
        # Set some parameters
        max_attempts = 10
        checksum = True
        # Set for catching errors
        return_values = OrderedDict()
        last_exception = None

        # Main loop for downloading
        for i, product_id in enumerate(uuid_list):
            logging.info(f"Start download {i + 1} of {len(uuid_list)}")

            # For multiple attempts of loading the same file
            for att_num in range(max_attempts):
                try:
                    product_info = api.download(product_id, dwndir, checksum)
                    return_values[product_id] = product_info
                    break
                except (KeyboardInterrupt, SystemExit):
                    raise
                except InvalidChecksumError as e:
                    last_exception = e
                    logging.warning(
                        "Invalid checksum. The downloaded file for"
                        f" '{products[product_id]['title']}' is corrupted."
                    )
                except SentinelAPILTAError as e:
                    last_exception = e
                    logging.warning(
                        f"There was an error retrieving"
                        f" '{products[product_id]['title']}' from the LTA"
                    )
                    break
                except Exception as e:
                    last_exception = e
                    logging.warning(
                        "There was an error downloading %s"
                        f" '{products[product_id]['title']}'."
                    )
            # Log the number of the file that was just downloaded
            logging.info(f"{i + 1}/{len(uuid_list)} products downloaded")

        # If all downloads fail raise exception
        failed = set(uuid_list) - set(return_values)
        if len(failed) == len(uuid_list) and last_exception is not None:
            raise last_exception
    else:
        # If no new files were found
        logging.info("No new files found!")

    logging.info('The script has finished!')
    logging.shutdown()


if __name__ == "__main__":
    # Download folder
    dwn_pth = 'R:\\Sentinel-1_SLC\\'

    # Path to log file
    log_pth = ".\\userfiles\\LOGFILE.log"

    # Path to file with SciHub credentials
    api_pth = ".\\userfiles\\apihub.txt"

    # Set query parameters
    ############################################################################
    #   * (Date-type query parameter 'beginposition' expects a two-element tuple
    #     of str or datetime objects.)
    #   * Search for last 24 hrs: date=('NOW-8HOURS', 'NOW') or NOW-<n>DAY(S) or
    #     datetime(2017, 1, 5, 23, 59, 59, 999999) + import datetime or string
    #     '2017-12-31T23:59:59.999Z'
    strtime = 'NOW-2MONTH'  # 'NOW-14DAYS'
    endtime = 'NOW-2DAYS'  # '2019-07-31T23:59:59.999Z'

    # Platform name:
    platformname = 'Sentinel-1'

    # Product type:
    producttype = 'SLC'

    # Geographical extents (minx, miny, maxx, maxy)
    footprint = box(13.278422963870495, 45.33663869316604,
                    16.687265418304985, 46.96845660190081)
    # nam_aoi = 'polygon.geojson'
    # pth_aoi = join(wrkdir, nam_aoi)
    # footprint = geojson_to_wkt(read_geojson(pth_aoi))

    query_params = {
        'strtime': strtime,
        'endtime': endtime,
        'platformname': platformname,
        'producttype': producttype,
        'footprint': footprint
    }

    main(dwn_pth, log_pth, api_pth, query_params)
