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


class MetaParamsFile(File):
    """
    name: meta_params
    Description: |
        多样性拆分参数的File类
        json字符串,主要是软件的参数，键有flash；split_by_barcode；trim_fqseq；trimmomatic；
        length_required: 长度过滤参数,fastp用
        cut_by_quality5: fastp用，默认0
        cut_by_quality3: fastp用，默认20
        cut_right_mean_quality: fastp用
        cut_right_window_size: fastp用
        min_length: -m,两个reads之间所需的最小重叠长度,以提供可靠的重叠;flash使用
        max_length: -M,两个reads之间的最大重叠长度
        mismatch_rate: flash用
        valid_length: trim_fqseq专用,trim_fqseq专用,最长值
        min_len: trim_fqseq专用,最短值
        mismatch: split_by_barcode的错配
    """
    def __init__(self):
        super(MetaParamsFile, self).__init__()

    def check(self):
        if super(MetaParamsFile, self).check():
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
                if "trimmomatic" in json_dict:
                    self.set_property("length_required", json_dict["trimmomatic"]["minlen"])
                    self.set_property("cut_by_quality5", json_dict["trimmomatic"]["leading"])
                    self.set_property("cut_by_quality3", json_dict["trimmomatic"]["trailing"])
                    self.set_property("cut_right_window_size", json_dict["trimmomatic"]["slidingwindow"].split(":")[0])
                    self.set_property("cut_right_mean_quality", json_dict["trimmomatic"]["slidingwindow"].split(":")[1])
                elif "meta-fastp" in json_dict:
                    self.set_property("length_required", json_dict["meta-fastp"]["minlen"])
                    self.set_property("cut_by_quality5", json_dict["meta-fastp"]["leading"])
                    self.set_property("cut_by_quality3", json_dict["meta-fastp"]["trailing"])
                    self.set_property("cut_right_window_size", json_dict["meta-fastp"]["slidingwindow"].split(":")[0])
                    self.set_property("cut_right_mean_quality", json_dict["meta-fastp"]["slidingwindow"].split(":")[1])
                else:
                    raise FileError("多样性质控参数传递有误")
                self.set_property("min_length", json_dict["flash"]["m"])
                self.set_property("max_length", json_dict["flash"]["M"])
                self.set_property("mismatch_rate", json_dict["flash"]["x"])
                self.set_property("valid_length", json_dict["trim_fqseq"]["m"])
                self.set_property("min_len", json_dict["trim_fqseq"]["l"])
                self.set_property("mismatch", json_dict["split_by_barcode"]["mismatch"])
                self.set_property("split_type", json_dict["split_type"])
            else:
                self.set_property("length_required", None)
                self.set_property("cut_by_quality5", None)
                self.set_property("cut_by_quality3", None)
                self.set_property("cut_right_window_size", None)
                self.set_property("cut_right_mean_quality", None)
                self.set_property("min_length", None)
                self.set_property("max_length", None)
                self.set_property("mismatch_rate", None)
                self.set_property("valid_length", None)
                self.set_property("min_len", None)
                self.set_property("mismatch", None)
                self.set_property("split_type", None)
        except:
            raise FileError("json: %s格式不正确" % self.prop["path"])
        f.close()

if __name__ == "__main__":
    a = MetaParamsFile()
    a.set_path("/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/sample_split/test/meta.json")
    print a.check()
    print a.prop["length_required"]
