import time
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import pyvips
import zipfile
import tarfile
import json
import os

def convert_zip(filename, out_dir, size):
    start_time = time.perf_counter()

    with zipfile.ZipFile(filename) as jp2_dir:
        for file in jp2_dir.namelist():
            with jp2_dir.open(file) as jp2_file:
                if file.endswith('.jp2'):
                    try:
                        thumbnail = pyvips.Image.thumbnail_buffer(jp2_file.read(),
                                                                  size)
                        new_name = Path(out_dir) / file.split('/')[-1][:-4]
                        new_path = str(new_name) + '.jpg'
                        thumbnail.write_to_file(new_path)
                    except:
                        print('Error with ', file)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    return elapsed_time

def convert_tar(filename, out_dir, size):
    start_time = time.perf_counter()

    with tarfile.open(filename) as jp2_dir:
        for file in jp2_dir.getmembers():
            if file.endswith('.jp2'):
                thumbnail = pyvips.Image.thumbnail_buffer(jp2_dir.extractfile(file).read(),
                                                          size)
                new_name = Path('out_dir') / file.split('/')[-1][:-4]
                new_path = str(new_name) + '.jpg'
                thumbnail.write_to_file(new_path)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    return elapsed_time

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_file",
                    help="JP2 archive file")
    ap.add_argument("-o", "--output_dir",
                    help="Output directory")
    ap.add_argument('-s', '--size',
                    help="Thumbnail size")
    ap.add_argument('--delete_jp2', action='store_true')
    args = ap.parse_args()

    filename = Path(args.input_file)
    if os.path.exists(filename):
        if filename.suffix == '.zip':
            convert_time = convert_zip(filename, args.output_dir, args.size)
        elif filename.suffix == '.tar':
            convert_time = convert_tar(filename, args.output_dir, args.size)
        if args.delete_jp2:
            os.remove(filename)
