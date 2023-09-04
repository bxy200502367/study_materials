# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/22
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import argparse
import os
import shutil
import pandas as pd

def split_data_release_info(infile: str, qc_dir: str, outdir: str) -> None:
    """
    将data_release_info拆成多个文件
    """
    #infile = "/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/to_file/20230731_test/MJ20220413034_SJ2023073100005.data_release_info.xls"
    #qc_dir = "/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/to_file/20230731_test/sample_qc_params_dir"
    #outdir = "/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/to_file"
    data_release_info_df = pd.read_csv(infile, sep="\t", encoding="utf-8")
    if not data_release_info_df.empty:
        product_type_list = list(data_release_info_df["release_specimen_id"].drop_duplicates())
        for i in product_type_list:
            data_release_one_info_df = data_release_info_df[data_release_info_df["release_specimen_id"]==i]
            outfile = os.path.join(outdir, "{}.data_release_info.xls".format(i))
            data_release_one_info_df.to_csv(outfile, index=False, header=True, sep="\t")
            qc_params_info = os.path.join(qc_dir, i)
            qc_params_outdir = os.path.join(outdir, i)
            shutil.copytree(qc_params_info, qc_params_outdir)
    else:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="拆分data_release_info文件")
    parser.add_argument("-i", "--infile", help="输入文件", required=True)
    parser.add_argument("-s", "--qc_dir", help="输入质控信息文件夹", required=True)
    parser.add_argument("-o", "--outdir", help="输出文件夹", required=True)
    args = parser.parse_args()
    split_data_release_info(args.infile, args.qc_dir, args.outdir)
