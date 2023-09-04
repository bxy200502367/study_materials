# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230202
# last modify: 20230202


import re
import os
import json
import time
import shutil
# from src.mbio.workflows.datasplit_v2.submit import Submit
# from submit import Submit
from biocluster.workflow import Workflow
from biocluster.core.exceptions import OptionError


class PacbioSplitV3Workflow(Workflow):
    def __init__(self, wsheet_object):
        self._sheet = wsheet_object
        super(PacbioSplitV3Workflow, self).__init__(wsheet_object)
        options = [
            {"name": "pacbio_params", "type": "infile", "format": "datasplit.library_params", "required": True}, # 三代拆分参数
            {"name": "pacbio_sample_sheet", "type": "string"},
            {"name": "split_id", "type": "string"},
            {"name": "update_info", "type": "string"},
            {"name": "split_type", "type": "string"}
        ]
        self.add_option(options)
        self.set_options(self._sheet.options())
        self.lima_different = self.add_module("datasplit_v3.pacbio_split.datasplit_pacbio_split_v3")
        self.multi_bam_to_fastq = self.add_module("datasplit_v3.pacbio_split.datasplit_multi_bam_to_fastq_v3")
        self.multi_pacbio_qc = self.add_module("datasplit_v3.pacbio_split.datasplit_multi_pacbio_qc_v3")
        self.pacbio_stat = self.add_module("datasplit_v3.pacbio_split.datasplit_pacbio_stat_v3")
        self.import_pacbio = self.api.api("datasplit_v3.pacbio_split_v3")

    def check_options(self):
        if not self.option("pacbio_params").is_set:
            raise OptionError("缺少三代数据拆分参数,请检查")
        f = open(self.option("pacbio_params").prop["path"], "rb")
        try:
            json_dict = json.loads(f.read())
            self.params_json = json_dict["pacbio_split"]
        except:
            raise OptionError("JSON格式不正确")
        if self.option("split_type") == "different":
            self.hifi_preset_mode = "ASYMMETRIC"
        elif self.option("split_type") == "same":
            self.hifi_preset_mode = "SYMMETRIC"
        else:
            raise OptionError("lima的hifi-preset有误")
        if self.params_json["bam_path"].endswith("hifi_reads.bam"):
            self.source_data = "hifi_reads"
        elif self.params_json["bam_path"].endswith("subreads.bam"):
            self.source_data = "subreads_reads"
        else:
            raise OptionError("bam文件后缀既不是hifi_reads.bam也不是subreads.bam")

    def run_lima(self):
        options = {
            "ccs_bam": self.params_json["bam_path"],
            "hifi_preset_mode": self.hifi_preset_mode,
            "sample_sheet": self.option("pacbio_sample_sheet"),
            "source_data": self.source_data
        }
        self.lima_different.set_options(options)
        self.lima_different.on("end", self.set_output, "different_lima")
        self.lima_different.on("end", self.run_multi_bam_to_fastq)
        self.lima_different.run()

    def run_multi_bam_to_fastq(self):
        options = {
            "sample_list": os.path.join(self.output_dir, "temp", "sample_list.txt"),
            "split_result_dir": os.path.join(self.output_dir, "01.bam_result")
        }
        self.multi_bam_to_fastq.set_options(options)
        self.multi_bam_to_fastq.on("end", self.set_output, "bam_to_fastq")
        self.multi_bam_to_fastq.on("end", self.run_multi_pacbio_qc)
        self.multi_bam_to_fastq.run()

    def run_multi_pacbio_qc(self):
        options = {
            "sample_list": os.path.join(self.output_dir, "temp", "sample_list.txt"),
            "fastq_result_dir": os.path.join(self.output_dir, "02.raw_fastq")
        }
        self.multi_pacbio_qc.set_options(options)
        self.multi_pacbio_qc.on("end", self.set_output, "pacbio_qc")
        self.multi_pacbio_qc.on("end", self.run_pacbio_stat)
        self.multi_pacbio_qc.run()

    def run_pacbio_stat(self):
        options = {
            "raw_fastq_dir": os.path.join(self.output_dir, "02.raw_fastq"),
            "clean_fastq_dir": os.path.join(self.output_dir, "03.clean_fastq"),
            "lima_summary_file": os.path.join(self.lima_different.output_dir, "split", "samples.lima.summary")
        }
        self.pacbio_stat.set_options(options)
        self.pacbio_stat.on("end", self.set_output, "pacbio_stat")
        self.pacbio_stat.on("end", self.set_db)
        self.pacbio_stat.run()

    def set_db(self):
        s3_upload_dir = self._sheet.output
        self.import_pacbio.update_sg_pacbio(self.option("split_id"), os.path.join(self.output_dir, "04.pacbio_stat", "lima_count.txt"))
        self.import_pacbio.update_sg_pacbio_specimen(self.option("split_id"), s3_upload_dir,
                                            os.path.join(self.output_dir, "04.pacbio_stat", "raw_fastq_stat.xls"),
                                            os.path.join(self.output_dir, "04.pacbio_stat", "clean_fastq_stat.xls"),
                                            self.option("split_type"))
        #self.import_pacbio.update_sg_pacbio_status(self.option("split_id"))
        self.end()

    def run(self):
        self.run_lima()
        super(PacbioSplitV3Workflow, self).run()

    def set_output(self, event):
        obj = event['bind_object']
        if event['data'] == "different_lima":
            output = os.path.join(obj.output_dir, "split_result")
            temp = os.path.join(obj.output_dir, "temp")
            self.move2outputdir(output, "01.bam_result")
            self.move2outputdir(temp, "temp")
        elif event['data'] == "bam_to_fastq":
            self.move2outputdir(obj.output_dir, "02.raw_fastq")
        elif event['data'] == "pacbio_qc":
            self.move2outputdir(obj.output_dir, "03.clean_fastq")
        elif event['data'] == "pacbio_stat":
            self.move2outputdir(obj.output_dir, "04.pacbio_stat")
        else:
            self.set_error("经过这里")

    def move2outputdir(self, olddir, newdir):
        """
        移动一个目录下的所有文件/文件夹到workflow输出文件夹下
        :param olddir: 初始路径
        :param newdir: 目标路径，可以自定义
        :return:
        """
        start_time = time.time()
        if not os.path.isdir(olddir):
            self.set_error("需要移动到output目录的文件夹不存在。")
        newdir = os.path.join(self.output_dir, newdir)
        if not os.path.exists(newdir):
            os.makedirs(newdir)
        allfiles = os.listdir(olddir)
        oldfiles = [os.path.join(olddir, i) for i in allfiles]
        newfiles = [os.path.join(newdir, i) for i in allfiles]
        for newfile in newfiles:
            if os.path.isfile(newfile) and os.path.exists(newfile):
                os.remove(newfile)
            elif os.path.isdir(newfile) and os.path.exists(newfile):
                shutil.rmtree(newfile)
        for i in range(len(allfiles)):
            self.move_file(oldfiles[i], newfiles[i])
        end_time = time.time()
        duration = end_time - start_time
        self.logger.info("文件夹{}到{}移动耗时{}s".format(olddir, newdir, duration))

    def move_file(self, old_file, new_file):
        """
        递归移动文件或者文件到指定路径
        :param old_file: 初始路径
        :param new_file: 目的路径
        :return:
        """
        if os.path.isfile(old_file):
            os.link(old_file, new_file)
        else:
            os.mkdir(new_file)
            for file_ in os.listdir(old_file):
                file_path = os.path.join(old_file, file_)
                new_path = os.path.join(new_file, file_)
                self.move_file(file_path, new_path)

    def remove_file(self):
        """
        删除不需要上传到磁盘的文件
        :return:
        """
        rm_list = list()
        if self.option("split_type") == "different":
            rm_list.append(self.output_dir + "/01.bam_result")
        elif self.option("split_type") == "same":
            rm_list.append(self.output_dir + "/02.raw_fastq")
            rm_list.append(self.output_dir + "/03.clean_fastq")
        else:
            raise OptionError("split_type有误")
        for files in rm_list:
            if os.path.isfile(files):
                os.remove(files)
                self.logger.info("删除文件{}成功！".format(files))
            elif os.path.isdir(files):
                code = os.system("rm -r {}".format(files))
                if code != 0:
                    self.logger.info("删除文件夹{}失败！".format(files))
            else:
                self.logger.info("文件{}不存在，不用删除！".format(files))

    def end(self):
        self.remove_file()
        result_dir = self.add_upload_dir(self.output_dir)
        result_dir.add_relpath_rules([
            [".","","结果输出目录"]
        ])
        result_dir.add_regexp_rules([
            ["","",""]
        ])
        if self.option("split_id"):
            self.logger.info("更新主表运行状态")
            self.import_pacbio.update_sg_pacbio_status(self.option("split_id"))
        super(PacbioSplitV3Workflow, self).end()


