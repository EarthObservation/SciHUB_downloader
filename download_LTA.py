# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 12:04:46 2019

@author: Nejc Coz
@copyright: ZRC SAZU (Novi trg 2, 1000 Ljubljana, Slovenia)

IMPORTANT: Set your SciHUB account credentials in apihub.txt!

Download files from SciHUB listed in a CSV file:
    - required values in CSV file are: 'id', 'title' and 'downloaded'
    - script reads the SciHUB credentials and connects to the API
    - loads the CSV file into DataFrame
    - For each file, check if it is 'Online', if not retrieve from LTA
    - If it is 'Online', proceed with download
    - Update the CSV file when the download is complete
"""

import pandas as pd
import logging
import sys

from os.path import basename
from datetime import datetime
from time import sleep
from sentinelsat import SentinelAPI, InvalidChecksumError


def main(dwndir, csvpath, logpath, apipath):
    # Configure file for logging
    # ==========================
    logging.basicConfig(
        filename=logpath,
        format="%(asctime)s - %(module)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    with open(logpath, "a") as f:
        loghead = f"\nStarting a new session\n{datetime.now()}\n" + 26 * "=" + "\n"
        f.write(loghead)
    print("Started script download_LTA.py")
    logging.info("Started script download_LTA.py")

    # Read password file
    # ==================
    try:
        with open(apipath) as f:
            (usrnam, psswrd) = f.readline().split(" ")
            if psswrd.endswith("\n"):
                psswrd = psswrd[:-1]
    except IOError:
        logging.info("Error reading the password file!")
        sys.exit("Error reading the password file!")

    # Connect to API using <username> and <password>
    # ==============================================
    print("Connecting to SciHub API...")
    api = SentinelAPI(usrnam, psswrd, "https://scihub.copernicus.eu/dhus")

    # Read CSV file
    # =============
    try:
        dwnfil = pd.read_csv(csvpath)
        print(f"Import CSV file: {basename(csvpath)}")
        logging.info(f"Import CSV file: {basename(csvpath)}")
    except IOError:
        logging.info("Error reading the CSV file!")
        sys.exit("Error reading the CSV file!")

    # Download files from the CSV list
    # ================================
    max_attempts = 10
    checksum = True
    product_ids = list(dwnfil['uuid'])
    # product_example = "672e5131-c79d-4500-b825-9dabf40662e3"
    print(f"Found {len(product_ids)} products in CSV list.\n")
    logging.info(f"Found {len(product_ids)} products in CSV list.\n")

    # Main loop for download
    # ======================
    for i, product_id in enumerate(product_ids):
        if not dwnfil['downloaded'].get(i):
            current_file = api.get_product_odata(product_id)
            print(f"     Next file: {current_file['title']}")
            print(f"     File uuid: {product_id}")
            logging.info(f"     Next file: {current_file['title']}")
            logging.info(f"     File uuid: {product_id}")

            # If product isn't online (it is in LTA), wait and check every 5 min
            waiting = 0
            while not current_file['Online']:
                if waiting == 0:
                    print("File is offline, waiting 5 min...")
                    logging.info("File is offline, waiting 5 min...")
                sleep(5*60)
                waiting += 5
                print(f"{waiting} min has passed, file still Offline..")
                logging.info(f"{waiting} min has passed, file still Offline..")

            # When file goes online proceed with download
            for attempt_num in range(max_attempts):
                try:
                    api.download(product_id, dwndir, checksum)
                    # Update CSV file
                    dwnfil.at[i, 'downloaded'] = True
                    dwnfil.to_csv(csvpath, index=False)
                    logging.info("CSV file updated\n")
                    break
                except (KeyboardInterrupt, SystemExit):
                    raise
                except InvalidChecksumError as e:
                    logging.info(f"Invalid checksum. The downloaded file for '{product_id}' is corrupted.")
                    logging.error(e)
                except Exception as e:
                    logging.info(f"There was an error downloading {product_id}")
                    logging.error(e)
            else:
                logging.info(f"    ****  File {product_id} was not Online!\n")
        else:
            logging.info(f"SKIP!  File {product_id} has already been downloaded.\n")

    # End message
    # ============
    print("---------  Session finished  ---------")
    logging.info(f"---------  Session {dwndir} finished  ---------\n")
    logging.shutdown()


if __name__ == "__main__":
    # Download folder
    dwn_pth = "R:\\Sentinel-1_SLC\\"

    # Path to CSV file with a list of products to be triggered
    csv_pth = ".\\userfiles\\slc_list.csv"

    # Path to log file
    log_pth = ".\\userfiles\\LOGFILE_lta.log"

    # Path to file with SciHub credentials
    api_pth = ".\\userfiles\\apihub.txt"

    main(dwn_pth, csv_pth, log_pth, api_pth)
