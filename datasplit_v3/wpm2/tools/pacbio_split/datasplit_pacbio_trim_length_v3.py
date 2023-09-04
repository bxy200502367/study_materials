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
name: pacbio trim length
description: |
    fastq长度过滤
cpu: 2
mem: 4G
squeue: chaifen
global_var:
    - perl
    - pacbio_length_filter
env:
    - LD_LIBRARY_PATH
options:
    - name: fastq_file
      desc: 要过滤的fastq文件
      type: string
      required: True
    - name: min_length
      desc: 最小长度
      type: string
      required: True
    - name: max_length
      desc: 最大长度
      type: string
      required: True
    - name: sample_name
      desc: 样本名字
      type: string
      required: True
cmds:
    - name: run_pacbio_length_filter
      shell: True
      formatter: >
          {perl} {pacbio_length_filter} -i {fastq_file} -o {output_dir}/{sample_name}.trim.fastq -m {min_length} -x {max_length}
"""


DatasplitPacbioTrimLengthV3Agent = type("DatasplitPacbioTrimLengthV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitPacbioTrimLengthV3Tool = type("DatasplitPacbioTrimLengthV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
