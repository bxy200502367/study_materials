# -*- coding: utf-8 -*-
"""
Last-edit: 2022/04/10
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.iofile import File
from biocluster.core.exceptions import FileError
from itertools import islice
import csv
from collections import namedtuple
import os

class OneSampleInfoFile(File):
    """
    name: one_sample_info
    Description: |
        多列，以制表符分隔
    Props:
        one_sample_dict: 样品s3字典，样本名为键，raw_path1和raw_path2元组为值
        tuple_number: 元组数量
        r1_paths_str: 空格分隔的r1列表字符串
        r2_paths_str: 空格分隔的r2列表字符串
        sample_id: 样本的id，也是最后的名字
    """
    def check(self):
        if super(OneSampleInfoFile, self).check():
            self.get_info()
            return True
        return False

    def get_info(self):
        super(OneSampleInfoFile, self).get_info()
        one_sample_dict = self.check_one_sample_info()
        self.set_property("one_sample_dict", one_sample_dict)
        self.set_property("tuple_number", len(*one_sample_dict.values()))
        r1_path_list = []
        r2_path_list = []
        for key, value in one_sample_dict.items():
            for r1_path, r2_path in value:
                r1_path_list.append(r1_path)
                r2_path_list.append(r2_path)
        sample_id = key
        r1_paths_str = " ".join(r1_path_list)
        r2_paths_str = " ".join(r2_path_list)
        self.set_property("sample_id", sample_id)
        self.set_property("r1_paths_str", r1_paths_str)
        self.set_property("r2_paths_str", r2_paths_str)

    def check_one_sample_info(self):
        """
        检查函数
        """
        one_sample_dict = {}
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            sample_info_nt = namedtuple('sample_info_nt', headers)
            for row in f_csv:
                each_row = sample_info_nt(*row)
                sample_id = each_row.library_name + "--" + each_row.majorbio_sn + "--" + each_row.sample_name
                if len(each_row.raw_path.split(";")) == 2:
                    fastq_r1_path, fastq_r2_path = each_row.raw_path.split(";")
                elif len(each_row.work_raw_path.split(";")) ==1:
                    fastq_r1_path = each_row.work_raw_path
                    fastq_r2_path = None
                else:
                    raise("有超过两个样本的fastq文件")
                one_sample_dict.setdefault(sample_id, []).append((fastq_r1_path, fastq_r2_path))
        return one_sample_dict

if __name__ == "__main__":
    a = OneSampleInfoFile()
    a.set_path("/mnt/lustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/test/merge_info_dir/GD48_3.sample_info.xls")
    print a.check()
    print a.prop["path"]
    print a.prop["one_sample_dict"]
    print a.prop["tuple_number"]
    print a.prop["sample_id"]
    print a.prop["r1_paths_str"]
    print a.prop["r2_paths_str"]