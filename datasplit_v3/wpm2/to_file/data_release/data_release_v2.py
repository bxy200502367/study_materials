# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/22
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

project_type = "datasplit_v3"
client = Config().get_mongo_client(mtype=project_type, db_version=0)
db = client[Config().get_mongo_dbname(project_type, db_version=0)]


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
    #data = "6465913ae5994944962871b2"
    release_id = check_objectid(data)
    sg_data_release_col = db["sg_data_release"]
    sg_data_release_specimen_col = db["sg_data_release_specimen"]
    sg_split_specimen_col = db["sg_split_specimen"]
    sg_data_release_doc = sg_data_release_col.find_one({"_id": release_id})
    contract_sn = sg_data_release_doc["contract_sn"]
    fx_sn = sg_data_release_doc["fx_sn"]
    sg_data_release_specimen_doc = sg_data_release_specimen_col.find({"main_id": release_id})
    sg_data_release_specimen_num = sg_data_release_specimen_doc.count()
    if sg_data_release_specimen_num > 0:
        pass
    else:
        raise Exception("合同 {} 的 {} 没有样本！".format(contract_sn, fx_sn))
    data_release_info = os.path.join(dir_path, "{}_{}.data_release_info.xls".format(contract_sn, fx_sn))
    with open(data_release_info, "w") as w:
        header_list = ["release_specimen_id", "sampling_st", "merge_st", "qc_st", "rename_st", "rm_primer_st",
                       "contract_data_size","sample_rename", "split_specimen_id","library_number", "product_type", 
                       "specimen_name", "majorbio_name", "barcode_tag", "f_barcode", "r_barcode", "primer", "link_primer",
                       "reverse_primer", "raw_path", "clean_path", "work_path", "clean_work_path", "raw_md5sum", "clean_md5sum", 
                       "raw_bytes", "clean_bytes","raw75_path", "raw75_md5sum", "raw75_bytes"]
        w.write("\t".join(header_list))
        w.write("\n")
        for doc in sg_data_release_specimen_doc:
            release_specimen_id = doc["_id"].__str__()
            sampling_st = doc["sampling_st"].__str__()
            merge_st = doc["merge_st"].__str__()
            qc_st = doc["qc_st"].__str__()
            rename_st = doc["rename_st"].__str__()
            rm_primer_st = str(doc.get("rm_primer_st", "false"))
            contract_data_size = doc["contract_data_size"]
            sample_rename = doc["sample_rename"]
            merge_samples = doc["merge_samples"]
            for sample in merge_samples:
                split_specimen_id = check_objectid(sample["mongo_specimen_id"])
                sg_split_specimen_doc = sg_split_specimen_col.find_one({"_id": split_specimen_id})
                library_number = sg_split_specimen_doc["library_number"]
                product_type = sg_split_specimen_doc["product_type"]
                specimen_name = sg_split_specimen_doc["specimen_name"]
                majorbio_name = sg_split_specimen_doc["majorbio_name"]
                barcode_tag = sg_split_specimen_doc.get("barcode_tag", "")
                f_barcode = sg_split_specimen_doc.get("f_barcode", "")
                r_barcode = sg_split_specimen_doc.get("r_barcode", "")
                primer = sg_split_specimen_doc.get("primer", "")
                link_primer = sg_split_specimen_doc.get("link_primer", "")
                reverse_primer = sg_split_specimen_doc.get("reverse_primer", "")
                raw_path = sg_split_specimen_doc["raw_path"]
                clean_path = sg_split_specimen_doc["clean_path"]
                work_path = sg_split_specimen_doc["work_path"]
                clean_work_path = sg_split_specimen_doc.get("clean_work_path", "")
                raw_md5sum = sg_split_specimen_doc.get("raw_md5sum", "")
                clean_md5sum = sg_split_specimen_doc.get("clean_md5sum", "")
                raw_bytes = sg_split_specimen_doc.get("raw_bytes", "")
                clean_bytes = sg_split_specimen_doc.get("clean_bytes", "")
                raw75_path = sg_split_specimen_doc.get("raw75_path", "")
                raw75_md5sum = sg_split_specimen_doc.get("raw75_md5sum", "")
                raw75_bytes = sg_split_specimen_doc.get("raw75_bytes", "")
                line_list = [release_specimen_id, sampling_st, merge_st, qc_st, rename_st, rm_primer_st, 
                             contract_data_size, sample_rename, str(split_specimen_id), library_number,
                             product_type, specimen_name, majorbio_name, barcode_tag, f_barcode, r_barcode, primer, link_primer, reverse_primer, raw_path, 
                             clean_path, work_path, clean_work_path, raw_md5sum, clean_md5sum, raw_bytes, clean_bytes, raw75_path, raw75_md5sum, raw75_bytes]
                w.write("\t".join(line_list))
                w.write("\n")
    return data_release_info

