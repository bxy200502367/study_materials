# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/31
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml

DatasplitSplitByBarcodeOfficialAgent = type(
    "DatasplitSplitByBarcodeOfficialAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "datasplit_split_by_barcode_official.yml")))
DatasplitSplitByBarcodeOfficialTool = type(
    "DatasplitSplitByBarcodeOfficialTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "datasplit_split_by_barcode_official.yml"),
                             global_config=read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml"))))