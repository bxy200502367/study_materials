# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230209
# last modify: 20230209

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugartool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.tool_global_config import tool_global_config
import unittest

SUGAR_YAML = r"""
name: lima
description: |
    lima拆分三代ccs
cpu: 8
mem: 64G
squeue: chaifen
global_var:
    - lima
    - mkdir
options:
    - name: ccs_bam
      desc: 要拆分的bam文件路径
      type: string
      required: True
    - name: barcode_file
      desc: barcode的文件
      type: string
      required: True
    - name: hifi_preset_mode
      desc: hifi拆分模式,单端拆还是双端拆
      type: string
      required: True
    - name: source_data
      desc: 来源文件是hifi还是subreads
      type: string
      required: True
cmds:
    - name: make_dir
      shell: True
      formatter: >
          {mkdir} -p {output_dir}/split
    - name: run_lima
      formatter: >
          {lima} --split-bam-named --min-passes 0 --ccs --hifi-preset {hifi_preset_mode} --num-threads 6
          {ccs_bam} {barcode_file} {output_dir}/split/samples.bam
      whenif:
          var: source_data
          oprt: ==
          value: hifi_reads
      whenelse: >
          {lima} -s --split-bam-named --min-passes 0 --num-threads 6 
          {ccs_bam} {barcode_file} {output_dir}/split/samples.bam
"""

DatasplitLimaV3Agent = type("DatasplitLimaV3Agent", (Agent, ),
                            create_agent_dict_by_yaml(SUGAR_YAML))
DatasplitLimaV3Tool = type("DatasplitLimaV3Tool", (Tool, ),
                            create_tool_dict_by_yaml(SUGAR_YAML, global_config=tool_global_config))

class TestFunction(unittest.TestCase):
    '''
    测试脚本
    '''
    def test(self):
        import random
        from mbio.workflows.single import SingleWorkflow
        from biocluster.wsheet import Sheet
        data = {
            "id": "datasplit_lima_v3_" + str(random.randint(1, 10000)),
            "type": "tool",
            "name": "datasplit_v3.pacbio_split.datasplit_lima_v3",
            "options": {
                "ccs_bam": "/mnt/clustre/upload/pacbio/r64440e_20230206_072245/1_B02/m64440e_230206_073455.hifi_reads.bam",
                "barcode_file": "/mnt/clustre/users/sanger-dev/users/yuan.xu/Datasplit_v3/tools/datasplit_lima_v3/barcode.fasta",
                "hifi_preset_mode": "ASYMMETRIC"
            }
        }
        wsheet = Sheet(data=data)
        wf = SingleWorkflow(wsheet)
        wf.run()


if __name__ == '__main__':
    unittest.main()