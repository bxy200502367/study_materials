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
name: generate pacbio barcode file
description: |
    生成barcode.fasta
cpu: 2
mem: 16G
squeue: chaifen
global_var:
    - python3
    - generate_pacbio_barcode_file
env:
    - LD_LIBRARY_PATH
options:
    - name: sample_sheet
      desc: to_file生成的文件
      type: string
      required: True
cmds:
    - name: run_generate_pacbio_barcode_file
      formatter: >
          {python3} {generate_pacbio_barcode_file} --infile {sample_sheet} --outfile {output_dir}/barcode.fasta
"""


DatasplitGeneratePacbioBarcodeFileV3Agent = type("DatasplitGeneratePacbioBarcodeFileV3Agent", (Agent, ),
                                                 create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitGeneratePacbioBarcodeFileV3Tool = type("DatasplitGeneratePacbioBarcodeFileV3Tool", (Tool, ),
                                                 create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))
