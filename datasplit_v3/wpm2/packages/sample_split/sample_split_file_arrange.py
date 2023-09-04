# -*- coding:utf-8 -*-
"""
Last-edit: 2023/06/04
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import os
import shutil

def make_dirs(indir: str) -> None:
    if os.path.exists(indir):
        pass
    else:
        os.makedirs(indir)

def file_arrange_sample_result(indir: str, outdir: str) -> None:
    """
    整理二拆结果文件
    """
    #indir = "/mnt/clustre/users/sanger-dev/wpm2/workspace/20230604/SampleSplit_CF15-20230530PE300-P2-N2_20230604_test3-xu/ParallelMeta/output/"
    dir_list = [dir for dir in os.listdir(indir) if os.path.isdir(os.path.join(indir, dir))]
    new_sample_raw_data = os.path.join(outdir, "meta", "meta_raw_data")
    new_sample_clean_data = os.path.join(outdir, "meta", "meta_clean_data")
    new_sample_stat_info = os.path.join(outdir, "library_stat_info")
    make_dirs(new_sample_raw_data)
    make_dirs(new_sample_clean_data)
    make_dirs(new_sample_stat_info)
    for dir in dir_list:
        library_result_dir = os.path.join(indir, dir)
        sample_raw_data = os.path.join(library_result_dir, "08.raw_data")
        sample_clean_data = os.path.join(library_result_dir, "09.clean_data")
        sample_stat_info = os.path.join(library_result_dir, "10.stat_info")
        for file in os.listdir(sample_raw_data):
            old_file = os.path.join(sample_raw_data, file)
            new_file = os.path.join(new_sample_raw_data, file)
            shutil.copyfile(old_file, new_file)
        for file in os.listdir(sample_clean_data):
            old_file = os.path.join(sample_clean_data, file)
            new_file = os.path.join(new_sample_clean_data, file)
            shutil.copyfile(old_file, new_file)
        for file in os.listdir(sample_stat_info):
            old_file = os.path.join(sample_stat_info, file)
            new_file = os.path.join(new_sample_stat_info, file)
            shutil.copyfile(old_file, new_file)
    with open(os.path.join(outdir, "raw_meta_fastq_list.xls"), "w") as m:
        for file in os.listdir(new_sample_raw_data):
            if file.endswith(".R1.raw.fastq.gz"):
                file_name = file.replace(".R1.raw.fastq.gz", "")
                file_path = os.path.join(new_sample_raw_data, file)
                line_list = [file_name, file_path]
                m.write("\t".join(line_list))
                m.write("\n")
            elif file.endswith(".R1.fastq.gz"):
                print(file)
                file_name = file.replace(".R1.fastq.gz", "")
                file_path = os.path.join(new_sample_raw_data, file)
                line_list = [file_name, file_path]
                m.write("\t".join(line_list))
                m.write("\n")
            else:
                continue
    with open(os.path.join(outdir, "clean_meta_fastq_list.xls"), "w") as n:
        for file in os.listdir(new_sample_clean_data):
            if file.endswith(".fastq.gz"):
                file_name = file.replace(".fastq.gz", "")
                file_path = os.path.join(new_sample_clean_data, file)
                line_list = [file_name, file_path]
                n.write("\t".join(line_list))
                n.write("\n")
            elif file.endswith(".fq.gz"):
                file_name = file.replace(".fq.gz", "")
                file_path = os.path.join(new_sample_clean_data, file)
                line_list = [file_name, file_path]
                n.write("\t".join(line_list))
                n.write("\n")
            else:
                continue
        
        
if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="整理二拆结果文件")
    parse.add_argument("-c", "--indir", help="要整理的文件夹", required=True)
    parse.add_argument("-i", "--outdir", help="输出结果文件夹", required=True)
    args = parse.parse_args()
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    file_arrange_sample_result(args.indir, args.outdir)
