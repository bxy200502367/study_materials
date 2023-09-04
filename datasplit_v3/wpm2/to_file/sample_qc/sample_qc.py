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

def export_sample_qc_info(data, option_name, dir_path, bind_obj=None):
    """
    导出数据质控的信息表
    """
    split_id = check_objectid(data)
    sg_split_library_collection = db["sg_split_library"]
    sg_split_specimen_collection = db["sg_split_specimen"]
    sg_split_specimem_docs = sg_split_specimen_collection.find({"split_id": split_id})
    sample_qc_info_list = os.path.join(dir_path, "sample_qc_info_list.xls")
    with open(sample_qc_info_list, "w") as w:
        header_list = ["specimen_id", "split_id", "library_id", "library_number", "product_type", "specimen_name", "majorbio_name", "raw_path", "work_path", "analysis_type"]
        w.write("\t".join(header_list))
        w.write("\n")
        for doc in sg_split_specimem_docs:
            specimen_id = doc["_id"].__str__()
            split_id = doc["split_id"].__str__()
            library_id = doc["library_id"].__str__()
            library_number = doc["library_number"]
            product_type = doc["product_type"]
            specimen_name = doc["specimen_name"]
            majorbio_name = doc["majorbio_name"]
            raw_path = doc["raw_path"]
            work_path = doc["work_path"]
            analysis_type = doc["analysis_type"]
            new_line_list = [specimen_id, split_id, library_id, library_number, product_type, specimen_name, majorbio_name, raw_path, work_path, analysis_type]
            w.write("\t".join(new_line_list))
            w.write("\n")
    return sample_qc_info_list

def export_sample_qc_params(data, option_name, dir_path, bind_obj=None):
    """
    导出质控的参数
    """
    split_id = check_objectid(data)
    sg_split_collection = db["sg_split"]
    sg_split_doc = sg_split_collection.find_one({"_id": split_id})
    split_params = json.loads(sg_split_doc["params"])
    sample_qc_params_dir = os.path.join(dir_path, "sample_qc_params_dir")
    make_dir(sample_qc_params_dir)
    # 多样性质控参数
    meta_params = split_params.get("meta", {})
    meta_params_file = os.path.join(sample_qc_params_dir, "meta.json")
    with open(meta_params_file, "w") as w:
        w.write(json.dumps(meta_params) + "\n")
    # rna质控参数
    rna_params = split_params.get("rna", {})
    rna_params_file = os.path.join(sample_qc_params_dir, "rna.json")
    with open(rna_params_file, "w") as w:
        w.write(json.dumps(rna_params) + "\n")
    # mirna质控参数
    mirna_params = split_params.get("mirna", {})
    mirna_params_file = os.path.join(sample_qc_params_dir, "mirna.json")
    with open(mirna_params_file, "w") as w:
        w.write(json.dumps(mirna_params) + "\n")
    # microbial_genome质控参数
    microbial_genome_params = split_params.get("microbial_genome", {})
    microbial_genome_params_file = os.path.join(sample_qc_params_dir, "microbial_genome.json")
    with open(microbial_genome_params_file, "w") as w:
        w.write(json.dumps(microbial_genome_params) + "\n")
    # meta_genomic质控参数
    meta_genomic_params = split_params.get("meta_genomic", {})
    meta_genomic_params_file = os.path.join(sample_qc_params_dir, "meta_genomic.json")
    with open(meta_genomic_params_file, "w") as w:
        w.write(json.dumps(meta_genomic_params) + "\n")
    # prokaryotic_rna质控参数
    prokaryotic_rna_params = split_params.get("prokaryotic_rna", {})
    prokaryotic_rna_params_file = os.path.join(sample_qc_params_dir, "prokaryotic_rna.json")
    with open(prokaryotic_rna_params_file, "w") as w:
        w.write(json.dumps(prokaryotic_rna_params) + "\n")
    # lncrna质控参数
    lncrna_params = split_params.get("lncrna", {})
    lncrna_params_file = os.path.join(sample_qc_params_dir, "lncrna.json")
    with open(lncrna_params_file, "w") as w:
        w.write(json.dumps(lncrna_params) + "\n")
    # dna质控参数
    dna_params = split_params.get("dna", {})
    dna_params_file = os.path.join(sample_qc_params_dir, "dna.json")
    with open(dna_params_file, "w") as w:
        w.write(json.dumps(dna_params) + "\n")
    # self_library质控参数
    self_library_params = split_params.get("self_library", {})
    self_library_params_file = os.path.join(sample_qc_params_dir, "self_library.json")
    with open(self_library_params_file, "w") as w:
        w.write(json.dumps(self_library_params) + "\n")
    return sample_qc_params_dir

def export_mirna_specimen_qc_params(data, option_name, dir_path, bind_obj=None):
    """
    导出每一个样本的mirna质控参数
    """
    split_id = check_objectid(data)
    sg_split_specimen_col = db["sg_split_specimen"]
    sg_split_specimen_doc = sg_split_specimen_col.find({"split_id": split_id})
    mirna_specimen_qc_params = os.path.join(dir_path, "mirna_specimen_qc_params")
    make_dir(mirna_specimen_qc_params)
    for doc in sg_split_specimen_doc:
        library_number = doc["library_number"]
        specimen_name = doc["specimen_name"]
        mirna_qc_params = json.loads(doc["mirna_qc_params"])
        mirna_qc_params_file = os.path.join(mirna_specimen_qc_params, library_number + "--" + specimen_name + ".json")
        with open(mirna_qc_params_file, "w") as w:
            w.write(json.dumps(mirna_qc_params) + "\n")
    return mirna_specimen_qc_params

if __name__ == '__main__':
    #export_library_split_list(data="644799001134104c5539cce2",option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_library_split_params(data="644799001134104c5539cce2", option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_rename_file(data="644799001134104c5539cce2", option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_sample_qc_info(data="64867b79ec82c630a3786752", option_name="",dir_path="/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/to_file/",bind_obj=None)
    #export_sample_qc_params(data="64867b79ec82c630a3786752", option_name="",dir_path="/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/to_file/",bind_obj=None)
    export_mirna_specimen_qc_params(data="64c8a9ed7e18b7701c63a6a3", option_name="",dir_path="/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/to_file/",bind_obj=None)