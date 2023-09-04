# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230220
# last modify: 20230220

from biocluster.core.exceptions import OptionError
from biocluster.module import Module
from mbio.modules.datasplit_v3.sugarmodule import create_module_dict_by_yaml


SUGAR_YAML="""
name: pacbio stat
description: |
    三代拆分统计module
options:
    - name: raw_fastq_dir
      desc: 质控前fastq文件夹
      type: string
      required: True
    - name: clean_fastq_dir
      desc: 质控后fastq文件夹
      type: string
      required: True
    - name: lima_summary_file
      desc: lima拆分的统计文件
      type: string
      required: True
phase_configs:
    - phase_name: Step01
      phase_desc: 质控前的fastq统计
      routine_configs:
          - - name: datasplit_v3.pacbio_split.datasplit_pacbio_fastq_stat_v3
              option:
                  fastq_dir: '{raw_fastq_dir}'
                  match_pattern: '*.ccs.fastq.gz'
                  output_file: raw_fastq_stat.xls
              log: 质控前统计运行
              publish: ''
          - - name: datasplit_v3.pacbio_split.datasplit_pacbio_fastq_stat_v3
              option:
                  fastq_dir: '{clean_fastq_dir}'
                  match_pattern: '*.value.fastq.gz'
                  output_file: clean_fastq_stat.xls
              log: 质控后统计运行
              publish: ''
          - - name: datasplit_v3.pacbio_split.datasplit_lima_summary_v3
              option:
                  "lima_summary_file": '{lima_summary_file}'
              log: 统计lima结果
              publish: ''
"""

DatasplitPacbioStatV3Module = type("DatasplitPacbioStatV3Module", (Module, ),
                                     create_module_dict_by_yaml(SUGAR_YAML))

