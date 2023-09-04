# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/02
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


import argparse
import re

def stat_fastx_clipper(sample_id: str, infile: str, outfile: str) -> None:
    """
    统计fastx_clipper出来的结果.o文件里的信息
    """
    #infile = "/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/to_file/sample_qc_info_list.xls"
    #infile = "/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/sample_qc_info_list.xls"
    #outdir = "/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/sample_split/test"
    with open(infile, "r") as f, open(outfile, "w") as w:
        w.write("Sample\tRaw_reads\tAdapter_only\tN_reads\t<18nt\t>32nt\tClean_reads\tAdapter%\n")
        raw_reads, short_reads, adapter_only, n_reads, less_reads, big_reads, clean_reads = 0, 0, 0, 0, 0, 0, 0
        for line in f:
            if re.match(r"Input", line):
                raw_reads = line.strip().split()[1]
                continue
            if re.match(r"Output", line):
                clean_reads = line.strip().split()[1]
                continue
            if re.match(r"discarded.*too-short reads", line):
                short_reads = line.strip().split()[1]
                continue
            if re.match(r"discarded.*adapter-only reads", line):
                adapter_only = line.strip().split()[1]
                continue
            if re.match(r"discarded.*N reads", line):
                n_reads = line.strip().split()[1]
                continue
            if re.match(r"discarded.*bigger than 32 reads", line):
                big_reads = line.strip().split()[1]
                continue
            if re.match(r"remain.*clean reads", line):
                clean_reads = line.strip().split()[1]
                continue
        adapter_rate = round(float(adapter_only) / int(raw_reads), 4) * 100
        new_line_list = [sample_id, str(raw_reads), str(adapter_only), str(n_reads), str(short_reads), 
                         str(big_reads), str(clean_reads), str(adapter_rate)]
        w.write("\t".join(new_line_list))
        w.write("\n")

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="统计fastx_clipper出来的结果.o文件里的信息")
    parse.add_argument("-s", "--sample_id", help="输入的sample_id", required=True)
    parse.add_argument("-i", "--infile", help="输入文件", required=True)
    parse.add_argument("-o", "--outfile", help="输出文件", required=True)
    args = parse.parse_args()
    stat_fastx_clipper(args.sample_id, args.infile, args.outfile)
