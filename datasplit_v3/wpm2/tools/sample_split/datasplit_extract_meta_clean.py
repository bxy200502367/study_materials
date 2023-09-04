# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/31
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


import os
from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import (
    create_tool_dict_by_yaml,
    create_agent_dict_by_yaml,
)
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml


def dynamic_memory(self):
    size = os.path.getsize(self.option("in_fastq").path)
    memory = float(size) / 1024 / 1024 / 1024
    if memory < 5:
        return "8G"
    else:
        allocate_memory = str(int(memory) + 5) + "G"
        return allocate_memory


DatasplitExtractMetaCleanAgent = type(
    "DatasplitExtractMetaCleanAgent",
    (Agent,),
    create_agent_dict_by_yaml(
        read_local_file(__file__, "datasplit_extract_meta_clean.yml"),
        dynamic_memory=dynamic_memory,
    ),
)
DatasplitExtractMetaCleanTool = type(
    "DatasplitExtractMetaCleanTool",
    (Tool,),
    create_tool_dict_by_yaml(
        read_local_file(__file__, "datasplit_extract_meta_clean.yml"),
        global_config=read_yaml(read_local_file(__file__, "../tool_global_config.yml")),
    ),
)
