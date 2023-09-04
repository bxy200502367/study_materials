# -*- coding:utf-8 -*-
"""
Last-edit: 2023/06/03
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import glob
import os


def merge_valid_stat(indir: str, outfile: str) -> None:
    """
    获取sample_primer配置信息
    """
    stat_files = glob.glob(os.path.join(indir, "*.part_*.raw.valid.stat"))
    total_raw_num, total_chimeric_num, total_no_f_barcode_num, total_no_r_barcode_num, total_valid_num, total_rate = 0, 0, 0, 0, 0, 0
    for file in stat_files:
        with open(file, "r") as f:
            stat_info = f.read().split("\n")[1]
            raw_num, chimeric_num, no_f_barcode_num, no_r_barcode_num, valid_num, rate = stat_info.split("\t")
            total_raw_num += int(raw_num)
            total_chimeric_num += int(chimeric_num)
            total_no_f_barcode_num += int(no_f_barcode_num)
            total_no_r_barcode_num += int(no_r_barcode_num)
            total_valid_num += int(valid_num)
        total_rate = round(total_valid_num/total_raw_num, 4)
    with open(outfile, "w") as w:
        header_list = ["#RawNum", "ChimericNum", "NoFbarcodeNum", "NoRbarcodeNum", "ValidNum", "Rate"]
        line_list = [str(total_raw_num), str(total_chimeric_num), str(total_no_f_barcode_num), str(total_no_r_barcode_num), str(total_valid_num), str(total_rate)]
        w.write("\t".join(header_list))
        w.write("\n")
        w.write("\t".join(line_list))
        w.write("\n")

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="合并valid_stat文件")
    parse.add_argument("-i", "--indir", help="indir", required=True)
    parse.add_argument("-o", "--outfile", help="输出文件", required=True)
    args = parse.parse_args()
    merge_valid_stat(args.indir, args.outfile)
