# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/06/11
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

"""
重命名纯文库
"""

import argparse
import os
import csv
from collections import namedtuple


def rename_self_library(self_library_info: str, indir: str) -> None:
    with open(self_library_info, "r") as f:
        f_csv = csv.reader(f, delimiter="\t")
        headers = next(f_csv)
        self_library_info_nt = namedtuple('self_library_info_nt', headers)
        old_new = {}
        for row in f_csv:
            each_row = self_library_info_nt(*row)
            dir_name = each_row.lane_name + "_" + each_row.library_number
            dir_name_path = os.path.join(indir, each_row.lane, dir_name)
            for fq in os.listdir(dir_name_path):
                if fq.endswith("R1_001.fastq.gz"):
                    new_name = each_row.library_number + "--" + each_row.sample_names + ".R1.raw.fastq.gz"
                    os.rename(os.path.join(dir_name_path, fq), os.path.join(dir_name_path, new_name))
                    old_new[fq] = new_name
                elif fq.endswith("R2_001.fastq.gz"):
                    new_name = each_row.library_number + "--" + each_row.sample_names + ".R2.raw.fastq.gz"
                    os.rename(os.path.join(dir_name_path, fq), os.path.join(dir_name_path, new_name))
                    old_new[fq] = new_name
                else:
                    pass
            md5sum_path = os.path.join(dir_name_path, "md5sum.txt")
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
              

parser = argparse.ArgumentParser(description="重命名纯文库文件")
parser.add_argument("-s", "--self_library_info", required=True)
parser.add_argument("-i", "--indir", required=True)
args = vars(parser.parse_args())
rename_self_library(args["self_library_info"], args["indir"])
