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


class LibraryInfoDirFile(Directory):
    """
    空检查，用于指定infile类型的文件夹
    """

    def check(self):
        if super(LibraryInfoDirFile, self).check():
            self.is_dir()
            lane_dict = self.get_lane_dict()
            self.set_property("lane_dict", lane_dict)
            return True

    def is_dir(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isdir(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))

    def get_lane_dict(self):
        """
        检索文件夹下的所有lane_match信息并返回
        """
        lane_dict = {}
        pattern1 = r"(.*).library_info.xls$"
        file_list = glob.glob(self.path + "/*")
        for file in file_list:
            match_obj = re.search(pattern1, file)
            if match_obj:
                self.check_library_info(file)
                lane_dict[os.path.basename(match_obj.group(1))] = match_obj.group(1)
        return lane_dict

    def check_library_info(self, library_info_file):
        index_dict = {}
        with open(library_info_file, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            library_info_nt = namedtuple('library_info_nt', headers)
            for row in f_csv:
                each_row = library_info_nt(*row)
                if each_row.index_id in index_dict.keys():
                    raise FileError("一拆文库的index信息重复,重复的index为 {}".format(each_row.index_id))
                index_dict[each_row.index_id] = each_row.index
        return True
                        
                
        
        