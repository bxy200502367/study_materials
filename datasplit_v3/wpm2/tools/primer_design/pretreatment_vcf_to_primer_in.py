# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/08
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml

PretreatmentVcfToPrimerInAgent = type(
    "PretreatmentVcfToPrimerInAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "pretreatment_vcf_to_primer_in.yml")))

PretreatmentVcfToPrimerInTool = type(
    "PretreatmentVcfToPrimerInTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "pretreatment_vcf_to_primer_in.yml"),
                             global_config=read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml"))))
