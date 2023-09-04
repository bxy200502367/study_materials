# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230209
# last modify: 20230209

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugartool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.tool_global_config import tool_global_config

SUGAR_YAML = r"""
name: lima summary
description: |
    生成lima summary结果
cpu: 1
mem: 8G
squeue: chaifen
global_var:
    - python3
    - generate_lima_summary
env:
    - LD_LIBRARY_PATH
options:
    - name: lima_summary_file
      desc: to_file生成的文件
      type: string
      required: True
cmds:
    - name: run_generate_pacbio_sample_list
      formatter: >
          {python3} {generate_lima_summary} --infile {lima_summary_file} --outfile {output_dir}/lima_count.txt
"""


DatasplitLimaSummaryV3Agent = type("DatasplitLimaSummaryV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitLimaSummaryV3Tool = type("DatasplitLimaSummaryV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
