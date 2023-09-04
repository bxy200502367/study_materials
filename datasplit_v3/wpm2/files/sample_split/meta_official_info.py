# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/30
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import csv
from collections import namedtuple
import os
from biocluster.iofile import File
from biocluster.core.exceptions import FileError


class MetaOfficialInfoFile(File):
    """
    空检查,用于指定infile类型的文件夹
    """

    def check(self):
        if super(MetaOfficialInfoFile, self).check():
            self.is_file()
            self.get_info()
            return True
        return False

    def is_file(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isfile(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))
        
    def get_info(self):
        #its_primer = "no"
        #its_primer_info = ["ITS1F_ITS2R", "ITS3F_ITS4R", "ITSF_ITSR", "ITS3F_ITS4OFR", "1737F_2043R",
        #              "1761F_2043R", "ITS1F_2043R", "ITS-J1F_ITS-J2R", "ITS1F_ITS4R", "1761F_ITS2R",
        #              "ITS86F_ITS4R", "ITS2-S2F_ITS4R", "ITS5F_ITS2R"]  # ITS引物
        is_its_primer_list = []
        split_method_list = []
        library_number_list = []
        lane_name_list = []
        library_s3_path_list = []
        library_work_path_list = []
        insert_size_list = []
        primer_list = []
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            sample_info_nt = namedtuple('sample_info_nt', headers)
            for row in f_csv:
                each_row = sample_info_nt(*row)
                lane_name_list.append(each_row.lane_name)
                library_number_list.append(each_row.library_number)
                library_s3_path_list.append(each_row.library_s3_path)
                library_work_path_list.append(each_row.library_work_path)
                insert_size_list.append(each_row.insert_size)
                primer_list.append(each_row.primer)
                split_method_list.append(each_row.split_method)
                is_its_primer_list.append(each_row.is_its_primer)
        if len(set(lane_name_list)) == 1:
            self.set_property("lane_name", lane_name_list[0])
        else:
            raise FileError("meta_official_info文件中有多个lane")
        if len(set(library_number_list)) == 1:
            self.set_property("library_number", library_number_list[0])
        else:
            raise FileError("meta_official_info文件中有多个文库")
        if len(set(library_work_path_list)) == 1:
            fastq_r1_path, fastq_r2_path = library_work_path_list[0].split(";")
            if os.path.exists(fastq_r1_path) and os.path.exists(fastq_r2_path):
                self.set_property("fastq_r1_path", fastq_r1_path)
                self.set_property("fastq_r2_path", fastq_r2_path)
            else:
                if len(set(library_s3_path_list)) == 1:
                    fastq_r1_s3_path, fastq_r2_s3_path = library_s3_path_list[0].split(";")
                    self.set_property("fastq_r1_path", fastq_r1_s3_path)
                    self.set_property("fastq_r2_path", fastq_r2_s3_path)
                else:
                    raise FileError("meta_official_info文件中有多个s3路径")
        else:
            raise FileError("meta_official_info文件中有多个工作路径")
        max_lib_insert_size = max([int(float(i)) for i in set(insert_size_list)])
        if max_lib_insert_size <= 220:
            trim_max_length = str(160)
        elif 220 < max_lib_insert_size < 320:
            trim_max_length = str(200)
        elif 320 <= max_lib_insert_size < 380:
            trim_max_length = str(250)
        elif max_lib_insert_size >= 380:
            trim_max_length = "pass"
        else:
            raise FileError("lib_insert_size有问题")
        if max_lib_insert_size < 200:
            trim_min_length = str(max_lib_insert_size - 20)
        elif max_lib_insert_size >= 200:
            trim_min_length = str(200)
        else:
            raise FileError("lib_insert_size有问题")
        #for primer_name in set(primer_list):
        #    if primer_name in its_primer_info:
        #        trim_max_length = "pass"
        #       its_primer = "yes"
        if len(set(split_method_list)) == 1 and split_method_list[0] != "": # split_method判断
            self.set_property("split_method", split_method_list[0])
        elif len(set(split_method_list)) == 1 and split_method_list[0] == "":
            if max_lib_insert_size > 550:
                self.set_property("split_method", "Single")
            elif max_lib_insert_size <= 550:
                self.set_property("split_method", "Pair")
        else:
            self.set_property("split_method", "Pair")
        if len(set(is_its_primer_list)) == 1 and is_its_primer_list[0] != "": # 判断是不是its_primer序列
            if is_its_primer_list[0] == "no":
                self.set_property("its_primer", "no")
            elif is_its_primer_list[0] == "yes":
                self.set_property("its_primer", "yes")
                trim_max_length = "pass"
            else:
                raise FileError("its_primer 传参既不是yes也不是no")
        else:
            self.set_property("its_primer", "yes")
        self.set_property("trim_max_length", trim_max_length)
        self.set_property("trim_min_length", trim_min_length)
        #self.set_property("its_primer", its_primer)
        self.set_property("max_lib_insert_size", max_lib_insert_size)
            
if __name__ == "__main__":
    a = MetaOfficialInfoFile()
    a.set_path("/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_split/to_file/meta_no_official/230512PE300-M10--MJ230508_59.no_official_meta_info.xls")
    print a.check()
    print a.prop["path"]
    print a.prop["library_number"]
    print a.prop["fastq_r1_path"]
    print a.prop["fastq_r2_path"]