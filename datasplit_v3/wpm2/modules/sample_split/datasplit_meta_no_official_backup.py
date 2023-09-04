# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/23
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def is_single(self):
    if self.option("split_type") == "Single":
        return True
    elif self.option("split_type") == "Pair":
        return False
    elif self.option("split_type") == "Auto":
        return self.option("meta_no_official_info").prop["max_lib_insert_size"] > 550
    raise Exception("沒有這個split_type")

def is_pair(self):
    if self.option("split_type") == "Single":
        return False
    elif self.option("split_type") == "Pair":
        return True
    elif self.option("split_type") == "Auto":
        return self.option("meta_no_official_info").prop["max_lib_insert_size"] <= 550
    raise Exception("沒有這個split_type")
    
DatasplitMetaNoOfficialModule = type(
    "DatasplitMetaNoOfficialModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "datasplit_meta_no_official.yml"),
                               is_single = is_single,
                               is_pair = is_pair))