# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230329
# last modify: 20230329

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugartool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.tool_global_config import tool_global_config


SUGAR_YAML = r"""
name: fastq to fasta
description: |
    fastq文件转化成fasta文件
cpu: 1
mem: 4G
squeue: chaifen
global_var:
    - seqtk
options:
    - name: fastq_path
      desc: fastq文件
      type: string
      required: True
    - name: sample_name
      desc: 样本名
      type: string
      required: True
cmds:
    - name: run_fq_to_fa
      shell: True
      formatter: >
          {seqtk} seq -a {fastq_path} > {output_dir}/{sample_name}.merge.fa
"""

DatasplitFqToFaV3Agent = type("DatasplitFqToFaV3Agent", (Agent, ),
                                      create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitFqToFaV3Tool = type("DatasplitFqToFaV3Tool", (Tool, ),
                                     create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
