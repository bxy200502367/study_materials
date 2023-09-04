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
name: rfam stat
description: |
    对blastn后的xml文件进行统计
cpu: 4
mem: 4G
squeue: chaifen
global_var:
    - python
    - rfam_stat_script
    - rfam_seed
options:
    - name: xml_file
      desc: 序列fastq文件
      type: string
      required: True
    - name: sample_name
      desc: balstn的evalue值
      type: string
      required: True
cmds:
    - name: run_rfam_stat
      shell: True
      formatter: >
          {python} {rfam_stat_script} -i {xml_file} -db {rfam_seed} -o {output_dir}/{sample_name}.rfam_summary.xls
"""

DatasplitRfamStatV3Agent = type("DatasplitRfamStatV3Agent", (Agent, ),
                                      create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitRfamStatV3Tool = type("DatasplitRfamStatV3Tool", (Tool, ),
                                     create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
