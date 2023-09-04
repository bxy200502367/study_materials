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

class DataReleaseInfoFile(File):
    """
    name: data_release_info
    Description: |
        多列，以制表符分隔
    Props:
        one_sample_dict: 样品路径字典，样本名为键，raw_path1和raw_path2元组为值
        tuple_number: 元组数量
    """
    def check(self):
        if super(DataReleaseInfoFile, self).check():
            self.get_info()
            return True
        return False

    def get_info(self):
        super(DataReleaseInfoFile, self).get_info()
        data_release_info_dict = self.check_data_release_info_dict()
        self.set_property("data_release_info_dict", data_release_info_dict)
        self.set_property("tuple_number", len(data_release_info_dict))

    def check_data_release_info_dict(self):
        """
        检查函数
        """
        data_release_info_dict = {}
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            data_release_info_nt = namedtuple('data_release_info_nt', headers)
            for row in f_csv:
                each_row = data_release_info_nt(*row)
                if len(each_row.raw_path.split(";")) == 2:
                    r1_raw_path, r2_raw_path = each_row.raw_path.split(";")
                    self.set_property("r1_raw_path", r1_raw_path)
                    self.set_property("r2_raw_path", r2_raw_path)
                elif len(each_row.raw_path.split(";")) ==1:
                    r1_raw_path = each_row.raw_path
                    r2_raw_path = None
                    self.set_property("r1_raw_path", r1_raw_path)
                    self.set_property("r2_raw_path", r2_raw_path)
                else:
                    raise("有超过两个样本的fastq文件")
                data_release_info_dict.setdefault(each_row.release_specimen_id, []).append((r1_raw_path, r2_raw_path))
        return data_release_info_dict

if __name__ == "__main__":
    a = DataReleaseInfoFile()
    a.set_path("/mnt/lustre/users/sanger-dev/sg-users/yuan.xu/majorbio_test/data_release/to_file/MJ20230401025_SJ2023070600008.data_release_info.xls")
    print a.check()
    print a.prop["path"]
    print a.prop["data_release_info_dict"]
    print a.prop["tuple_number"]