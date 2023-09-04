# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/06/12
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""



from biocluster.core.exceptions import FileError
from biocluster.iofile import File
import os
import json


class RnaParamsFile(File):
    """
    name: rna_params
    Description: |
        rna质控参数File类
    """
    def __init__(self):
        super(RnaParamsFile, self).__init__()

    def check(self):
        if super(RnaParamsFile, self).check():
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
                self.set_property("length_required", json_dict["fastp"]["l"])
                self.set_property("cut_mean_quality", json_dict["fastp"]["M"])
                self.set_property("n_base_limit", json_dict["fastp"]["n"])
                self.set_property("qualified_quality_phred", json_dict["fastp"]["q"])
                self.set_property("cut_by_quality3", json_dict["fastp"]["3"])
                self.set_property("cut_by_quality5", json_dict["fastp"]["5"])
                self.set_property("adapter_sequence", json_dict["fastp"]["adapter_sequence"])
                self.set_property("adapter_sequence_r2", json_dict["fastp"]["adapter_sequence_r2"])
            else:
                self.set_property("length_required", None)
                self.set_property("cut_mean_quality", None)
                self.set_property("n_base_limit", None)
                self.set_property("qualified_quality_phred", None)
                self.set_property("cut_by_quality3", None)
                self.set_property("cut_by_quality5", None)
                self.set_property("adapter_sequence", None)
                self.set_property("adapter_sequence_r2", None)
        except:
            raise FileError("json: %s格式不正确" % self.prop["path"])
        f.close()

if __name__ == "__main__":
    a = RnaParamsFile()
    a.set_path("/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/to_file/sample_qc_params_dir/rna.json")
