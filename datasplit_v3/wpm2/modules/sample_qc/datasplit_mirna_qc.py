# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/06/30
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.module import Module
from mbio.tools.datasplit_v3.sugar.module import create_module_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def get_r1_fastq(self):
    r1_fastq, _ = self.option("fastq_paths").split(";")
    return r1_fastq
  
def get_r2_fastq(self):
    _, r2_fastq = self.option("fastq_paths").split(";")
    return r2_fastq

def get_specimen_id(self):
    specimen_id, *_ = self.option("sample_id").split("--")
    return specimen_id
  
def get_library_number(self):
    _, library_number, *_ = self.option("sample_id").split("--")
    return library_number

def get_specimen_name(self):
    _, _, specimen_name, _ = self.option("sample_id").split("--")
    return specimen_name

def get_majorbio_name(self):
    _, _, _, majorbio_name = self.option("sample_id").split("--")
    return majorbio_name


DatasplitMirnaQcModule = type(
    "DatasplitMirnaQcModule", (Module, ),
    create_module_dict_by_yaml(read_local_file(__file__, "datasplit_mirna_qc.yml"),
                               get_r1_fastq = get_r1_fastq,
                               get_r2_fastq = get_r2_fastq,
                               get_specimen_id = get_specimen_id,
                               get_library_number = get_library_number,
                               get_specimen_name = get_specimen_name,
                               get_majorbio_name = get_majorbio_name))