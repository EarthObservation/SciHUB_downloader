# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 09:13:34 2019

@author: Nejc Coz
@copyright: ZRC SAZU (Novi trg 2, 1000 Ljubljana, Slovenia)

IMPORTANT: Set your SciHUB account credentials in apihub.txt!

An improvised method to trigger retrieval from LTA in SciHUB. The server allows
only one retrieval request every 30 min. The status of a specific product can be
obtained by checking the 'Online' attribute in the metadata. If 'Online' is set
to False, the file has to be retrieved from LTA before starting the download.

The program loops through a list of products provided through a CSV file. For
each product, the program first checks the 'Online' status and triggers its
retrieval if false. It waits 31 min before starting the retrieval of the next
product.
"""

import logging
from datetime import datetime
import pandas as pd
import sys
from sentinelsat import SentinelAPI, SentinelAPILTAError
from time import sleep


def main(csvpath, logpath, apipath):
    # Configure file for logging
    # ===========================
    logging.basicConfig(filename=logpath,
                        format="%(asctime)s - %(message)s",
                        level=logging.INFO)
    with open(logpath, "a") as f:
        loghead = f"\nStarting a new session\n{datetime.now()}\n" + 26 * "=" + "\n"
        f.write(loghead)
    logging.info("Started trigger_LTA.py")

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
    # ==============================================
    print("Connecting to SciHub API...")
    api = SentinelAPI(usrnam, psswrd, "https://scihub.copernicus.eu/dhus")

    # Read CSV file
    # ==============
    try:
        dwnfil = pd.read_csv(csvpath)
        print(f"Import CSV file: {csvpath}")
        logging.info(f"Import CSV file: {csvpath}")
    except IOError:
        logging.info("Error reading the CSV file!")
        sys.exit("Error reading the CSV file!")
    print(f"Found {dwnfil.shape[0]} products.")
    logging.info(f"Found {dwnfil.shape[0]} products.")

    # Trigger LTA retrieval
    # ======================
    product_ids = list(dwnfil['uuid'])

    f_skip = 0
    f_trig = 0
    for i, product_id in enumerate(product_ids):
        current_file = api.get_product_odata(product_id)
        logging.info(f"     Next file: {current_file['title']}")
        logging.info(f"     File uuid: {product_id}")
        print(f"Product {i+1}/{len(product_ids)}: {current_file['title']}")
        if not dwnfil['downloaded'].get(i):
            if not current_file['Online']:
                # Trigger retrieval from LTA
                try:
                    api.download(product_id)
                    f_trig += 1
                except (KeyboardInterrupt, SystemExit):
                    raise
                except SentinelAPILTAError as e:
                    # Retry if user quota exceeded, else log error and go to next file
                    if e.msg == "Requests for retrieval from LTA exceed user quota":
                        logging.info("Waiting 31 min before retrying")
                        sleep(31 * 60)
                        try:
                            api.download(product_id)
                            f_trig += 1
                        except (KeyboardInterrupt, SystemExit):
                            raise
                        except SentinelAPILTAError:
                            logging.info(f"There was an error retrieving {product_id} from the LTA")
                    else:
                        logging.info(f"There was an error retrieving {product_id} from the LTA")
                # Wait 31 min after a successful trigger
                logging.info("Waiting 31 min before triggering next file\n")
                sleep(31*60)
            else:
                f_skip += 1
                print("File already online")
                logging.info("File already online")
        else:
            logging.info("File already downloaded")

    # End message
    # ============
    print("---------  Session finished  ---------")
    logging.info("   FINISHED!")
    logging.info(f"{f_trig} files retrieved, {f_skip} files skipped")
    logging.shutdown()


if __name__ == "__main__":
    # Path to CSV file with a list of products to be triggered
    csv_pth = ".\\userfiles\\slc_list.csv"

    # Path to log file
    log_pth = ".\\userfiles\\LOGFILE_trigger.log"

    # Path to file with SciHub credentials
    api_pth = ".\\userfiles\\apihub.txt"

    main(csv_pth, log_pth, api_pth)
