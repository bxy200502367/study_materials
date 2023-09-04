# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/08/07
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

"""
获取barcode和primer的配置文件
"""

import argparse

def get_meta_config(f_barcode: str, r_barcode: str, link_primer: str, reverse_primer: str, sample_name: str, outfile: str) -> None:
    with open(outfile, "w") as w:
        header_list = ["Sample", "F-barcode", "Linkprimer",	"R-barcode", "ReversePrimer"]
        w.write("\t".join(header_list))
        w.write("\n")
        line_list = [sample_name, f_barcode, link_primer, r_barcode, reverse_primer]
        w.write("\t".join(line_list))
        w.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="拆分完的结果改名")
    parser.add_argument("-f", "--f_barcode", help="f端barcode序列", required=True)
    parser.add_argument("-r", "--r_barcode", help="r端barcode序列", required=True)
    parser.add_argument("-l", "--link_primer", help="link_primer序列", required=True)
    parser.add_argument("-v", "--reverse_primer", help="reverse_primer序列", required=True)
    parser.add_argument("-s", "--sample_name", help="样本名称", required=True)
    parser.add_argument("-o", "--outfile", help="结果文件", required=True)
    args = vars(parser.parse_args())
    get_meta_config(args["f_barcode"], args["r_barcode"], args["link_primer"], args["reverse_primer"], args["sample_name"], args["outfile"])
