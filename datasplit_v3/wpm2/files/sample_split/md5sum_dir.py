# !usr/bin/python
# -*- coding: utf-8 -*-
"""
Last-edit: 2023/6/05
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


class Md5sumDirFile(Directory):
    """
    空检查，用于指定infile类型的文件夹
    """
    def check(self):
        if super(Md5sumDirFile, self).check():
            self.is_dir()
            self.is_empty()
            return True

    def is_dir(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isdir(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))

    def is_empty(self):
        """
        检索文件夹下的文件
        """
        file_list = glob.glob(self.path + "/*")
        if file_list:
            self.set_property("is_empty", "no")
        else:
            self.set_property("is_empty", "yes")
            
if __name__ == "__main__":
    a = Md5sumDirFile()
