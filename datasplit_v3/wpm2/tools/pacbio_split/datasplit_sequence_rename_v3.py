# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230306
# last modify: 20230306

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugartool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.tool_global_config import tool_global_config


SUGAR_YAML = r"""
name: rename sequence
description: |
    对质控完的clean_fastq序列重命名
cpu: 2
mem: 4G
squeue: chaifen
global_var:
    - python3
    - sequence_rename
    - gzip
env:
    - LD_LIBRARY_PATH
options:
    - name: fastq_file
      desc: 要对序列重命名的fastq文件
      type: string
      required: True
    - name: sample_name
      desc: 样本id
      type: string
      required: True
cmds:
    - name: run_lima
      formatter: >
          {python3} {sequence_rename} --fastq_file {fastq_file} --sample_name {sample_name} --outfile {output_dir}/{sample_name}.rename.value.fastq
    - name: run_gzip_fastq
      shell: True
      formatter: >
          {gzip} {output_dir}/{sample_name}.rename.value.fastq
"""

DatasplitSequenceRenameV3Agent = type("DatasplitSequenceRenameV3Agent", (Agent, ),
                            create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitSequenceRenameV3Tool = type("DatasplitSequenceRenameV3Tool", (Tool, ),
                            create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
