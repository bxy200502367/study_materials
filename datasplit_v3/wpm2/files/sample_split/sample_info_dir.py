# !usr/bin/python
# -*- coding: utf-8 -*-
"""
Last-edit: 2023/5/14
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


class SampleInfoDirFile(Directory):
    """
    空检查，用于指定infile类型的文件夹
    """
    def check(self):
        if super(SampleInfoDirFile, self).check():
            self.is_dir()
            meta_official_dict = self.get_meta_official_dict()
            meta_no_official_dict = self.get_meta_no_official_dict()
            self.set_property("meta_official_dict", meta_official_dict)
            self.set_property("meta_no_official_dict", meta_no_official_dict)
            if meta_official_dict:
                self.set_property("has_meta_official", "yes")
            else:
                self.set_property("has_meta_official", "no")
            if meta_no_official_dict:
                self.set_property("has_meta_no_official", "yes")
            else:
                self.set_property("has_meta_no_official", "no")
            return True

    def is_dir(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isdir(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))

    def get_meta_official_dict(self):
        """
        检索文件夹下的所有官方多样性文库文件并返回
        """
        meta_official_dict = {}
        pattern1 = r"(.*).official_meta_info.xls$"
        file_list = glob.glob(self.path + "meta_official/*")
        for file in file_list:
            match_obj = re.search(pattern1, file)
            if match_obj:
                meta_official_dict[os.path.basename(match_obj.group(1))] = match_obj.group(0)
        return meta_official_dict
    
    def get_meta_no_official_dict(self):
        """
        检索文件夹下的所有官方多样性文库文件并返回
        """
        meta_no_official_dict = {}
        pattern2 = r"(.*).no_official_meta_info.xls$"
        file_list = glob.glob(self.path + "meta_no_official/*")
        for file in file_list:
            match_obj = re.search(pattern2, file)
            if match_obj:
                meta_no_official_dict[os.path.basename(match_obj.group(1))] = match_obj.group(0)
        return meta_no_official_dict

if __name__ == "__main__":
    a = SampleInfoDirFile()
    a.set_path("/mnt/clustre/users/sanger-dev/wpm2/workspace/20230531/SampleSplit_sample_split-20230531_test1/output/sample_split_info/")
    print a.check()
    print a.prop["path"]
    print a.prop["meta_official_dict"]
    print a.prop["meta_no_official_dict"]
    print a.prop["has_meta_official"]
    print a.prop["has_meta_no_official"]
        