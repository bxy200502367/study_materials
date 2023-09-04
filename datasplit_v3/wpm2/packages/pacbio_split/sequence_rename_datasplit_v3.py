# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230209
# last_modified: 20230209

"""
拆完的bam改名
"""

import argparse
import pysam

def sequence_rename(fastq_file: str, sample_name: str, outfile: str) -> None:
    index = 0
    sample_name = sample_name.split("--")[3]
    with open(outfile, "w") as w:
        for record in pysam.FastxFile(fastq_file):
            index += 1
            new_sequence_name = "@" + sample_name + "_" + str(index)
            sequence = record.sequence
            sequence_comment = "+"
            sequence_quality = record.quality
            w.write(new_sequence_name + '\n')
            w.write(sequence + '\n')
            w.write(sequence_comment + '\n')
            w.write(sequence_quality + '\n')

parser = argparse.ArgumentParser(description="拆分完的结果改名")
parser.add_argument("-i", "--fastq_file", required=True)
parser.add_argument("-s", "--sample_name", required=True)
parser.add_argument("-o", "--outfile", required=True)
args = vars(parser.parse_args())
sequence_rename(args["fastq_file"], args["sample_name"], args["outfile"])
