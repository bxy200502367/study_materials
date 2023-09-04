# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/30
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import csv
from collections import namedtuple

def get_primer_config(infile: str, outfile: str) -> None:
    """
    获取primer配置信息
    """
    with open(infile, "r") as f, open(outfile, "w") as w:
        header_list = ["#Sample", "F-barcode", "LinkPrimer", "R-barcode", "ReversePrimer"]
        w.write("\t".join(header_list))
        w.write("\n")
        f_csv = csv.reader(f, delimiter="\t")
        headers = next(f_csv)
        sample_info_nt = namedtuple('sample_info_nt', headers)
        for row in f_csv:
            each_row = sample_info_nt(*row)
            sample_id_list = [each_row.project_sn, each_row.library_number, each_row.specimen_id, each_row.specimen_name]
            sample_id = "--".join(sample_id_list)
            new_line_list = [sample_id, each_row.f_barcode, each_row.link_primer, each_row.r_barcode, each_row.reverse_primer]
            w.write("\t".join(new_line_list))
            w.write("\n")


if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="生成barcode配置文件")
    parse.add_argument("-i", "--infile", help="输入文件", required=True)
    parse.add_argument("-o", "--outfile", help="输出文件", required=True)
    args = parse.parse_args()
    get_primer_config(args.infile, args.outfile)
