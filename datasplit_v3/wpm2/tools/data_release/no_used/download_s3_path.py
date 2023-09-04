# -*- coding:utf-8 -*-
"""
Last-edit: 2023/04/09
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml

DownloadS3PathAgent = type(
    "DownloadS3PathAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "download_s3_path.yml")))

DownloadS3PathTool = type(
    "DownloadS3PathTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "download_s3_path.yml"),
                             global_config=read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml"))))
