# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230209
# last_modified: 20230209

"""
拆完的bam改名
"""

import argparse
import os
import pathlib


def pacbio_rename(sample_list: str, split_dir: str, out_dir: str) -> None:
    with open(sample_list, "r", encoding='utf-8') as f:
        for line in f:
            line_list = line.split("\t")
            if len(line_list) == 10:
                majorbio_name, sample_name, barcode_name, f_name, r_name, product_type, primer_name, \
                forward_primer, reverse_primer, primer_range = line_list
                bam_file = "samples." + f_name + "--" + r_name + ".bam"
                bam_file_path = os.path.join(split_dir, bam_file)
                new_bam_file = majorbio_name + "--" + primer_name + "--" + barcode_name + "--" + sample_name + ".bam"
                new_bam_file_path = os.path.join(out_dir, new_bam_file)
                if os.path.exists(bam_file_path) and os.path.isfile(bam_file_path):
                    os.system('cp {} {}'.format(bam_file_path, new_bam_file_path))
                bam_pbi_file = "samples." + f_name + "--" + r_name + ".bam.pbi"
                bam_pbi_file_path = os.path.join(split_dir, bam_pbi_file)
                new_bam_pbi_file = majorbio_name + "--" + primer_name + "--" + barcode_name + "--" + sample_name + ".bam.pbi"
                new_bam_pbi_file_path = os.path.join(out_dir, new_bam_pbi_file)
                if os.path.exists(bam_pbi_file_path) and os.path.isfile(bam_pbi_file_path):
                    os.system('cp {} {}'.format(bam_pbi_file_path, new_bam_pbi_file_path))
            else:
                raise Exception("sample_list.txt不为10列,所以报错")


parser = argparse.ArgumentParser(description="拆分完的结果改名")
parser.add_argument("-i", "--sample_list", required=True)
parser.add_argument("-s", "--split_dir", required=True)
parser.add_argument("-o", "--out_dir", required=True)
args = vars(parser.parse_args())
pacbio_rename(args["sample_list"], args["split_dir"], args["out_dir"])
