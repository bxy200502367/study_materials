# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/31
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import csv
import json
from collections import namedtuple

def get_barcode_primer_json(infile: str, outfile: str) -> None:
    """
    获取sample_primer配置信息
    """
    with open(infile, "r") as f, open(outfile, "w") as w:
        sample_primer_dict = {}
        f_csv = csv.reader(f, delimiter="\t")
        headers = next(f_csv)
        sample_info_nt = namedtuple('sample_info_nt', headers)
        for row in f_csv:
            each_row = sample_info_nt(*row)
            sample_id_list = [each_row.project_sn, each_row.library_number, each_row.specimen_id, each_row.specimen_name]
            sample_id = "--".join(sample_id_list)
            sample_primer_dict[sample_id] = each_row.primer
        w.write(json.dumps(sample_primer_dict) + "\n")

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="生成sample_primer_json配置文件")
    parse.add_argument("-i", "--infile", help="输入文件", required=True)
    parse.add_argument("-o", "--outfile", help="输出文件", required=True)
    args = parse.parse_args()
    get_barcode_primer_json(args.infile, args.outfile)
