# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/16
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import os
import csv
from collections import namedtuple
import pathlib

def generate_empty_fastq(indir: str, library_info: str) -> None:
    """
    如果bcl_to_fastq没有拆分出数据,则生成空文件
    """
    library_dir_expect_list = []
    with open(library_info, "r") as f:
        f_csv = csv.reader(f, delimiter="\t")
        headers = next(f_csv)
        library_info_nt = namedtuple('library_info_nt', headers)
        for row in f_csv:
            each_row = library_info_nt(*row)
            library_dir_expect_list.append(each_row.lane_name + "_" + each_row.library_number)
    library_dir_exist_list = os.listdir(indir)
    diff_list = list(set(library_dir_expect_list) - set(library_dir_exist_list))
    if diff_list:
        for dir in diff_list:
            library_dir_diff = os.path.join(indir, dir)
            if os.path.exists(library_dir_diff):
                continue
            else:
                os.makedirs(library_dir_diff)
                r1_fastq = os.path.join(library_dir_diff, dir + ".R1.raw.fastq.gz")
                r2_fastq = os.path.join(library_dir_diff, dir + ".R2.raw.fastq.gz")
                md5sum_file = os.path.join(library_dir_diff, "md5sum.txt")
                pathlib.Path(r1_fastq).touch()
                pathlib.Path(r2_fastq).touch()
                with open(md5sum_file, "w") as w:
                    w.write("d41d8cd98f00b204e9800998ecf8427e  ")
                    w.write(dir + ".R1.raw.fastq.gz\n")
                    w.write("d41d8cd98f00b204e9800998ecf8427e  ")
                    w.write(dir + ".R2.raw.fastq.gz\n")
    else:
        pass
        

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="如果bcl_to_fastq没有拆分出数据,则生成空文件")
    parse.add_argument("-i", "--indir", help="文库拆分结果文件夹", required=True)
    parse.add_argument("-l", "--library_info", help="输入的library_info.xls", required=True)
    args = parse.parse_args()
    generate_empty_fastq(args.indir, args.library_info)
