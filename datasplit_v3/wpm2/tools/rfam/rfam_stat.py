# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/25
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import os
from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml


def judge_xml_size(self):
    file_size = os.path.getsize(self.option("xml_file"))
    if file_size > 0:
        return True
    else:
        return False


RfamStatAgent = type(
    "RfamStatAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "rfam_stat.yml")))
RfamStatTool = type(
    "RfamStatTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "rfam_stat.yml"),
                             global_config=read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml")),
                             judge_xml_size = judge_xml_size))
