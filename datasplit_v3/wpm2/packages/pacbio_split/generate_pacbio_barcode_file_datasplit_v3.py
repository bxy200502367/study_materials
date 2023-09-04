# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230209
# last_modified: 20230209

"""
生成barcode.fasta
"""

import argparse
from itertools import islice


def generate_pacbio_barcode_file(infile: str, outfile: str) -> None:
    with open(infile, "r", encoding='utf-8') as f, open(outfile, "w", encoding="utf-8") as w:
        barcode_dict = {}
        for line in islice(f, 1, None):
            line_list = line.split("\t")
            if len(line_list) == 16:
                cell_name, majorbio_name, sample_name, barcode_name, data_type, type, project_type, f_name, r_name, \
                f_barcode, r_barcode, primer_name, primer_f_base, primer_r_base, primer_length, primer_range = line_list
                if f_name in barcode_dict:
                    if barcode_dict[f_name] == f_barcode:
                        pass
                    else:
                        raise Exception("barcode:{}重复且序列不一样{}:{}".format(f_name, barcode_dict[f_name], f_barcode))
                else:
                    barcode_dict[f_name] = f_barcode
                if r_name in barcode_dict:
                    if barcode_dict[r_name] == r_barcode:
                        pass
                    else:
                        raise Exception("barcode:{}重复且序列不一样{}:{}".format(f_name, barcode_dict[r_name], r_barcode))
                else:
                    barcode_dict[r_name] = r_barcode
            else:
                raise Exception("sample_sheet.txt不为16列,所以报错")
        print(barcode_dict)
        for barcode_name, barcode_seq in sorted(barcode_dict.items(), key=lambda item: item[0]):
            w.write(">{}\n".format(barcode_name))
            w.write("{}\n".format(barcode_seq))


parser = argparse.ArgumentParser(description="生成拆分任务的barcode文件")
parser.add_argument("-i", "--infile", required=True)
parser.add_argument("-o", "--outfile", required=True)
args = vars(parser.parse_args())
generate_pacbio_barcode_file(args["infile"], args["outfile"])
