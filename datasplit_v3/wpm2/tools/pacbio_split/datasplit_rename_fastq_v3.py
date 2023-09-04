# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230301
# last modify: 20230301

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugartool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.tool_global_config import tool_global_config

SUGAR_YAML = r"""
name: rename fastq
description: |
    过滤
cpu: 2
mem: 4G
squeue: chaifen
global_var:
    - ln
    - rm
env:
    - LD_LIBRARY_PATH
options:
    - name: old_fastq_file
      desc: 要过滤的fastq文件
      type: string
      required: True
    - name: new_fastq_path
      desc: 最小长度
      type: string
      required: True
cmds:
    - name: run_pacbio_length_filter
      shell: True
      formatter: >
          {rm} -f {new_fastq_path} && {ln} {old_fastq_file} {new_fastq_path}
"""


DatasplitRenameFastqV3Agent = type("DatasplitRenameFastqV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitRenameFastqV3Tool = type("DatasplitRenameFastqV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
