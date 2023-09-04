# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230117
# last modify: 20230206

from biocluster.core.exceptions import OptionError
from biocluster.module import Module
from mbio.modules.datasplit_v3.sugarmodule import create_module_dict_by_yaml

SUGAR_YAML="""
name: library split
description: |
    二代一拆module
options:
    - name: data_path
      desc: bcl文件路径
      type: string
      required: True
    - name: lane_match
      desc: 匹配的lane
      type: string
      required: True
    - name: library_info_file
      desc: 一拆信息表
      type: string
      required: True
    - name: bases_mask
      desc: 测序模式
      type: string
      required: True
    - name: barcode_mismatch
      desc: barcode错配个数
      type: string
      required: True
    - name: ignore_error
      desc: 是否忽略warnings信息
      type: string
      required: True
phase_configs:
    - phase_name: Step01
      phase_desc: 生成library_sheet.csv文件
      routine_configs:
          - - name: datasplit_v3.library_split.datasplit_generate_library_sheet_v3
              option:
                  lane_match: '{lane_match}'
                  library_info_file: '{library_info_file}'
              log: 生成libray_sheet.csv
              publish: ''
    - phase_name: Step02
      phase_desc: bcl转化成fastq文件
      routine_configs:
          - - name: datasplit_v3.library_split.datasplit_bcl_to_fastq_v3
              option:
                  data_path: '{data_path}'
                  lane_match: '{lane_match}'
                  sample_sheet: '{output_dir}/{lane_match}.library_sheet.csv'
                  bases_mask: '{bases_mask}'
                  barcode_mismatch: '{barcode_mismatch}'
                  ignore_error: '{ignore_error}'
              log: 生成一拆的fastq
              publish: ''
"""

DatasplitLibrarySplitV3Module = type("DatasplitLibrarySplitV3Module", (Module, ),
                                     create_module_dict_by_yaml(SUGAR_YAML))

