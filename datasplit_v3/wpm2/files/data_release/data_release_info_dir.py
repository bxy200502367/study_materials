# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/24
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import os
import glob
import re
from biocluster.iofile import Directory
from biocluster.core.exceptions import FileError


class DataReleaseInfoDirFile(Directory):
    """
    检查数据释放info文件夹
    """
    def check(self):
        if super(DataReleaseInfoDirFile, self).check():
            self.is_dir()
            data_release_info_dict = self.get_data_release_info_dict()
            self.set_property("data_release_info_dict", data_release_info_dict)
            return True
        return False

    def is_dir(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isdir(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))
        
    def get_data_release_info_dict(self):
        """
        检索文件夹下的释放单并返回
        """
        data_release_info_dict = {}
        pattern = r"(.*).data_release_info.xls$"
        file_list = glob.glob(self.path + "/*")
        for file in file_list:
            match_obj = re.search(pattern, file)
            if match_obj:
                data_release_info_dict[os.path.basename(match_obj.group(1))] = match_obj.group(0)
        return data_release_info_dict

if __name__ == "__main__":
    a = DataReleaseInfoDirFile()
    a.set_path("/mnt/clustre/users/sanger-dev/wpm2/workspace/20230531/SampleSplit_sample_split-20230531_test1/output/sample_split_info/")
    print a.check()
