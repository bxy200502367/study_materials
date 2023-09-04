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
name: rfam blast
description: |
    对rfam数据库进行blastn比对
cpu: 4
mem: 10G
squeue: chaifen
global_var:
    - blastn
    - rfam_database
env:
    - LD_LIBRARY_PATH
options:
    - name: fasta_path
      desc: 序列fastq文件
      type: string
      required: True
    - name: evalue
      desc: balstn的evalue值
      type: float
      required: True
    - name: num_threads
      desc: blastn线程数
      type: int
      required: True
    - name: outfmt
      desc: blastn输出格式，默认为xml
      type: int
      required: True
    - name: num_alignment
      desc: blastn每条序列的输出结果
      type: int
      required: True
    - name: sample_name
      desc: 样本名
      type: string
      required: True
cmds:
    - name: run_rfam_blastn
      formatter: >
          {blastn} -query {fasta_path} -db {rfam_database} -num_threads {num_threads} -evalue {evalue} -outfmt {outfmt} 
          -max_hsps 10 -max_target_seqs {num_alignment} -out {output_dir}/{sample_name}.xml
"""

DatasplitRfamBlastV3Agent = type("DatasplitRfamBlastV3Agent", (Agent, ),
                                      create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitRfamBlastV3Tool = type("DatasplitRfamBlastV3Tool", (Tool, ),
                                     create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
