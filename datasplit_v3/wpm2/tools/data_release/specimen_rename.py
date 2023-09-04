# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/08/16
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import os
from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml


def exist_r1_clean_rename(self):
    if os.path.exists(self.option("r1_clean_fastq")) and self.option("rename_st") == "True":
        return True
    else:
        return False

def exist_r2_clean_rename(self):
    if os.path.exists(self.option("r2_clean_fastq")) and self.option("rename_st") == "True":
        return True
    else:
        return False
    
def exist_r1_clean_no_rename(self):
    if os.path.exists(self.option("r1_clean_fastq")) and self.option("rename_st") != "True":
        return True
    else:
        return False
    
def exist_r2_clean_no_rename(self):
    if os.path.exists(self.option("r2_clean_fastq")) and self.option("rename_st") != "True":
        return True
    else:
        return False

SpecimenRenameAgent = type(
    "SpecimenRenameAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "specimen_rename.yml")))

SpecimenRenameTool = type(
    "SpecimenRenameTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "specimen_rename.yml"),
                             global_config=read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml")),
                             exist_r1_clean_rename = exist_r1_clean_rename,
                             exist_r2_clean_rename = exist_r2_clean_rename,
                             exist_r1_clean_no_rename = exist_r1_clean_no_rename,
                             exist_r2_clean_no_rename = exist_r2_clean_no_rename))
