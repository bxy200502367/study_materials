# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/27
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""



from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def get_fq_dict(self):
    """
    获得下载列表合并的列表
    """
    fq_dict = {}
    paths_list = self.option("paths_str").split(";")
    for index, path in enumerate(paths_list, start=0):
        fq_dict[str(index).zfill(3)] = path
    return fq_dict

DataMergeModule = type(
    "DataMergeModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "data_merge.yml"),
                               get_fq_dict = get_fq_dict))
