# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/24
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def get_r1_fq_dict(self):
    """
    获得r1的下载列表
    """
    r1_fq_dict = {}
    r1_paths_list = self.option("r1_paths_str").split(";")
    for index, r1_path in enumerate(r1_paths_list, start=0):
        r1_fq_dict[str(index).zfill(3)] = r1_path
    return r1_fq_dict

def get_r2_fq_dict(self):
    """
    获得r2的下载列表
    """
    r2_fq_dict = {}
    r2_paths_list = self.option("r2_paths_str").split(";")
    for index, r2_path in enumerate(r2_paths_list, start=0):
        r2_fq_dict[str(index).zfill(3)] = r2_path
    return r2_fq_dict

DataMergeRawModule = type(
    "DataMergeRawModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "data_merge_raw.yml"),
                               get_r1_fq_dict = get_r1_fq_dict,
                               get_r2_fq_dict = get_r2_fq_dict))
