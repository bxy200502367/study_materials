# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/24
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import os
from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml

def get_fq_str(self):
    file_list = []
    dir_list = os.listdir(self.option("fastq_dir"))
    if len(dir_list) != int(self.option("tuple_number")):
        raise Exception("需要合并 {} 个样本，和 tuple_number {}个样本冲突".format(len(dir_list), self.option("tuple_number")))      
    for dir in dir_list:
        for file in os.listdir(os.path.join(self.option("fastq_dir"), dir)):
            file_list.append(os.path.join(self.option("fastq_dir"), dir, file))
    return " ".join(file_list)
    
DataMergeAgent = type(
    "DataMergeAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "data_merge.yml")))

DataMergeTool = type(
    "DataMergeTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "data_merge.yml"),
                             global_config=read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml")),
                             get_fq_str = get_fq_str))
