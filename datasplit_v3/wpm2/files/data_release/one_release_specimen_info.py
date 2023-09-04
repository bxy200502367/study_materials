# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/24
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.iofile import File
from biocluster.core.exceptions import FileError
import csv
import os
from collections import namedtuple

class OneReleaseSpecimenInfoFile(File):
    """
    name: one_release_specimen_info
    Description: |
        多列，以制表符分隔
    Props:
        tuple_number: int类型, 合并的样本数
        sample_id: str, 样本编号
        r1_paths_str: str, r1的字符串
        r2_paths_str: str, r2的字符串
    """
    def check(self):
        if super(OneReleaseSpecimenInfoFile, self).check():
            self.get_info()
            return True
        return False

    def get_info(self):
        super(OneReleaseSpecimenInfoFile, self).get_info()
        self.check_one_specimen_params()
        one_specimen_info_list = self.check_one_specimen_info()
        self.set_property("tuple_number", len(one_specimen_info_list))
        specimen_name_list = []
        sample_id_list = []
        r1_path_list = []
        r2_path_list = []
        r1_clean_path_list = []
        r2_clean_path_list = []
        raw75_path_list = []
        for path in one_specimen_info_list:
            specimen_name, sample_id, r1_path, r2_path, r1_clean_path, r2_clean_path, raw75_path = path
            specimen_name_list.append(specimen_name)
            sample_id_list.append(sample_id)
            r1_path_list.append(r1_path)
            if r2_path != None:
                r2_path_list.append(r2_path)
            r1_clean_path_list.append(r1_clean_path)
            if r2_clean_path != None:
                r2_clean_path_list.append(r2_clean_path)
            raw75_path_list.append(raw75_path)
        exist_workpath_clean_r1_list = [True for fastq in r1_clean_path_list if fastq.startswith("s3")]
        exist_workpath_clean_r2_list = [True for fastq in r2_clean_path_list if fastq.startswith("s3")]
        exist_s3_clean = any(exist_workpath_clean_r1_list + exist_workpath_clean_r2_list)
        self.set_property("exist_s3_clean", exist_s3_clean)
        if len(set(sample_id_list)) == 1:
            specimen_name = specimen_name_list[0]
            sample_id = sample_id_list[0]
            r1_paths_str = ";".join(r1_path_list)
            if r2_path_list == []:
                r2_paths_str = None
            else:
                r2_paths_str = ";".join(r2_path_list)
            r1_clean_paths_str = ";".join(r1_clean_path_list)
            if r2_clean_path_list == []:
                r2_clean_paths_str = None
            else:
                r2_clean_paths_str = ";".join(r2_clean_path_list)
            raw75_paths_str = ";".join(raw75_path_list)
            self.set_property("specimen_name", specimen_name)
            self.set_property("sample_id", sample_id)
            self.set_property("r1_paths_str", r1_paths_str)
            self.set_property("r2_paths_str", r2_paths_str)
            self.set_property("r1_clean_paths_str", r1_clean_paths_str)
            self.set_property("r2_clean_paths_str", r2_clean_paths_str)
            self.set_property("raw75_paths_str", raw75_paths_str)
        else:
            raise FileError("一个释放样本有多个sample_id {}".format(";".join(sample_id_list)))

    def check_one_specimen_info(self):
        """
        检查函数
        """
        one_specimen_info_list = []
        clean_workpath_exist = "yes"
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            specimen_info_nt = namedtuple('specimen_info_nt', headers)
            for row in f_csv:
                each_row = specimen_info_nt(*row)
                sample_id = "--".join([each_row.majorbio_name, each_row.release_specimen_id, each_row.specimen_name])
                specimen_name = each_row.specimen_name
                if len(each_row.work_path.split(";")) == 2:
                    r1_path, r2_path = each_row.work_path.split(";")
                    if os.path.exists(r1_path) and os.path.exists(r2_path):
                        r1_path, r2_path = each_row.work_path.split(";")
                    else:
                        r1_path, r2_path = each_row.raw_path.split(";")
                elif each_row.work_path.split(";") == [""] and len(each_row.raw_path.split(";")) == 2: # 判断work_path是不是空字符串；如果是则直接用raw_path
                    r1_path, r2_path = each_row.raw_path.split(";")
                elif each_row.work_path.split(";") == [""] and len(each_row.raw_path.split(";")) == 1:
                    r1_path = each_row.raw_path
                    r2_path = None
                elif len(each_row.work_path.split(";")) == 1:
                    r1_path = each_row.work_path
                    r2_path = None
                    if os.path.exists(r1_path):
                        r1_path = each_row.work_path
                        r2_path = None
                    else:
                        r1_path = each_row.raw_path
                        r2_path = None
                else:
                    raise FileError("有超过两个样本的raw_fastq文件")
                if len(each_row.clean_work_path.split(";")) == 2:
                    r1_clean_path, r2_clean_path = each_row.clean_work_path.split(";")
                    if os.path.exists(r1_clean_path) and os.path.exists(r2_clean_path):
                        r1_clean_path, r2_clean_path = each_row.clean_work_path.split(";")
                    else:
                        r1_clean_path, r2_clean_path = each_row.clean_path.split(";")
                elif each_row.clean_work_path.split(";") == [""] and len(each_row.clean_path.split(";")) == 2: # 判断work_path是不是空字符串；如果是则直接用raw_path
                    r1_clean_path, r2_clean_path = each_row.clean_path.split(";")
                elif each_row.clean_work_path.split(";") == [""] and len(each_row.clean_path.split(";")) == 1:
                    r1_clean_path = each_row.clean_path
                    r2_clean_path = None
                elif len(each_row.clean_work_path.split(";")) == 1:
                    r1_clean_path = each_row.work_path
                    r2_clean_path = None
                    if os.path.exists(r1_clean_path):
                        r1_clean_path = each_row.clean_work_path
                        r2_clean_path = None
                    else:
                        r1_clean_path = each_row.clean_path
                        r2_clean_path = None
                else:
                    raise FileError("有超过两个样本的fastq文件")
                raw75_path = each_row.raw75_path
                one_specimen_info_list.append((specimen_name, sample_id , r1_path, r2_path, r1_clean_path, r2_clean_path, raw75_path))
        return one_specimen_info_list

    def check_one_specimen_params(self):
        """
        将释放的参数输出
        """
        data_release_params_list= []
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            specimen_info_nt = namedtuple('specimen_info_nt', headers)
            sampling_st_list = []
            merge_st_list = []
            qc_st_list = []
            rename_st_list = []
            rm_primer_st_list = []
            contract_data_size_list = []
            product_type_list = []
            sample_rename_list = []
            barcode_tag_list = []
            f_barcode_list = []
            r_barcode_list = []
            primer_list = []
            link_primer_list =[]
            reverse_primer_list = []
            for row in f_csv:
                each_row = specimen_info_nt(*row)
                sampling_st = each_row.sampling_st
                sampling_st_list.append(sampling_st)
                merge_st = each_row.merge_st
                merge_st_list.append(merge_st)
                qc_st = each_row.qc_st
                qc_st_list.append(qc_st)
                rename_st = each_row.rename_st
                rename_st_list.append(rename_st)
                rm_primer_st = each_row.rm_primer_st
                rm_primer_st_list.append(rm_primer_st)
                contract_data_size = each_row.contract_data_size
                contract_data_size_list.append(contract_data_size)
                product_type = each_row.product_type
                product_type_list.append(product_type)
                sample_rename = each_row.sample_rename
                sample_rename_list.append(sample_rename)
                barcode_tag = each_row.barcode_tag
                barcode_tag_list.append(barcode_tag)
                f_barcode = each_row.f_barcode
                f_barcode_list.append(f_barcode)
                r_barcode = each_row.r_barcode
                r_barcode_list.append(r_barcode)
                primer = each_row.primer
                primer_list.append(primer)
                link_primer = each_row.link_primer
                link_primer_list.append(link_primer)
                reverse_primer = each_row.reverse_primer
                reverse_primer_list.append(reverse_primer)
            if len(set(sampling_st_list)) == 1:
                self.set_property("sampling_st", sampling_st_list[0])
            else:
                raise FileError("参数状态不对:有超过两个sampling_st")
            if len(set(merge_st_list)) == 1:
                self.set_property("merge_st", merge_st_list[0])
            else:
                raise FileError("参数状态不对:有超过两个merge_st")
            if len(set(qc_st_list)) == 1:
                self.set_property("qc_st", qc_st_list[0])
            else:
                raise FileError("参数状态不对:有超过两个qc_st")
            if len(set(rename_st_list)) == 1:
                self.set_property("rename_st", rename_st_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的rename_st")
            if len(set(rm_primer_st_list)) == 1:
                self.set_property("rm_primer_st", rm_primer_st_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的rm_primer_st")
            if len(set(product_type_list)) == 1:
                self.set_property("product_type", product_type_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的product_type")
            if len(set(contract_data_size_list)) == 1:
                self.set_property("contract_data_size", contract_data_size_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的contract_data_size")
            if len(set(sample_rename_list)) == 1:
                self.set_property("sample_rename", sample_rename_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的sample_rename")
            if len(set(barcode_tag_list)) == 1:
                self.set_property("barcode_tag", barcode_tag_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的barcode_tag")
            if len(set(f_barcode_list)) == 1:
                self.set_property("f_barcode", f_barcode_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的f_barcode")
            if len(set(r_barcode_list)) == 1:
                self.set_property("r_barcode", r_barcode_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的r_barcode")
            if len(set(primer_list)) == 1:
                self.set_property("primer", primer_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的primer")
            if len(set(link_primer_list)) == 1:
                self.set_property("link_primer", link_primer_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的link_primer")
            if len(set(reverse_primer_list)) == 1:
                self.set_property("reverse_primer", reverse_primer_list[0])
            else:
                raise FileError("参数状态不对:有超过两个的reverse_primer")
            

if __name__ == "__main__":
    a = OneReleaseSpecimenInfoFile()
    a.set_path("/mnt/clustre/users/sanger-dev/wpm2/workspace/20230727/DataRelease_data_release-20230727-test02/output/00.data_release_info_dir/64659adee5994944962871b3.data_release_info.xls")
    print a.check()
    print a.prop["path"]
    print a.prop["specimen_name"]
    print a.prop["sample_id"]
    print a.prop["tuple_number"]
    print a.prop["r1_paths_str"]
    print a.prop["r2_paths_str"]
    print a.prop["r1_clean_paths_str"]
    print a.prop["r2_clean_paths_str"]
    print a.prop["sampling_st"]
    print a.prop["merge_st"]
    print a.prop["qc_st"]
    print a.prop["rename_st"]
    print a.prop["product_type"]
    print a.prop["contract_data_size"]
    print a.prop["sample_rename"]
    print a.prop["barcode_tag"]
    print a.prop["f_barcode"]
    print a.prop["r_barcode"]
    print a.prop["primer"]
    print a.prop["link_primer"]
    print a.prop["reverse_primer"]
    print a.prop["exist_s3_clean"]