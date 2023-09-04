# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/25
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def judge_run_rename_rm_primer(self):
    if self.option("rm_primer_st") == "True" and self.option("rename_st") == "True":
        return True
    else:
        return False

def judge_run_rename_rm_primer2(self):
    if self.option("rm_primer_st") == "True" and self.option("rename_st") != "True":
        return True
    else:
        return False

DataProcessMetaModule = type(
    "DataProcessMetaModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "data_process_meta.yml"),
                               judge_run_rename_rm_primer = judge_run_rename_rm_primer,
                               judge_run_rename_rm_primer2 = judge_run_rename_rm_primer2))
