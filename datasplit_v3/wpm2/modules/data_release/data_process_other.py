# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/29
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file


def judge_merge_rename_qc1(self):
    """
    需要合并或或者改名或者质控，此时需要拉s3路径
    """
    if self.option("merge_st") == "True" or self.option("rename_st") == "True" or self.option("qc_st") == "True":
        return True
    else:
        return False
    
def judge_merge_rename_qc2(self):
    """
    加上是否存在clean的本地路径，如果存在直接合并
    """
    if (self.option("merge_st") == "True" or self.option("rename_st") == "True" or self.option("qc_st") == "True") and self.option("exist_s3_clean") == "False":
        return True
    else:
        return False

def judge_qc_1(self):
    if self.option("qc_st") == "True" and self.option("exist_s3_clean") == "True" and self.option("rename_st") == "True":
        return True
    else:
        return False
    
def judge_qc_2(self):
    if self.option("qc_st") == "True" and self.option("exist_s3_clean") == "True" and self.option("rename_st") == "False":
        return True
    else:
        return False
    
DataProcessOtherModule = type(
    "DataProcessOtherModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "data_process_other.yml"),
                               judge_merge_rename_qc1 = judge_merge_rename_qc1,
                               judge_merge_rename_qc2 = judge_merge_rename_qc2,
                               judge_qc_1 = judge_qc_1,
                               judge_qc_2 = judge_qc_2))
