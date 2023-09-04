# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/27
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml
import os
import json

def dynamic_memory(self):
    size = os.path.getsize(self.option("valid_fastq_r1"))
    memory = float(size) / 1024 / 1024 / 1024 * 2
    if memory > 100:
        return "100G"
    elif memory > 5:
        return "{}G".format(int(memory))
    else:
        return "5G"

def get_sample_primer(self):
    self.primer_info = {}
    with open(self.option("sample_primer_json"), "rb") as f:
        self.primer_info = json.load(f)

def gunzip_raw(self):
    """
    对结果文件进行压缩
    """
    raw_dir = os.path.join(self.work_dir, "raw")
    for file in os.listdir(raw_dir):
        name = file + ".gz"
        if file.endswith(".R1.raw.fastq"):
            sample_name = file.split(".R1.raw.fastq")[0]
            if sample_name in self.primer_info.keys():
                name = sample_name + "." + self.primer_info[sample_name] + ".R1.raw.fastq.gz"
        elif file.endswith(".R2.raw.fastq"):
            sample_name = file.split(".R2.raw.fastq")[0]
            if sample_name in self.primer_info.keys():
                name = sample_name + "." + self.primer_info[sample_name] + ".R2.raw.fastq.gz"
        old_file_name = os.path.join(raw_dir, file)
        new_file_name = os.path.join(self.output_dir, name)
        os.system("gzip -c {} > {}".format(old_file_name, new_file_name))


DatasplitExtractRawFromValidAgent = type(
    "DatasplitExtractRawFromValidAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "datasplit_extract_raw_from_valid.yml"),
                              dynamic_memory = dynamic_memory))
DatasplitExtractRawFromValidTool = type(
    "DatasplitExtractRawFromValidTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "datasplit_extract_raw_from_valid.yml"),
                             global_config = read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml")),
                             get_sample_primer = get_sample_primer,
                             gunzip_raw = gunzip_raw))