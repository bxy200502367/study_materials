# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/06/14
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import argparse
import os
import csv
from collections import namedtuple
import pathlib
import json

def generate_empty_fastq_sample_split(indir: str, sample_primer_json: str, mode: str) -> None:
    """
    如果如果二拆没有样本，则生成空文件
    """
    with open(sample_primer_json, "r") as f:
        sample_primer_dict = json.load(f)
    library_dir_expect_list = []
    for sample_info, primer_info in sample_primer_dict.items():
        library_dir_expect_list.append(sample_info + "." + primer_info)
    library_dir_exist_list = os.listdir(indir)
    library_dir_exist_set = set([i.replace(".R1.raw.fastq.gz", "").replace(".R2.raw.fastq.gz", "") for i in library_dir_exist_list])
    diff_list = list(set(library_dir_expect_list) - library_dir_exist_set)
    if diff_list:
        for sample_name in diff_list:
            if mode == "raw":
                library_dir_diff_r1 = os.path.join(indir, sample_name + ".R1.raw.fastq.gz")
                library_dir_diff_r2 = os.path.join(indir, sample_name + ".R2.raw.fastq.gz")
                if os.path.exists(library_dir_diff_r1) and os.path.exists(library_dir_diff_r2):
                    continue
                else:
                    pathlib.Path(library_dir_diff_r1).touch()
                    pathlib.Path(library_dir_diff_r2).touch()
            elif mode == "clean":
                library_dir_diff = os.path.join(indir, sample_name + ".fastq.gz")
                if os.path.exists(library_dir_diff):
                    continue
                else:
                    pathlib.Path(library_dir_diff).touch()
            else:
                raise Exception("mode有问题")
    else:
        pass
        

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="如果如果二拆没有样本，则生成空文件")
    parse.add_argument("-i", "--indir", help="文库拆分结果文件夹", required=True)
    parse.add_argument("-l", "--sample_primer_json", help="输入的sample_primer_json文件", required=True)
    parse.add_argument("-m", "--mode", help="raw还是clean", required=True)
    args = parse.parse_args()
    generate_empty_fastq_sample_split(args.indir, args.sample_primer_json, args.mode)
