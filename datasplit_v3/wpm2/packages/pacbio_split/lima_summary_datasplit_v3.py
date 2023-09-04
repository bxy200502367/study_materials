# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230209
# last_modified: 20230209

"""
拆完的bam改名
"""

import argparse


def lima_summary(infile: str, outfile: str) -> None:
    with open(infile, "r", encoding='utf-8') as f, open(outfile, "w", encoding='utf-8') as w:
        header_list = ["ccs_reads", "reconize_reads", "reconize_retio"]
        w.write("\t".join(header_list))
        w.write("\n")
        for line in f:
            if line.startswith("ZMWs input"):
                ccs_reads = line.split(":")[1].strip()
            if line.startswith("ZMWs above all thresholds"):
                reconize_reads = line.split(":")[1].strip().split("(")[0].strip()
                reconize_retio = str(round(int(reconize_reads) / int(ccs_reads), 4))
        new_line_list = [ccs_reads, reconize_reads, reconize_retio]
        w.write("\t".join(new_line_list))
        w.write("\n")


parser = argparse.ArgumentParser(description="lima结果统计")
parser.add_argument("-i", "--infile", required=True)
parser.add_argument("-o", "--outfile", required=True)
args = vars(parser.parse_args())
lima_summary(args["infile"], args["outfile"])
