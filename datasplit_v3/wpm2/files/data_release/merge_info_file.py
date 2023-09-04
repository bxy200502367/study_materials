# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/22
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""



from biocluster.iofile import File
from biocluster.core.exceptions import FileError
import csv
import os
from collections import namedtuple

class OneSampleInfoFile(File):
    """
    name: one_sample_info
    Description: |
        多列，以制表符分隔
    Props:
        one_sample_dict: 样品路径字典，样本名为键，raw_path1和raw_path2元组为值
        tuple_number: 元组数量
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
        self.set_property("tuple_number", len(one_sample_dict))
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
        merge_info_dict = {}
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            merge_info_nt = namedtuple('merge_info_nt', headers)
            for row in f_csv:
                each_row = merge_info_nt(*row)
                if each_row.product_type == "meta":
                    sample_id = "--".join(each_row.lane_name, each_row.library_name, each_row.majorbio_sn, each_row.sample_name, each_row.primer_name)
                else:
                    sample_id = "--".join(each_row.lane_name, each_row.library_name)
                if len(each_row.raw_path.split(";")) == 2:
                    r1_raw_path, r2_raw_path = each_row.raw_path.split(";")
                    self.set_property("r1_path", r1_raw_path)
                    self.set_property("r2_path", r2_raw_path)
                elif len(each_row.raw_path.split(";")) ==1:
                    r1_raw_path = each_row.raw_path
                    r2_raw_path = None
                    self.set_property("r1_path", r1_raw_path)
                    self.set_property("r2_path", r2_raw_path)
                else:
                    raise("raw_path字段中有超过一个的;符号")
                one_sample_dict[sample_id] = (fastq_r1_path, fastq_r2_path)
        return one_sample_dict

if __name__ == "__main__":
    a = OneSampleInfoFile()
    a.set_path("/mnt/clustre/users/sanger-dev/users/yuan.xu/Datasplit_v3/files/one_sample_info/s3_path.txt")
    print a.check()
    print a.prop["path"]
    print a.prop["one_sample_dict"]
    print a.prop["tuple_number"]
    print a.prop["sample_id"]
    print a.prop["r1_paths_str"]
    print a.prop["r2_paths_str"]