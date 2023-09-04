# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/31
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import argparse
import json
import os 
import pysam


def get_sample_primer(sample_primer_json: str):
    sample_primer_info = {}
    with open(sample_primer_json, "rb") as f:
        sample_primer_info = json.load(f)
    return sample_primer_info

def extract_meta_clean(infile: str, sample_primer_json: str, outdir: str) -> None:
    """
    将一个fastq文件拆分成多个fastq文件
    """
    #infile = "/mnt/clustre/users/sanger-dev/wpm2/workspace/20230522/SampleSplit_CF9-20230519PE300-P1-N2_20230522_152225/MetaQc/SingleMetaQc/SplitByBarcode/output/MJ230515P_70.trim.merge.split.allLen.fq"
    fastq_dict = {}
    sample_primer_info = get_sample_primer(sample_primer_json)
    with pysam.FastxFile(infile) as fin:
        for record in fin:
            new_record_name = record.name.split("--")[-1]
            sample_name = "_".join(new_record_name.split("_")[:-1])
            file_name = "--".join(record.name.split("--")[:-1] + [sample_name])
            line1 = "@" + new_record_name + "\t" + record.comment
            line2 = record.sequence
            if len(line2) < 50:
                continue
            line3 = "+"
            line4 = record.quality
            fastq_dict.setdefault(file_name, []).append((line1, line2, line3, line4))
        for sample, sequences in fastq_dict.items():
            out_fq_file = os.path.join(outdir, sample + "." + sample_primer_info[sample] + ".fastq")
            with open(out_fq_file, "w") as w:
                for one_sequence in sequences:
                    w.write("\n".join(one_sequence))
                    w.write("\n")

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="拆分质控后的fastq")
    parse.add_argument("-i", "--infile", help="输入文件", required=True)
    parse.add_argument("-s", "--sample_primer_json", help="输入的样本和引物对应表", required=True)
    parse.add_argument("-o", "--outdir", help="输出文件夹", required=True)
    args = parse.parse_args()
    extract_meta_clean(args.infile, args.sample_primer_json, args.outdir)
