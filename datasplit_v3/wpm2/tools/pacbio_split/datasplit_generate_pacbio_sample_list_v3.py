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
name: generate pacbio sample list
description: |
    生成sample_list.txt
cpu: 2
mem: 16G
squeue: chaifen
global_var:
    - python3
    - generate_pacbio_sample_list
env:
    - LD_LIBRARY_PATH
options:
    - name: sample_sheet
      desc: to_file生成的文件
      type: string
      required: True
cmds:
    - name: run_generate_pacbio_sample_list
      formatter: >
          {python3} {generate_pacbio_sample_list} --infile {sample_sheet} --outfile {output_dir}/sample_list.txt
"""


DatasplitGeneratePacbioSampleListV3Agent = type("DatasplitGeneratePacbioSampleListV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitGeneratePacbioSampleListV3Tool = type("DatasplitGeneratePacbioSampleListV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
