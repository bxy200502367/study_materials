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
name: pacbio bam to fastq
description: |
    把bam文件转化成fastq文件
cpu: 4
mem: 32G
squeue: chaifen
global_var:
    - bam_to_fastq
options:
    - name: bam_file
      desc: 单个bam文件
      type: string
      required: True
    - name: out_prefix
      desc: 输出的fastq的前缀
      type: string
      required: True
cmds:
    - name: run_bam_to_fastq
      formatter: >
          {bam_to_fastq} -o {out_prefix} -c 4 {bam_file}
      log: 把bam转化成fastq
"""


DatasplitBamToFastqV3Agent = type("DatasplitBamToFastqV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitBamToFastqV3Tool = type("DatasplitBamToFastqV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
