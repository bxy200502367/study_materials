# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230523
# last modify: 20230523

from biocluster.config import Config
from bson.objectid import ObjectId
import csv
from collections import namedtuple
import re
import operator
import json
import os
import types

project_type = "datasplit"
client = Config().get_mongo_client(mtype=project_type)
db = client[Config().get_mongo_dbname(project_type)]



def make_dir(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        pass
    else:
        os.makedirs(dir_path)

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

def export_sample_split_info(data, option_name, dir_path, bind_obj=None):
    """
    导出数据二拆的信息表
    """
    split_id = check_objectid(data)
    #sample_info_dir = os.path.join(dir_path, "sample_info_dir")
    #make_dir(sample_info_dir)
    sg_barcode_collection = db["sg_barcode"]
    sg_split_library_collection = db["sg_split_library"]
    sg_split_specimen_collection = db["sg_split_specimen"]
    sg_split_docs = sg_split_library_collection.find({"split_id": split_id})
    specimen_info_list = os.path.join(dir_path, "specimen_info_list.xls")
    with open(specimen_info_list, "w") as w:
        header_list = ["specimen_id", "library_id", "lane_name", "library_number", "library_type", "library_s3_path", "library_work_path", 
                       "project_sn", "product_type", "specimen_name", "majorbio_name","insert_size", "barcode_tag", "f_barcode", "r_barcode", 
                       "primer", "link_primer", "reverse_primer", "analysis_type", "meta_type", "split_method", "is_its_primer"] # modified by yuan.xu,20230808,增加两个参数split_method(单端拆分还是双端拆分)和is_its_primer(是否是ITS引物)
        w.write("\t".join(header_list))
        w.write("\n")
        for doc in sg_split_docs:
            library_id = doc["_id"]
            library_lane = doc["lane_name"]
            library_number = doc["library_number"]
            library_type = doc["library_type"]
            if operator.contains(library_type, "双index官方多样性文库"):
                meta_type = "official"
            elif operator.contains(library_type, "Illumina多样性文库"):
                meta_type = "no_official"
            else:
                meta_type = "no_meta"
            library_s3_path = doc["path"]
            try:
              library_work_path = doc["work_path"]
            except:
              library_work_path = ""
            sg_split_specimen_docs = sg_split_specimen_collection.find({"split_id": split_id, "library_id":library_id})
            for specimen_doc in sg_split_specimen_docs:
                specimen_id = specimen_doc["_id"]
                project_sn = specimen_doc["project_sn"]
                product_type = specimen_doc["product_type"]
                specimen_name = specimen_doc["specimen_name"]
                majorbio_name = specimen_doc["majorbio_name"]
                insert_size = str(specimen_doc["insert_size"])
                if meta_type == "official":
                    barcode_tag = specimen_doc["barcode_tag"] if specimen_doc["barcode_tag"] else doc["i7_index_id"]
                    f_barcode = specimen_doc["f_barcode"] if specimen_doc["f_barcode"] else doc["i7_index_seq"]
                    r_barcode = specimen_doc["r_barcode"] if specimen_doc["r_barcode"] else doc["i5_index_seq"]
                elif meta_type == "no_official":
                    barcode_doc = sg_barcode_collection.find_one({"barcode_label": specimen_doc["barcode_tag"]})
                    if not barcode_doc:
                        raise Exception("数据库里没有样本 {} 的barcode: {}".format(specimen_doc["specimen_name"], specimen_doc["barcode_tag"]))
                    barcode_tag = barcode_doc["barcode_tag"]
                    f_barcode = specimen_doc["f_barcode"]
                    r_barcode = specimen_doc["r_barcode"]
                elif meta_type == "no_meta":
                    barcode_tag = specimen_doc["barcode_tag"]
                    f_barcode = specimen_doc["f_barcode"]
                    r_barcode = specimen_doc["r_barcode"]
                primer = specimen_doc["primer"]
                link_primer = specimen_doc["link_primer"]
                reverse_primer = specimen_doc["reverse_primer"]
                analysis_type = specimen_doc["analysis_type"]
                split_method = specimen_doc.get("split_method", "Pair")
                is_its_primer = specimen_doc.get("is_its_primer", "no")
                new_line_list = [specimen_id.__str__(), library_id.__str__(), library_lane, library_number, library_type, library_s3_path, 
                                 library_work_path, project_sn, product_type, specimen_name, majorbio_name, insert_size, barcode_tag, 
                                 f_barcode, r_barcode, primer, link_primer, reverse_primer, analysis_type, meta_type, split_method, is_its_primer]
                w.write("\t".join(new_line_list))
                w.write("\n")
    return specimen_info_list

def export_sample_split_params(data, option_name, dir_path, bind_obj=None):
    """
        导出二拆meta的参数
    """
    split_id = check_objectid(data)
    sg_split_collection = db["sg_split"]
    sg_split_doc = sg_split_collection.find_one({"_id": split_id})
    print "此时的params字段为{}".format(sg_split_doc['params'])
    split_params = json.loads(sg_split_doc["params"])
    meta_params = split_params.get("meta", {})
    meta_params_file = os.path.join(dir_path, "meta.json")
    with open(meta_params_file, "w") as w:
        w.write(json.dumps(meta_params) + "\n")
    return meta_params_file


if __name__ == '__main__':
    #export_library_split_list(data="644799001134104c5539cce2",option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_library_split_params(data="644799001134104c5539cce2", option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_rename_file(data="644799001134104c5539cce2", option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    export_sample_split_info(data="647444ffa853fd0bcc790eb8", option_name="",dir_path="/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_split/to_file/20230531_test/",bind_obj=None)
    export_sample_split_params(data="647444ffa853fd0bcc790eb8", option_name="",dir_path="/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_split/to_file/20230531_test/",bind_obj=None)