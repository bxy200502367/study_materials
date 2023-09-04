# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230220
# last modify: 20230220

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugartool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.tool_global_config import tool_global_config

SUGAR_YAML = r"""
name: pacbio seqkit fastq
description: |
    fastq文件统计
cpu: 4
mem: 32G
squeue: chaifen
global_var:
    - seqkit
env:
    - LD_LIBRARY_PATH
options:
    - name: fastq_dir
      desc: 要统计的fastq文件夹
      type: string
      required: True
    - name: match_pattern
      desc: 文件匹配模式
      type: string
      required: True
    - name: output_file
      desc: 输出文件名
      type: string
      required: True
cmds:
    - name: run_seqkit
      shell: True
      formatter: >
          {seqkit} stats -j 4 {fastq_dir}/{match_pattern} -a -b -T > {output_dir}/{output_file}
"""


DatasplitPacbioFastqStatV3Agent = type("DatasplitPacbioFastqStatV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitPacbioFastqStatV3Tool = type("DatasplitPacbioFastqStatV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
