# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/28
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


"""获取多样性的原始fastq"""
import os
import re
import argparse

"""
20230603:增加对#注释的兼容
"""

def get_raw_seq(fastq_r1: str, fastq_r2: str, seq2sam: str, outdir: str) -> None:
    seq_sample_dict = {}
    sample_list = []
    with open(seq2sam, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            elif line.startswith("@"):
                line_list = line.strip().split("\t")
                if len(line_list) == 2:
                    sequence_name, sample_name = line_list
                    seq_sample_dict[sequence_name] = sample_name
                    if sample_name not in sample_list:
                        sample_list.append(sample_name)
                else:
                    raise Exception("seq2sam文件不是两列")
            else:
                raise Exception("seq2sam文件有问题")
    fastq_r1_files = {}
    fastq_r2_files = {}
    for sample in sample_list:
        fastq_r1_files[sample] = open(os.path.join(outdir, sample + ".R1.raw.fastq"), "w")
        fastq_r2_files[sample] = open(os.path.join(outdir, sample + ".R2.raw.fastq"), "w")
    with open(fastq_r1, "r") as fastq1:
        for line in fastq1:
            seq_id = line.split(" ")[0]
            if seq_id in seq_sample_dict:
                sample = seq_sample_dict[seq_id]
                fastq_r1_files[sample].write("{}{}{}{}".format(line, next(fastq1), next(fastq1), next(fastq1)))
    with open(fastq_r2, "r") as fastq2:
        for line in fastq2:
            seq_id = line.split(" ")[0]
            if seq_id in seq_sample_dict:
                sample = seq_sample_dict[seq_id]
                fastq_r2_files[sample].write("{}{}{}{}".format(line, next(fastq2), next(fastq2), next(fastq2)))
    for sample in sample_list:
        fastq_r1_files[sample].close()
        fastq_r2_files[sample].close()


parser = argparse.ArgumentParser(description="获取多样性的原始fastq")
parser.add_argument("-i", "--fastq_r1", required=True)
parser.add_argument("-j", "--fastq_r2", required=True)
parser.add_argument("-s", "--seq2sam", required=True)
parser.add_argument("-o", "--outdir", required=True)
args = vars(parser.parse_args())

get_raw_seq(args["fastq_r1"], args["fastq_r2"], args["seq2sam"], args["outdir"])

