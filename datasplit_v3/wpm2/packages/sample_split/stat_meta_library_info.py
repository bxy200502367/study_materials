# -*- coding:utf-8 -*-
"""
Last-edit: 2023/06/01
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import csv
from collections import namedtuple
from itertools import islice
import json
import re
import os
#import time
#start = time.perf_counter()
#end = time.perf_counter()
#runTime = end - start

def stat_meta_library_info(library_number: str, valid_stat_file: str, flash_log_file: str, fastp_json: str, split_fastq: str, qc_stat: str) -> None:
    """
    统计多样性文库信息
    """
    trim_num, q20_rate, q30_rate, r1_reads, rank = 0, 0, 0, 0, "D"
    if os.path.exists(fastp_json):
        with open(fastp_json, "r") as f:
            json_dict = json.loads(f.read())
        r1_base = int(json_dict["read1_before_filtering"]["total_bases"])
        r2_base = int(json_dict["read2_before_filtering"]["total_bases"])
        q20_r1 = float(json_dict["read1_before_filtering"]["q20_bases"])
        q30_r1 = float(json_dict["read1_before_filtering"]["q30_bases"])
        q20_r2 = float(json_dict["read2_before_filtering"]["q20_bases"])
        q30_r2 = float(json_dict["read2_before_filtering"]["q30_bases"])
        trim_num = int(json_dict["read1_after_filtering"]["total_reads"])
        q20_rate = round((q20_r1 + q20_r2) / (r1_base + r2_base), 4) if r1_base + r2_base != 0 else 0
        q30_rate = round((q30_r1 + q30_r2) / (r1_base + r2_base), 4) if r1_base + r2_base != 0 else 0
        r1_reads = int(json_dict["read1_before_filtering"]["total_reads"])
        if q20_rate >= 0.95:
            rank = "A"
        elif q20_rate >= 0.85:
            rank = "B"
        elif q20_rate >= 0.75:
            rank = "C"
        else:
            rank = "D"
    raw_num, chimeric_num, raw_valid_num, chimeric_rate, raw_valid_rate = 0, 0, 0, 0, 0
    if os.path.exists(valid_stat_file):
        with open(valid_stat_file, "r") as f:
            for line in islice(f, 1, None):
                item = line.strip().split("\t")
                raw_num = int(item[0])
                chimeric_num = int(item[1])
                raw_valid_num = int(item[4])
                chimeric_rate = round(float(chimeric_num) / raw_num, 4) if raw_num !=0 else 0
                raw_valid_rate = round(float(raw_valid_num) / raw_num, 4) if raw_num !=0 else 0
    else:
        raw_num = r1_reads
        raw_valid_num = r1_reads
    merge_num = 0
    if os.path.exists(flash_log_file):
        with open(flash_log_file, "r") as f:
            for line in f:
                if re.search("Combined pairs:", line):
                    num = re.findall("\d+", line)
                    if len(num) > 0:
                        merge_num = int(num[0])
                    break
    else:
        merge_num = trim_num
    split_num = 0
    if os.path.exists(split_fastq) or os.path.getsize(split_fastq):
        count = -1
        with open(split_fastq, "rb") as f:
            for count, line in enumerate(f):
                pass
            count+=1
            split_num = int(count / 4)
    trim_rate, merge_rate, split_rate, high_quality_rate = 0, 0, 0, 0
    if raw_valid_num != 0:
        trim_rate = round(float(trim_num) / raw_valid_num, 4)
        merge_rate = round(float(merge_num) / trim_num, 4)
    if merge_num != 0:
        split_rate = round(float(split_num) / merge_num, 4)
    if raw_num != 0:
        high_quality_rate = round(float(split_num) / raw_num, 4)
    with open(qc_stat, "w") as w:
        w.write("#Lib\tRank\tQ20\tQ30\tRaw_pair\tchimeric\tchimeric_rate\tvalid_pair\tvalid_rate\t")
        w.write("Pair_trim\tTrim_rate\tPair_merge\tmerge_rate\tSeq_split\tSplit_rate\thighQuality_rate\n")
        w.write(library_number + "\t" + rank + "\t" + str(q20_rate) + "\t" + str(q30_rate) + "\t" + str(raw_num) + "\t")
        w.write(str(chimeric_num) + "\t" + str(chimeric_rate) + "\t" + str(raw_valid_num) + "\t" + str(raw_valid_rate) + "\t")
        w.write(str(trim_num) + "\t"+ str(trim_rate) + "\t" + str(merge_num) + "\t" + str(merge_rate) + "\t" + str(split_num) + "\t")
        w.write(str(split_rate) + "\t" + str(high_quality_rate) + "\n")


if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="生成多样性文库拆分的统计表")
    parse.add_argument("-l", "--library_number", help="文库名字", required=True)
    parse.add_argument("-v", "--valid_stat_file", help="valid统计文件", required=True)
    parse.add_argument("-f", "--flash_log_file", help="flash日志文件",required=True)
    parse.add_argument("-j", "--fastp_json", help="质控完json文件",required=True)
    parse.add_argument("-s", "--split_fastq", help="split的fastq文件",required=True)
    parse.add_argument("-q", "--qc_stat", help="统计结果",required=True)
    args = parse.parse_args()
    stat_meta_library_info(args.library_number, args.valid_stat_file, args.flash_log_file, args.fastp_json, args.split_fastq,
                           args.qc_stat)
