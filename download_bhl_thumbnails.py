import requests
from PIL import Image
import io
import time
import pandas as pd
import numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed
import argparse


def requests_PIL_download(photo_info):
    start_time = time.time()
    width, height = np.nan, np.nan
    filename = Path('page_thumbnails') / f"{photo_info['PageID']}.jpg"
    url_base = 'https://www.biodiversitylibrary.org/pagethumb'
    start_epoch = time.time()
    thumb_url = f"{url_base}/{photo_info['PageID']}"
    try:
        r = requests.get(thumb_url, timeout=60)
        if r.headers['Content-Type'] == 'image/jpeg':
            with Image.open(io.BytesIO(r.content)) as im:
                width, height = im.size
                im.save(filename)
        end_time = time.time()
    except:
        print(f"Error downloading photo {photo_info['PageID']}. Trying again...")
    end_time = time.time()
    return {'start_time':start_time,
            'end_time':end_time,
            'dl_time':end_time - start_time,
            'width': width, 'height': height, 'ids_id': photo_info['PageID']}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--processes",
                    help="number of processes")
    args = ap.parse_args()

    page_df = pd.read_csv('pages_to_download.tsv', sep='\t')
    page_list = page_df.to_dict(orient='records')
#    page_list = page_df.sample(1000).to_dict(orient='records')

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=int(args.processes)) as executor:
        dim_list = list(executor.map(requests_PIL_download, page_list))

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Downloaded {len(dim_list)} images in {elapsed_time} s")

    dim_df = pd.DataFrame(dim_list)
    dim_df.to_csv('bhl_page_dimensions.tsv', index=False, sep='\t')

