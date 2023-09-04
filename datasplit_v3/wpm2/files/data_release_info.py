# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/25
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import csv
from collections import namedtuple
import os
import glob
import re
from biocluster.iofile import File
from biocluster.core.exceptions import FileError


class DataReleaseInfoFile(File):
    """
    空检查，用于指定infile类型的文件夹
    """

    def check(self):
        if super(DataReleaseInfoFile, self).check():
            self.is_file()
            sample_dict = self.get_sample_dict()
            self.set_property("sample_dict", sample_dict)
            return True

    def is_dir(self):
        """
        检查传入的参数是否是文件并且判断是否存在
        """
        if not os.path.isfile(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))

    def get_sample_dict(self):
        """
        检查文件中所有的样本信息并返回字典
        """
        sample_dict = {}
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            data_release_info = namedtuple('data_release_info', headers)
            for row in f_csv:
                each_row = data_release_info(*row)
                sample_dict[each_row.sample_name] = each_row.sample_name
        return sample_dict

        