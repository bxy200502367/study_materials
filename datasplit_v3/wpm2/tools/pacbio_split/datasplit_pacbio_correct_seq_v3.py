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
name: pacbio correct seq
description: |
    fastq文件序列校正
cpu: 2
mem: 4G
squeue: chaifen
global_var:
    - perl
    - pacbio_correct_seq
    - mv
    - gzip
env:
    - LD_LIBRARY_PATH
options:
    - name: fastq_file
      desc: 要过滤的fastq文件
      type: string
      required: True
    - name: forward_primer
      desc: f端primer序列
      type: string
      required: True
    - name: reverse_primer
      desc: r端primer序列
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
          {perl} {pacbio_correct_seq} -i {fastq_file} -f {forward_primer} -r {reverse_primer} -l 2 -o {work_dir}/{sample_name}
    - name: run_rename_primer_fastq
      shell: True
      formatter: >
          {mv} {work_dir}/{sample_name}.split.primer.fq {output_dir}/{sample_name}.value.fastq
"""


DatasplitPacbioCorrectSeqV3Agent = type("DatasplitPacbioCorrectSeqV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitPacbioCorrectSeqV3Tool = type("DatasplitPacbioCorrectSeqV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
