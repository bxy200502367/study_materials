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
    - name: r1_fastq_path
      desc: r1序列fastq文件
      type: infile
      required: True
      format: dna_evolution.test
    - name: r2_fastq_path
      desc: r2序列fastq文件
      type: infile
      required: True
      format: dna_evolution.test
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
    - name: evalue
      desc: blastn的evalue值
      type: float
      required: True
    - name: num_threads
      desc: blastn所需要的线程
      type: int
      required: True
    - name: outfmt
      desc: blastn输出的格式,默认是xml
      type: int
      required: True
    - name: num_alignment
      desc: blastn每条序列输出的序列
      type: int
      required: True
phase_configs:
    - phase_name: Step01
      phase_desc: rfam比对统计
      routine_configs:
          - - name: datasplit_v3.rfam.datasplit_random_sampling_v3
              option:
                  r1_fastq_path: '{r1_fastq_path}'
                  r2_fastq_path: '{r2_fastq_path}'
                  random_number: '{random_number}'
                  read_num: '{read_num}'
                  sample_name: '{sample_name}'
              log: 对两端fastq文件随机取样并且合并
              publish: ''
            - name: datasplit_v3.rfam.datasplit_fq_to_fa_v3
              option:
                  fastq_path: '{output_dir}/{sample_name}.merge.fq'
                  sample_name: '{sample_name}'
              log: fastq文件转化成fasta文件
              publish: ''
            - name: datasplit_v3.rfam.datasplit_rfam_blast_v3
              option:
                  fasta_path: '{output_dir}/{sample_name}.merge.fa'
                  evalue: '{evalue}'
                  num_threads: '{num_threads}'
                  outfmt: '{outfmt}'
                  num_alignment: '{num_alignment}'
                  sample_name: '{sample_name}'
              log: fasta文件和rfam比对
              publish: ''
            - name: datasplit_v3.rfam.rfam_stat
              option:
                  xml_file: '{output_dir}/{sample_name}.xml'
                  sample_name: '{sample_name}'
              log: 对blasn比对后的xml格式统计
              publish: ''
"""

DatasplitRfamV3Module = type("DatasplitRfamV3Module", (Module, ),
                                     create_module_dict_by_yaml(SUGAR_YAML))

