# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/22
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


import csv
from collections import namedtuple
import os
import glob
import re
from biocluster.iofile import Directory
from biocluster.core.exceptions import FileError


class SampleQcInfoDirFile(Directory):
    """
    空检查，用于指定infile类型的文件夹
    """
    def check(self):
        if super(SampleQcInfoDirFile, self).check():
            self.is_dir()
            rna_sample_dict = self.get_rna_sample_dict()
            self.set_property("rna_sample_dict", rna_sample_dict)
            return True

    def is_dir(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isdir(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))

    def get_rna_sample_dict(self):
        """
        检索文件夹下是否存在rna.qc_info.xls
        """
        rna_sample_dict = {}
        if os.path.exists(os.path.join(self.path, "rna.qc_info.xls")):
            rna_sample_qc_info_file = os.path.join(self.path, "rna.qc_info.xls")
            self.set_property("has_rna", "yes")
            with open(rna_sample_qc_info_file, "r") as f:
                f_csv = csv.reader(f, delimiter="\t")
                headers = next(f_csv)
                rna_info_nt = namedtuple('rna_info_nt', headers)
                for row in f_csv:
                    each_row = rna_info_nt(*row)
                    sample_id = each_row.specimen_id + "--" + each_row.library_number + "--" + each_row.specimen_name + "--" + each_row.majorbio_name
                    fastq_r1_path, fastq_r2_path = each_row.work_path.split(";")
                    if os.path.exists(fastq_r1_path) and os.path.exists(fastq_r2_path):
                        pair_path = each_row.work_path
                    else:
                        pair_path = each_row.raw_path
                    rna_sample_dict[sample_id] = pair_path
        else:
            self.set_property("has_rna", "no")
        return rna_sample_dict
    
    def get_dna_sample_dict(self):
        """
        检索文件夹下是否存在dna.qc_info.xls
        """
        dna_sample_dict = {}
        if os.path.exists(os.path.join(self.path, "dna.qc_info.xls")):
            dna_sample_qc_info_file = os.path.join(self.path, "dna.qc_info.xls")
            self.set_property("has_dna", "yes")
            with open(dna_sample_qc_info_file, "r") as f:
                f_csv = csv.reader(f, delimiter="\t")
                headers = next(f_csv)
                dna_info_nt = namedtuple('dna_info_nt', headers)
                for row in f_csv:
                    each_row = dna_info_nt(*row)
                    sample_id = each_row.specimen_id + "--" + each_row.library_number + "--" + each_row.specimen_name + "--" + each_row.majorbio_name
                    fastq_r1_path, fastq_r2_path = each_row.work_path.split(";")
                    if os.path.exists(fastq_r1_path) and os.path.exists(fastq_r2_path):
                        pair_path = each_row.work_path
                    else:
                        pair_path = each_row.raw_path
                    dna_sample_dict[sample_id] = pair_path
        else:
            self.set_property("has_dna", "no")
        return dna_sample_dict
    
    def get_meta_genomic_sample_dict(self):
        """
        检索文件夹下是
        """   
        
    

if __name__ == "__main__":
    a = SampleQcInfoDirFile()
        