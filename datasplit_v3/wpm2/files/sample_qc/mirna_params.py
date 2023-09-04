# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/06/30
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.core.exceptions import FileError
from biocluster.iofile import File
import os
import json


class MirnaParamsFile(File):
    """
    name: mirna_params
    Description: |
        mirna质控参数File类
    """
    def __init__(self):
        super(MirnaParamsFile, self).__init__()

    def check(self):
        if super(MirnaParamsFile, self).check():
            if not os.path.exists(self.prop["path"]):
                raise FileError("{}文件不存在".format(self.prop["path"]))
            self.dump_json()
            return True
        return False

    def dump_json(self):
        """
        解析json文件
        """
        f = open(self.prop["path"], "rb")
        try:
            json_dict = json.loads(f.read())
            if json_dict:
                self.set_property("length", json_dict["fastx_clipper"]["l"])
                self.set_property("adapter", json_dict["fastx_clipper"]["adapter"])
                self.set_property("phred_score", json_dict["dynamix_trim"]["n"])
            else:
                self.set_property("length", None)
                self.set_property("adapter", None)
                self.set_property("phred_score", None)
        except:
            raise FileError("json: %s格式不正确" % self.prop["path"])
        f.close()

if __name__ == "__main__":
    a = MirnaParamsFile()
    a.set_path("/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/to_file/sample_qc_params_dir/rna.json")
