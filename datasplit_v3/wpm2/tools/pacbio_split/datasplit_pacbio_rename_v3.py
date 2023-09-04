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
name: renam lima result
description: |
    重命名lima的结果
cpu: 2
mem: 16G
squeue: chaifen
global_var:
    - mkdir
    - python3
    - pacbio_rename
env:
    - LD_LIBRARY_PATH
options:
    - name: sample_list
      desc: sample_list.txt文件
      type: string
      required: True
    - name: split_dir
      desc: 拆分的文件路径
      type: string
      required: True
cmds:
    - name: make_dir
      shell: True
      formatter: >
          {mkdir} -p {output_dir}/split_result
    - name: run_pacbio_rename
      formatter: >
          {python3} {pacbio_rename} --sample_list {sample_list} --split_dir {split_dir} --out_dir {output_dir}/split_result
"""


DatasplitPacbioRenameV3Agent = type("DatasplitPacbioRenameV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitPacbioRenameV3Tool = type("DatasplitPacbioRenameV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
