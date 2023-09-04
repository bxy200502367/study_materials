# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230117
# last modify: 20230206

from biocluster.core.exceptions import OptionError
from biocluster.module import Module
from mbio.modules.datasplit_v3.sugarmodule import create_module_dict_by_yaml


SUGAR_YAML="""
name: pacbio qc
description: |
    三代质控module
options:
    - name: fastq_file
      desc: 要过滤的fastq文件
      type: string
      required: True
    - name: min_length
      desc: 最短长度
      type: string
      required: True
    - name: max_length
      desc: 最长长度
      type: string
      required: True
    - name: forward_primer
      desc: F端引物序列
      type: string
      required: True
    - name: reverse_primer
      desc: R端引物序列
      type: string
      required: True
    - name: sample_name
      desc: 样本id
      type: string
      required: True
phase_configs:
    - phase_name: Step01
      phase_desc: 长度过滤
      routine_configs:
          - - name: datasplit_v3.pacbio_split.datasplit_pacbio_trim_length_v3
              option:
                  fastq_file: '{fastq_file}'
                  min_length: '{min_length}'
                  max_length: '{max_length}'
                  sample_name: '{sample_name}'
              log: 对fastq文件进行长度过滤
              publish: ''
            - name: datasplit_v3.pacbio_split.datasplit_pacbio_correct_seq_v3
              option:
                  fastq_file: '{output_dir}/{sample_name}.trim.fastq'
                  forward_primer: '{forward_primer}'
                  reverse_primer: '{reverse_primer}'
                  sample_name: '{sample_name}'
              log: 对fastq文件进行序列校正
              publish: ''
            - name: datasplit_v3.pacbio_split.datasplit_sequence_rename_v3
              option:
                  fastq_file: '{output_dir}/{sample_name}.value.fastq'
                  sample_name: '{sample_name}'
              log: 对clean的fastq文件根据样本名重新命名
              publish: ''
"""

DatasplitPacbioQcV3Module = type("DatasplitPacbioQcV3Module", (Module, ),
                                     create_module_dict_by_yaml(SUGAR_YAML))

