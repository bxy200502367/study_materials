# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/31
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def judge_split(self):
    if self.option("split_type") == "Pair" and self.option(valid_length) == "":
        return False
    elif self.option("split_type") == "Pair" and self.option(valid_length) != "":
        return True
    elif self.option("split_type") == "Single":
        return False
    else:
        raise("whenif的判断需要考虑其他情况")
    
DatasplitMetaNoOfficialPairModule = type(
    "DatasplitMetaNoOfficialPairModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "datasplit_meta_no_official_pair.yml")))