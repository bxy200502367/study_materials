# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/11
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml
import os
import re


def new_split_path(self):
    """
        拆分下机数据路径更新
    """
    self.sugar_var["bcl_path"] = "{data_path}/Data/Intensities/BaseCalls/".format(**self.sugar_var)
    data_path = "{data_path}".format(**self.sugar_var)
    print data_path
    if os.path.exists(data_path):
        self.sugar_var["new_data_path"] = data_path
        return
    if "ilustre" in data_path:
        new_data_path = data_path.replace("ilustre", "clustre")
        if os.path.exists(new_data_path):
            self.sugar_var["new_data_path"] = new_data_path
            return
    if "sglustre" in data_path:
        new_data_path = data_path.replace("sglustre", "ilustre")
        if os.path.exists(new_data_path):
            self.sugar_var["new_data_path"] = new_data_path
            return
    if "lustre" in data_path:
        new_data_path = data_path.replace("lustre", "lustre/users/sanger-dev/upload")
        if os.path.exists(new_data_path):
            self.sugar_var["new_data_path"] = new_data_path
            return
    if not os.path.exists(data_path):
        self.set_error("下机数据路径: {}没有找到，请检查".format(data_path))


def check_bcl2fastq_log(self):
    log_file = "{work_dir}/run_bcl2fastq.o".format(**self.sugar_var)
    if self.option("ignore_error") == "0":
        with open(log_file, "r") as f:
            lines = f.readlines()
            m = re.search("Processing completed with (.*?) errors and (.*?) warnings.*", lines[-2])
            log_info = m.group(0)
            error_counts = int(m.group(1))
            warning_counts = int(m.group(2))
            corrupt_files_list = []
            if m and error_counts:
                self.set_error("运行bcl2fastq出错,可能是测序模式有问题，请检查")
            else:
                if warning_counts:
                    self.logger.info(log_info)
                    for line in lines:
                        if re.search("WARNING", line):
                            corrupt_file_info = re.search("BCL file '\"(.*?)\"' corrupt.", line)
                            if corrupt_file_info:
                                corrupt_files_list.append(corrupt_file_info.group(1))
                    corrupt_file_list = list(set(corrupt_files_list))
                    if len(corrupt_file_list) > 10:
                        corrupt_files = ';'.join(corrupt_file_list[:10])
                        corrupt_files += "......"
                        self.logger.info("原始的bcl文件大概率不完整corrupt，请检查;文件{}不完整".format(corrupt_files))
                        self.set_error("原始的bcl文件大概率不完整corrupt，请检查;文件{}不完整".format(corrupt_files))
                    elif corrupt_file_list:
                        corrupt_files = ';'.join(corrupt_file_list)
                        self.logger.info("原始的bcl文件大概率不完整corrupt，请检查;文件{}不完整".format(corrupt_files))
                        self.set_error("原始的bcl文件大概率不完整corrupt，请检查;文件{}不完整".format(corrupt_files))
                    else:
                        return
                else:
                    return
    elif self.option("ignore_error") == "1":
        return
    else:
        self.set_error("ignore_error传参有问题,应该是0或者1中的一种")


def run_md5sum(self):
    """
        生成md5校验码,为什么生成了md5sum.txt;并且删除为空的文件夹
    """
    dir_path = os.path.join(self.work_dir, "bcl_result/Fastq")
    for fastq_dir in os.listdir(dir_path):
        fastq_dir_path = os.path.join(dir_path, fastq_dir)
        if len(os.listdir(fastq_dir_path)) > 0: #modified by yuan.xu:判断文件夹中文件个数 20230526
            md5sum_file = os.path.join(fastq_dir_path, "md5sum.txt")
            if os.path.exists(md5sum_file):
                os.remove(md5sum_file)
            else:
                pass
            os.system("md5sum {fastq_dir_path}/*.fastq.gz | awk -F 's?/' '{{print $1\t$NF}}'> {fastq_dir_path}/md5sum.txt"
                    .format(fastq_dir_path=fastq_dir_path))
        else:
            os.rmdir(fastq_dir_path)


DatasplitBclToFastqAgent = type(
    "DatasplitBclToFastqAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "datasplit_bcl_to_fastq.yml")))

DatasplitBclToFastqTool = type(
    "DatasplitBclToFastqTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "datasplit_bcl_to_fastq.yml"),
                             global_config=read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml")),
                             check_bcl2fastq_log=check_bcl2fastq_log,
                             run_md5sum=run_md5sum))
