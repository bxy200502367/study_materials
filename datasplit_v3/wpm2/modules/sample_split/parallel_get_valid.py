# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/06/02
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def make_part_nums(self):
    """
    生成part_nums值列
    """
    part_range = {}
    for i in range(1,self.option("part_nums") + 1):
        part_name = "part_00" + str(i)
        part_range[part_name] = part_name
    return part_range

ParallelGetValidModule = type(
    "ParallelGetValidModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "parallel_get_valid.yml"),
                               make_part_nums=make_part_nums))