# -*- coding: utf-8 -*-
"""
Last-edit: 2023/05/11
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.core.exceptions import FileError
from biocluster.iofile import File
import os
import json


class LibraryParamsFile(File):
    """
    name: library_params
    Description: |
        一拆library_split.json的File类
        json字符串，键有data_path，lane_match，barcode_mismatch，sample_sheet，bases_mask，ignore_error
    Props:
        data_path: bcl文件路径
        lane_match: 匹配的lane
        barcode_mismatch: barcode允许错配数
        sample_sheet: 一拆所需要的sheet文件
        bases_mask: 测序模式
        ignore_error: 是否忽略bcl2fastq中的warning信息
    """
    def __init__(self):
        super(LibraryParamsFile, self).__init__()

    def check(self):
        super(LibraryParamsFile, self).check()
        if not os.path.exists(self.prop["path"]):
            raise FileError("{}文件不存在".format(self.prop["path"]))
        self.dump_json()

    def dump_json(self):
        """
        解析json文件
        """
        f = open(self.prop["path"], "rb")
        try:
            json_dict = json.loads(f.read())
            self.set_property("data_path", json_dict["data_path"])
            self.set_property("lane_match", json_dict["lane_match"])
            self.set_property("barcode_mismatch", json_dict["barcode_mismatch"])
            self.set_property("sample_sheet", json_dict["sample_sheet"])
            self.set_property("bases_mask", json_dict["bases_mask"])
            self.set_property("ignore_error", json_dict["ignore_error"])
        except:
            raise FileError("json: %s格式不正确" % self.prop["path"])


if __name__ == "__main__":
    a = LibraryParamsFile()
    a.set_path("/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/library_split/test/library_info_dir/1.library_split.json")
    print a.check()
    print a.prop["data_path"]
