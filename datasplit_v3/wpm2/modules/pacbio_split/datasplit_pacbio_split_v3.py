# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230117
# last modify: 20230206

from biocluster.core.exceptions import OptionError
from biocluster.module import Module
from mbio.modules.datasplit_v3.sugarmodule import create_module_dict_by_yaml


SUGAR_YAML="""
name: hifi pacbio split
description: |
    三代拆分module
options:
    - name: ccs_bam
      desc: 要拆分的bam文件
      type: string
      required: True
    - name: hifi_preset_mode
      desc: hifi拆分模式,单端拆还是双端拆
      type: string
      required: True
    - name: sample_sheet
      desc: to_file生成的sample_sheet信息
      type: string
      required: True
    - name: source_data
      desc: 来源数据是hifi数据还是subreads数据
      type: string
      required: True
phase_configs:
    - phase_name: Step01
      phase_desc: 转化sample_info和barcode文件
      routine_configs:
          - - name: datasplit_v3.pacbio_split.datasplit_generate_pacbio_sample_list_v3
              option:
                  sample_sheet: '{sample_sheet}'
              log: datasplit_generate_pacbio_sample_list_v3运行
              publish: 'temp'
          - - name: datasplit_v3.pacbio_split.datasplit_generate_pacbio_barcode_file_v3
              option:
                  sample_sheet: '{sample_sheet}'
              log: datasplit_generate_pacbio_barcode_file_v3运行
              publish: 'temp'
    - phase_name: Step02
      phase_desc: lima拆分bam文件
      routine_configs:
          - - name: datasplit_v3.pacbio_split.datasplit_lima_v3
              option:
                  ccs_bam: '{ccs_bam}'
                  barcode_file: '{output_dir}/temp/barcode.fasta'
                  hifi_preset_mode: '{hifi_preset_mode}'
                  source_data: '{source_data}'
              log: lima拆分
              publish: ''
            - name: datasplit_v3.pacbio_split.datasplit_pacbio_rename_v3
              option:
                  sample_list: '{output_dir}/temp/sample_list.txt'
                  split_dir: '{output_dir}/split'
              log: lima的结果改名
              publish: ''
"""

DatasplitPacbioSplitV3Module = type("DatasplitPacbioSplitV3Module", (Module, ),
                                     create_module_dict_by_yaml(SUGAR_YAML))

