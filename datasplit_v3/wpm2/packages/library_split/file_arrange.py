# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/16
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import os
import shutil


def file_arrange_library_result(indir: str, outdir: str) -> None:
    """
    整理一拆结果文件
    """
    dir_list = [dir for dir in os.listdir(indir) if os.path.isdir(os.path.join(indir, dir))]
    for dir in dir_list:
        new_dir = os.path.join(outdir, dir)
        if os.path.exists(new_dir):
            shutil.rmtree(new_dir)
        else:
            os.makedirs(new_dir)
        old_fastq_dir = os.path.join(indir, dir, "Fastq")
        new_fastq_dir = os.path.join(outdir, dir)
        for dir2 in os.listdir(old_fastq_dir):
            old_library_dir = os.path.join(old_fastq_dir, dir2)
            new_library_dir = os.path.join(new_fastq_dir, dir2)
            shutil.copytree(old_library_dir, new_library_dir, copy_function=os.link)
        

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="整理一拆结果文件")
    parse.add_argument("-c", "--indir", help="要整理的文件夹", required=True)
    parse.add_argument("-i", "--outdir", help="输出结果文件夹", required=True)
    args = parse.parse_args()
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    file_arrange_library_result(args.indir, args.outdir)
