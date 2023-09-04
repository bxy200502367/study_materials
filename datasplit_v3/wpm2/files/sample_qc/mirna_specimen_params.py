# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/08/02
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.core.exceptions import FileError
from biocluster.iofile import File
import os
import json


class MirnaSpecimenParamsFile(File):
    """
    name: mirna_specimen_params
    Description: |
        mirna质控参数File类(单个样本
    """
    def __init__(self):
        super(MirnaSpecimenParamsFile, self).__init__()

    def check(self):
        if super(MirnaSpecimenParamsFile, self).check():
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
                self.set_property("cut_left", json_dict["cut_left"])
                self.set_property("cut_tail", json_dict["cut_tail"])
                self.set_property("length_contain", json_dict["length_contain"])
                self.set_property("adapter", json_dict["phred_score"])
                self.set_property("phred_score", json_dict["phred_score"])
                self.set_property("min_len", json_dict["min_len"])
                self.set_property("max_len", json_dict["max_len"])
            else:
                self.set_property("cut_left", json_dict["cut_left"])
                self.set_property("cut_tail", json_dict["cut_tail"])
                self.set_property("length_contain", json_dict["length_contain"])
                self.set_property("adapter", json_dict["phred_score"])
                self.set_property("phred_score", json_dict["phred_score"])
                self.set_property("min_len", json_dict["min_len"])
                self.set_property("max_len", json_dict["max_len"])
        except:
            raise FileError("json: %s格式不正确" % self.prop["path"])
        f.close()

if __name__ == "__main__":
    a = MirnaSpecimenParamsFile()
    a.set_path("/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/to_file/sample_qc_params_dir/rna.json")
