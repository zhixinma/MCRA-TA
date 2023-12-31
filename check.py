import pandas as pd
import argparse
import requests
import json
import time
import csv
from datetime import date
import os


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source_folder', dest='s')
    parser.add_argument('-s_date', '--source_date', dest='s_date')
    parser.add_argument('-t', '--target_folder', dest='t')
    parser.add_argument('-t_date', '--target_date', dest='t_date')
    args = parser.parse_args()
    return args

def compare(args):
    f_src = args.s
    date_src = args.s_date
    f_tgt = args.t
    date_tgt = args.t_date
    # path_badges = "badges"
    # path_details = "details"
    # path_skills = "skills"

    for postfix in ["badges", "details", "skills"]:
        file_path_src = f"{f_src}/{date_src}/{date_src}_{postfix}.csv"
        file_path_tgt = f"{f_tgt}/{date_tgt}/{date_tgt}_{postfix}.csv"
        with open(file_path_src, "r") as f:
            csv_src = csv.reader(f)
            csv_src = list(csv_src)
        with open(file_path_tgt, "r") as f:
            csv_tgt = csv.reader(f)
            csv_tgt = list(csv_tgt)
        
        print(f"Comparing {postfix}...")
        print(f"Source: {len(csv_src)}")
        print(f"Target: {len(csv_tgt)}")
        print(f"Source - Target: {len(csv_src) - len(csv_tgt)}")
        print(f"Target - Source: {len(csv_tgt) - len(csv_src)}")
        print()


if __name__ == "__main__":
    args = get_args()
    compare(args)
