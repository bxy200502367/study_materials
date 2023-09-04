# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/22
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import argparse
import os
import pandas as pd

def split_sample_qc_info(infile: str, outdir: str) -> None:
    """
    将sample_qc_info拆成多个文件
    """
    #infile = "/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/to_file/sample_qc_info_list.xls"
    #infile = "/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/sample_qc_info_list.xls"
    #outdir = "/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/sample_split/test"
    sample_qc_info_df = pd.read_csv(infile, sep="\t", encoding="utf-8")
    if not sample_qc_info_df.empty:
        product_type_list = list(sample_qc_info_df["product_type"].drop_duplicates())
        for i in product_type_list:
            sample_qc_info_one_df = sample_qc_info_df[sample_qc_info_df["product_type"]==i]
            outfile = os.path.join(outdir, "{}.qc_info.xls".format(i))
            sample_qc_info_one_df.to_csv(outfile, index=False, header=True, sep="\t")
    else:
        pass

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="拆分质控的信息文件")
    parse.add_argument("-i", "--infile", help="输入文件", required=True)
    parse.add_argument("-o", "--outdir", help="输出文件夹", required=True)
    args = parse.parse_args()
    split_sample_qc_info(args.infile, args.outdir)
