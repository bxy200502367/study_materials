# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230515
# last_modified: 20230515

"""
重命名一拆的结果
"""

import argparse
import json
import os


def rename_library(result_dir: str, rename_file: str) -> None:
    with open(rename_file, "r") as f:
        rename_info = json.loads(f.read())
    for lane_match, library_info_list in rename_info.items():
        for library_info in library_info_list:
            old_name_dir = os.path.join(result_dir, library_info['sample_id'])
            if not os.path.exists(old_name_dir):
                continue
            old_new = {}
            for fq in os.listdir(old_name_dir):
                if fq.endswith("R1_001.fastq.gz"):
                    new_name = library_info["library_number"] + "--" + library_info["specimen_name"] +\
                               ".R1.raw.fastq.gz"
                    os.rename(os.path.join(old_name_dir, fq), os.path.join(old_name_dir, new_name))
                    old_new[fq] = new_name
                elif fq.endswith("R2_001.fastq.gz"):
                    new_name = library_info["library_number"] + "--" + library_info["specimen_name"] + \
                               ".R2.raw.fastq.gz"
                    os.rename(os.path.join(old_name_dir, fq), os.path.join(old_name_dir, new_name))
                    old_new[fq] = new_name
                else:
                    pass
            md5sum_path = os.path.join(old_name_dir, "md5sum.txt")
            md5_info = {}
            with open(md5sum_path, "r") as f:
                for line in f:
                    line_list = line.strip().split("  ")
                    if line_list[1] in old_new.keys():
                        md5_info[old_new[line_list[1]]] = line_list[0]
                    else:
                        md5_info[line_list[1]] = line_list[0]
            with open(md5sum_path, "w") as w:
                for f in md5_info.keys():
                    w.write(md5_info[f] + "  " + f + "\n")


parser = argparse.ArgumentParser(description="重命名一拆的结果")
parser.add_argument("-i", "--result_dir", required=True)
parser.add_argument("-o", "--rename_file", required=True)
args = vars(parser.parse_args())
rename_library(args["result_dir"], args["rename_file"])
