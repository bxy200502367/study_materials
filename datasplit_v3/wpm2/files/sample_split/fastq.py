# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/06/02
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import os
import re
import gzip
import subprocess
from biocluster.iofile import File
from biocluster.core.exceptions import FileError
from biocluster.config import Config

class FastqFile(File):
    """
    主要是下载fastq文件
    并且获取文件的大小
    """

    def check(self):
        if super(FastqFile, self).check():
            self.is_file()
            self.get_info()
            return True
        return False

    def is_file(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isfile(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))
        
    def get_info(self):
        filesize = os.path.getsize(self.path)
        self.set_property("filesize", filesize)
        
    def get_file_name(self):
        basename = os.path.basename(self.path).replace(".fastq.gz", "")
        self.set_property("fastqname", basename)

if __name__=="__main__":
    data=FastqFile()
    data.set_path("/mnt/dlustre/users/sanger/wpm2/workspace/20230530/LibrarySplit_CF4-20230526PE300-P2-N2_20230530_093453/output/library_result/1/230526PE300-P2-N2_MJ230418P_136/MJ230418P_136_S1_L001_R1_001.fastq.gz")
    print data.check()
    print data.prop["path"]
    print data.prop["filesize"]

