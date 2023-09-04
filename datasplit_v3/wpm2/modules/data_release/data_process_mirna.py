# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/08/01
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def judge_run_merge_rename(self):
    if self.option("merge_st") == "True" or self.option("rename_st") == "True":
        return True
    else:
        return False

DataProcessMirnaModule = type(
    "DataProcessMirnaModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "data_process_mirna.yml"),
                               judge_run_merge_rename = judge_run_merge_rename))
