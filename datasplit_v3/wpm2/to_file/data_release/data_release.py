# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/21
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.config import Config
from bson.objectid import ObjectId
import os
import json
import shutil
import re
import types

project_type = "datasplit_v2"
client = Config().get_mongo_client(mtype=project_type)
db = client[Config().get_mongo_dbname(project_type)]


def make_dir(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        pass
    else:
        os.makedirs(dir_path)

def end_num(string):
    #以一个数字结尾字符串
    text = re.compile(r".*[0-9]$")
    if text.match(string):
        return True
    else:
        return False

def check_objectid(id_):
    """
    用于检查并转成成ObjectID
    """
    if not isinstance(id_, ObjectId):
        if isinstance(id_, types.StringTypes):
            id_ = ObjectId(id_)
        else:
            raise Exception("id必须为ObjectId对象或其对应的字符串!")
    return id_

def export_data_release_info(data, option_name, dir_path, bind_obj=None):
    """
        导出一个数据释放单的信息
    """
    #data = "646b2c9aeb83db34354d8dd2"
    release_id = check_objectid(data)
    sg_data_release_col = db["sg_data_release"]
    sg_data_release_specimen_col = db["sg_data_release_specimen"]
    sg_data_release_doc = sg_data_release_col.find_one({"_id": release_id})
    contract_sn = sg_data_release_doc["contract_sn"]
    fx_sn = sg_data_release_doc["fx_sn"]
    sg_data_release_specimen_docs = sg_data_release_specimen_col.find({"main_id": release_id})
    sg_data_release_specimen_num = sg_data_release_specimen_docs.count()
    data_release_info = os.path.join(dir_path, "{}_{}.data_release_info.xls".format(contract_sn, fx_sn))
    with open(data_release_info, "w") as w:
        header_list = ["specimen_id", "sampling_st", "merge_st", "qc_st", "rename_st", "contract_data_size",
                       "sample_name", "sample_rename", "library_type", "product_type", "barcode_name", "barcode_seq", "primer_name",
                       "primer_seq"]
        w.write("\t".join(header_list))
        w.write("\n")
        if sg_data_release_specimen_num > 0:
            for doc in sg_data_release_specimen_docs:
                specimen_id = doc["_id"].__str__()
                sampling_st = doc["sampling_st"].__str__()
                merge_st = doc["merge_st"].__str__()
                qc_st = doc["qc_st"].__str__()
                rename_st = doc["rename_st"].__str__()
                contract_data_size = doc["contract_data_size"]
                sample_name = doc["sample_name"]
                sample_rename = doc["sample_rename"]
                library_type = doc["library_type_name"]
                product_type = doc["product_type"]
                barcode_name = doc["barcode_name"]
                barcode_seq = doc["barcode_seq"]
                primer_name = doc["primer_name"]
                primer_seq = doc["primer_seq"]
                line_list = [specimen_id, sampling_st, merge_st, qc_st, rename_st, contract_data_size, sample_name, sample_rename, library_type,
                             product_type, barcode_name, barcode_seq, primer_name, primer_seq]
                w.write("\t".join(line_list))
                w.write("\n")
        else:
            raise Exception("合同 {} 的 {} 没有样本！".format(contract_sn, fx_sn))
    return data_release_info

def export_merge_info(data, option_name, dir_path, bind_obj=None):
    """
    导出一个数据释放单的合并信息
    """
    #data = "646b2c9aeb83db34354d8dd2"
    release_id = ObjectId(data)
    sg_data_release_col = db["sg_data_release"]
    sg_data_release_specimen_col = db["sg_data_release_specimen"]
    sg_data_release_doc = sg_data_release_col.find_one({"_id": release_id})
    contract_sn = sg_data_release_doc["contract_sn"]
    fx_sn = sg_data_release_doc["fx_sn"]
    sg_data_release_specimen_docs = sg_data_release_specimen_col.find({"main_id": release_id})
    sg_data_release_specimen_num = sg_data_release_specimen_docs.count()
    merge_info_dir = os.path.join(dir_path, "merge_info_dir")
    make_dir(merge_info_dir)
    if sg_data_release_specimen_num > 0:
        for doc in sg_data_release_specimen_docs:
            specimen_id = doc["_id"].__str__()
            merge_samples = doc["merge_samples"]
            sample_name = doc["sample_name"]
            sample_info_list = os.path.join(dir_path, "merge_info_dir", "{}.sample_info.xls".format(sample_name))
            with open(sample_info_list, "w") as w:
                header_list = ["sample_name", "majorbio_sn", "library_name", "lane_name", "raw_path"]
                w.write("\t".join(header_list))
                w.write("\n")
                for sample in merge_samples:
                    sample_name = sample["sample_name"]
                    majorbio_sn = sample["majorbio_sn"]
                    library_name = sample["library_name"]
                    lane_name = sample["lane_name"]
                    raw_path = sample["raw_path"]
                    line_list = [sample_name, majorbio_sn, library_name, lane_name, raw_path]
                    w.write("\t".join(line_list))
                    w.write("\n")
    else:
        raise Exception("合同 {} 的 {} 没有样本！".format(contract_sn, fx_sn))
    return merge_info_dir


def export_merge_info_all(data, option_name, dir_path, bind_obj=None):
    merge_id = check_objectid(data)
    sg_split_specimen_merge_col = db["sg_split_specimen_merge"]
    sg_split_specimen_merge_doc = sg_split_specimen_merge_col.find({"_id": merge_id})
    merge_info_file = os.path.join(dir_path, "merge_info.xls")
    with open(merge_info_file, "w") as w:
        header_list = ["merge_id", "fx_id", "fx_sn", "merge_st", "library_type_name", "product_type", "sample_name", "majorbio_sn", "library_name", "lane_name", "primer_name", "raw_path", "clean_path", "raw75_path"]
        w.write("\t".join(header_list))
        w.write("\n")
        for doc in sg_split_specimen_merge_doc:
            if doc["product_type"] == "" and doc["library_type_name"] == "LncRNA文库":
                product_type = "lncRNA"
            if doc["merge_st"]:
                merge_id = str(doc["_id"])
                fx_id = str(doc["fx_id"])
                fx_sn = doc["fx_sn"]
                merge_st = str(doc["merge_st"])
                library_type_name = doc["library_type_name"]
                product_type = doc["product_type"]
                merge_samples = doc["merge_samples"]
                for sample in merge_samples:
                    sample_name = sample["sample_name"]
                    majorbio_sn = sample["majorbio_sn"]
                    library_name = sample["library_name"]
                    lane_name = sample["lane_name"]
                    primer_name = sample["primer_name"]
                    raw_path = sample["raw_path"]
                    clean_path = sample["clean_path"]
                    raw75_path = sample["raw75_path"]
                    line_list = [merge_id, fx_id, fx_sn, merge_st, library_type_name, product_type, sample_name, majorbio_sn, library_name, lane_name, primer_name, raw_path, clean_path, raw75_path]
                    w.write("\t".join(line_list))
                    w.write("\n")
            else:
                continue
    return merge_info_file
        

if __name__ == '__main__':
    #export_library_split_list(data="644799001134104c5539cce2",option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_library_split_params(data="644799001134104c5539cce2", option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_rename_file(data="644799001134104c5539cce2", option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_data_release_info(data="6476e9bd30cc6916901882a2", option_name="",dir_path="/mnt/lustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/test/",bind_obj=None)
    #export_merge_info(data="6476e9bd30cc6916901882a2", option_name="",dir_path="/mnt/lustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/test/",bind_obj=None)
    export_merge_info_all(data="64bb2fc999eb6667991e3ee4", option_name="", dir_path="/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/to_file/", bind_obj=None)