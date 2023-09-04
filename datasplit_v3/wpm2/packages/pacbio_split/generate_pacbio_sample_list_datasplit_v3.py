# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230209
# last_modified: 20230209

"""
生成sample_list.txt
"""

import argparse
from itertools import islice


def generate_pacbio_sample_list(infile: str, outfile: str) -> None:
    with open(infile, "r", encoding='utf-8') as f, open(outfile, "w", encoding="utf-8") as w:
        for line in islice(f, 1, None):
            line_list = line.split("\t")
            if len(line_list) == 16:
                cell_name, majorbio_name, sample_name, barcode_name, data_type, type, project_type, f_name, r_name, \
                f_barcode, r_barcode, primer_name, primer_f_base, primer_r_base, primer_length, primer_range = line_list
                new_line_list = [majorbio_name, sample_name, barcode_name, f_name, r_name, project_type, primer_name,
                                primer_f_base, primer_r_base, primer_range]
                w.write("\t".join(new_line_list))
            else:
                raise Exception("sample_sheet.txt不为16列,所以报错")


parser = argparse.ArgumentParser(description="生成sample_list.txt")
parser.add_argument("-i", "--infile", required=True)
parser.add_argument("-o", "--outfile", required=True)
args = vars(parser.parse_args())
generate_pacbio_sample_list(args["infile"], args["outfile"])