def export_sample_qc_params(data, option_name, dir_path, bind_obj=None):
    """
    导出质控的参数
    """
    release_id = check_objectid(data)
    sg_data_release_specimen_col = db["sg_data_release_specimen"]
    sg_data_release_specimen_doc = sg_data_release_specimen_col.find({"main_id": release_id})
    sample_qc_params_dir = os.path.join(dir_path, "sample_qc_params_dir")
    make_dir(sample_qc_params_dir)
    for doc in sg_data_release_specimen_doc:
        release_specimen_id = doc["_id"].__str__()
        specimen_qc_params_dir = os.path.join(sample_qc_params_dir, release_specimen_id)
        make_dir(specimen_qc_params_dir)
        qc_params = json.loads(doc["qc_params"])
        # 多样性质控参数
        meta_params = qc_params.get("meta", {})
        meta_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "meta.json")
        with open(meta_params_file, "w") as w:
            w.write(json.dumps(meta_params) + "\n")
        # rna质控参数
        rna_params = qc_params.get("rna", {})
        rna_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "rna.json")
        with open(rna_params_file, "w") as w:
            w.write(json.dumps(rna_params) + "\n")
        # mirna质控参数
        mirna_params = qc_params.get("mirna", {})
        mirna_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "mirna.json")
        with open(mirna_params_file, "w") as w:
            w.write(json.dumps(mirna_params) + "\n")
        # microbial_genome质控参数
        microbial_genome_params = qc_params.get("microbial_genome", {})
        microbial_genome_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "microbial_genome.json")
        with open(microbial_genome_params_file, "w") as w:
            w.write(json.dumps(microbial_genome_params) + "\n")
        # meta_genomic质控参数
        meta_genomic_params = qc_params.get("meta_genomic", {})
        meta_genomic_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "meta_genomic.json")
        with open(meta_genomic_params_file, "w") as w:
            w.write(json.dumps(meta_genomic_params) + "\n")
        # prokaryotic_rna质控参数
        prokaryotic_rna_params = qc_params.get("prokaryotic_rna", {})
        prokaryotic_rna_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "prokaryotic_rna.json")
        with open(prokaryotic_rna_params_file, "w") as w:
            w.write(json.dumps(prokaryotic_rna_params) + "\n")
        # lncrna质控参数
        lncrna_params = qc_params.get("lncrna", {})
        lncrna_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "lncrna.json")
        with open(lncrna_params_file, "w") as w:
            w.write(json.dumps(lncrna_params) + "\n")
        # dna质控参数
        dna_params = qc_params.get("dna", {})
        dna_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "dna.json")
        with open(dna_params_file, "w") as w:
            w.write(json.dumps(dna_params) + "\n")
        # self_library质控参数
        self_library_params = qc_params.get("self_library", {})
        self_library_params_file = os.path.join(sample_qc_params_dir, release_specimen_id, "self_library.json")
        with open(self_library_params_file, "w") as w:
            w.write(json.dumps(self_library_params) + "\n")
    return sample_qc_params_dir
        
if __name__ == '__main__':
    export_data_release_info(data="64c754e10c695d61aa660be3", option_name="", dir_path="/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/to_file/20230731_test/", bind_obj=None)
    export_sample_qc_params(data="64c754e10c695d61aa660be3", option_name="", dir_path="/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/to_file/20230731_test/", bind_obj=None)
