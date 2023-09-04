# !usr/bin/python
# -*- coding: utf-8 -*-
"""
Last-edit: 2023/6/02
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


class SplitFastqDirFile(Directory):
    """
    空检查，用于指定infile类型的文件夹
    """
    def check(self):
        if super(SplitFastqDirFile, self).check():
            self.is_dir()
            fastq_name_dict = self.get_fastq_name_dict()
            self.set_property("fastq_name_dict", fastq_name_dict)
            return True
        return False

    def is_dir(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isdir(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))

    def get_fastq_name_dict(self):
        """
        检索文件夹下的所有官方多样性文库文件并返回
        """
        fastq_name_dict = {}
        pattern1 = r"(.*).fastq.gz$"
        file_list = glob.glob(self.path + "/*")
        for file in file_list:
            match_obj = re.search(pattern1, file)
            if match_obj:
                key_id = os.path.basename(match_obj.group(1)).split(".")[-1]
                fastq_name_dict[key_id] = key_id
        return fastq_name_dict
    
if __name__ == "__main__":
    a = SplitFastqDirFile()
    a.set_path("/mnt/clustre/users/sanger-dev/wpm2/workspace/20230602/SampleSplit_CF4-20230526PE300-P2-N2-20230601_test6/ParallelMeta/DatasplitMetaNoOfficial/DatasplitMetaNoOfficialPair/test/")
    print a.check()
    print a.prop["fastq_name_dict"]
        