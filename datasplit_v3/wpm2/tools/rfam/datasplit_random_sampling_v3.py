# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230328
# last modify: 20230328

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugartool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.tool_global_config import tool_global_config


SUGAR_YAML = r"""
name: random sampling
description: |
    对fastq文件抽样
cpu: 2
mem: 4G
squeue: chaifen
global_var:
    - seqtk
    - cat
options:
    - name: r1_fastq_path
      desc: r1序列fastq文件
      type: string
      required: True
    - name: r2_fastq_path
      desc: r2序列fastq文件
      type: string
      required: True
    - name: random_number
      desc: 随机数
      type: int
      required: True
    - name: read_num
      desc: 抽取的序列数
      type: int
      required: True
    - name: sample_name
      desc: 样本名
      type: string
      required: True
cmds:
    - name: run_random_sampling_r1
      shell: True
      formatter: >
          {seqtk} sample -s{random_number} {r1_fastq_path} {read_num} > {work_dir}/{sample_name}.r1.fq
    - name: run_random_sampling_r2
      shell: True
      formatter: >
          {seqtk} sample -s{random_number} {r1_fastq_path} {read_num} > {work_dir}/{sample_name}.r2.fq
    - name: cat_r1_r2
      shell: True
      formatter: >
          {cat} {work_dir}/{sample_name}.r1.fq {work_dir}/{sample_name}.r2.fq > {output_dir}/{sample_name}.merge.fq
"""

DatasplitRandomSamplingV3Agent = type("DatasplitRandomSamplingV3Agent", (Agent, ),
                                      create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitRandomSamplingV3Tool = type("DatasplitRandomSamplingV3Tool", (Tool, ),
                                     create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
