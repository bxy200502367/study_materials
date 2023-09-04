# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/23
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import os
import pandas as pd
import shutil

def pretreatment_sample_info(infile: str, outdir: str) -> None:
    """
    将sample_info拆成多个文件
    """
    #infile = "/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/sample_split/test/specimen_info_list.xls"
    #outdir = "/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/sample_split/test"
    sample_info_df = pd.read_csv(infile, sep="\t", encoding="utf-8")
    no_meta = sample_info_df[sample_info_df['meta_type']=="no_meta"]
    no_meta_file = os.path.join(outdir, "no_meta_info.xls")
    no_meta.to_csv(no_meta_file, index=False, header=True, sep="\t")
    meta_official = sample_info_df[sample_info_df['meta_type']=="official"]
    meta_official_file = os.path.join(outdir, "meta_official_info.xls")
    if not meta_official.empty:
        meta_official_dir = os.path.join(outdir, "meta_official")
        if os.path.exists(meta_official_dir):
            shutil.rmtree(meta_official_dir)
        os.mkdir(meta_official_dir)
        groups = meta_official.groupby(["lane_name", "library_number"])
        for group_key, group_value in groups:
            group = groups.get_group(group_key)
            outfile = os.path.join(meta_official_dir, "{}--{}.official_meta_info.xls".format(group_key[0],group_key[1]))
            group.to_csv(outfile, index=False, header=True, sep="\t")
    else:
        pass
    meta_official.to_csv(meta_official_file, index=False, header=True, sep="\t")
    meta_no_official = sample_info_df[sample_info_df['meta_type']=="no_official"]
    meta_no_official_file = os.path.join(outdir, "meta_no_official_info.xls")
    if not meta_no_official.empty:
        meta_no_official_dir = os.path.join(outdir, "meta_no_official")
        if os.path.exists(meta_no_official_dir):
            shutil.rmtree(meta_no_official_dir)
        os.mkdir(meta_no_official_dir)
        groups = meta_no_official.groupby(["lane_name", "library_number"])
        for group_key, group_value in groups:
            group = groups.get_group(group_key)
            outfile = os.path.join(meta_no_official_dir, "{}--{}.no_official_meta_info.xls".format(group_key[0],group_key[1]))
            group.to_csv(outfile, index=False, header=True, sep="\t")
    else:
        pass
    meta_no_official.to_csv(meta_no_official_file, index=False, header=True, sep="\t")

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="处理二拆的信息文件")
    parse.add_argument("-i", "--infile", help="输入文件", required=True)
    parse.add_argument("-o", "--outdir", help="输出文件夹", required=True)
    args = parse.parse_args()
    pretreatment_sample_info(args.infile, args.outdir)
