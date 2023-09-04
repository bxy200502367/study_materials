# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/16
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import datetime
import os
import csv
from collections import namedtuple
import re
import json
import types
import operator
import datetime
from bson.objectid import ObjectId
from collections import defaultdict
from biocluster.config import Config
from mbio.files.datasplit_v3.html import HtmlFile
from mbio.api.database.datasplit_v3.api_base import ApiBase
from itertools import islice

class SampleSplit(ApiBase):
    def __init__(self, bind_object):
        super(SampleSplit, self).__init__(bind_object)
        self._project_type = "datasplit"
        self._api_factory.update({
            "add_sg_split_library_qc": self.add_sg_split_library_qc,
            "add_file_info": self.add_file_info,
            "update_sample_split_path": self.update_sample_split_path,
            "update_sample_split_md5sum": self.update_sample_split_md5sum,
            "update_no_meta": self.update_no_meta
            })
        
    def check_objectid(self, id_):
        """
        用于检查并转成成ObjectID
        """
        if not isinstance(id_, ObjectId):
            if isinstance(id_, types.StringTypes):
                id_ = ObjectId(id_)
            else:
                raise Exception("id必须为ObjectId对象或其对应的字符串!")
        return id_

    def check_exists(self, path):
        """
        检查文件是否存在
        """
        if not os.path.exists(path):
            raise Exception("{}所指定的路径不存在，请检查".format(path))
        else:
            return True
        
    def friendly_size(self, size):
        """
        资源转换
        """
        gb = 1000 * 1000 * 1000.0
        mb = 1000 * 1000.0
        kb = 1000.0
        if size > gb:
            new_size = round(float(size) / gb, 4)
            return str(new_size) + "G"
        else:
            new_size = round(float(size) / mb, 4)
            return str(new_size) + "M"

        
    def add_sg_split_library_qc(self, collection, split_id, library_stat_info_dir):
        split_id = self.check_objectid(split_id)
        self.check_exists(library_stat_info_dir)
        for file in os.listdir(library_stat_info_dir):
            with open(os.path.join(library_stat_info_dir, file), "r") as f:
                for line in islice(f, 1, None):
                    line_list = line.strip().split("\t")
                    if len(line_list) == 16:
                        library_number, rank, q20, q30, raw_pair, chimeric, chimeric_rate, valid_pair, valid_rate, pair_trim, \
                        trim_rate, pair_merge, merge_rate, seq_split, split_rate, high_quality_rate = line_list
                        insert_data = {
                            "split_id": split_id,
                            "library_number": library_number,
                            "rank": rank,
                            "q20": float(q20),
                            "q30": float(q30),
                            "raw_pair": int(raw_pair),
                            "chimeric": int(chimeric),
                            "chimeric_rate": float(chimeric_rate),
                            "valid_pair": int(valid_pair),
                            "valid_rate": float(valid_rate),
                            "pair_trim": int(pair_trim),
                            "trim_rate": float(trim_rate),
                            "pair_merge": int(pair_merge),
                            "merge_rate": float(merge_rate),
                            "seq_split": int(seq_split),
                            "split_rate": float(split_rate),
                            "high_quality_rate": float(high_quality_rate),
                            "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        if self.db[collection].find({"split_id": split_id, "library_number":library_number}).count() == 0:
                            self.db[collection].insert_one(insert_data)
                        else:
                            self.db[collection].update_one({"split_id": split_id, "library_number":library_number}, {'$set': insert_data}, upsert=True)
                        self.bind_object.logger.info("library文库 {} 导入 {} 成功".format(library_number, collection))
                    else:
                        raise Exception("lib_stat.xls不为16列")
        self.bind_object.logger.info("split_id {} 导入 {} 成功".format(split_id.__str__(), collection))
        
    def add_file_info(self, collection, split_id, process, info_file):
        split_id = self.check_objectid(split_id)
        self.check_exists(info_file)
        if process == "meta_raw_stat":
            with open(info_file, "r") as f:
                f_csv = csv.reader(f, delimiter="\t")
                headers = next(f_csv)
                meta_raw_info_nt = namedtuple('meta_raw_info_nt', headers)
                for row in f_csv:
                    each_row = meta_raw_info_nt(*row)
                    if len(each_row.Sample_ID.split("--")) == 2: # 官方多样性拆分
                        lane_name, library_number = each_row.Sample_ID.split("--")
                        if self.db["sg_split_specimen"].find({"split_id": split_id, "library_number":library_number}).count() == 1:
                            doc_result= self.db["sg_split_specimen"].find_one({"split_id": split_id, "library_number":library_number})
                            insert_data = {
                                "split_id": split_id,
                                "library_number": library_number,
                                "specimen_name": doc_result["specimen_name"] + "." + doc_result["primer"],
                                "project_sn": doc_result["project_sn"],
                                "product_type": doc_result["product_type"],
                                "insert_len": doc_result["insert_size"],
                                "specimen_id": doc_result["_id"],
                                "seq_model": "PE",
                                "total_reads": int(each_row.Total_Reads),
                                "total_bases": int(each_row.Total_Bases),
                                "raw_data": self.friendly_size(float(each_row.Total_Bases)),
                                "a_rate": float(each_row.A),
                                "t_rate": float(each_row.T),
                                "c_rate": float(each_row.C),
                                "g_rate": float(each_row.G),
                                "n_rate": float(each_row.N),
                                "gc_rate": float(each_row.GC),
                                "q20_rate": float(each_row.Q20),
                                "q30_rate": float(each_row.Q30),
                                "error_rate": float(each_row.Error),
                                "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            if self.db[collection].find({"split_id": split_id, "library_number":library_number}).count() == 0:
                                self.db[collection].insert_one(insert_data)
                            else:
                                self.db[collection].update_one({"split_id": split_id, "library_number":library_number}, {'$set': insert_data}, upsert=True)
                            self.bind_object.logger.info("官方多样性文库 {} 导入 {} 成功".format(library_number, collection))
                        else:
                            raise Exception("文库 {} 不是官方多样性文库".format(library_number))
                    elif len(each_row.Sample_ID.split("--")) == 4:
                        project_sn, library_number, specimen_id, sample_id = each_row.Sample_ID.split("--")
                        doc_result= self.db["sg_split_specimen"].find_one({"split_id": split_id, "library_number":library_number, "_id": ObjectId(specimen_id)})
                        insert_data = {
                                "split_id": split_id,
                                "library_number": library_number,
                                "specimen_name": sample_id,
                                "project_sn": doc_result["project_sn"],
                                "product_type": doc_result["product_type"],
                                "insert_len": doc_result["insert_size"],
                                "specimen_id": doc_result["_id"],
                                "seq_model": "PE",
                                "total_reads": int(each_row.Total_Reads),
                                "total_bases": int(each_row.Total_Bases),
                                "raw_data": self.friendly_size(float(each_row.Total_Bases)),
                                "a_rate": float(each_row.A),
                                "t_rate": float(each_row.T),
                                "c_rate": float(each_row.C),
                                "g_rate": float(each_row.G),
                                "n_rate": float(each_row.N),
                                "gc_rate": float(each_row.GC),
                                "q20_rate": float(each_row.Q20),
                                "q30_rate": float(each_row.Q30),
                                "error_rate": float(each_row.Error),
                                "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                        if self.db[collection].find({"split_id": split_id, "library_number":library_number, "specimen_id": ObjectId(specimen_id)}).count() == 0:
                            self.db[collection].insert_one(insert_data)
                        else:
                            self.db[collection].update_one({"split_id": split_id, "library_number":library_number, "specimen_id": ObjectId(specimen_id)}, {'$set': insert_data}, upsert=True)
                            self.bind_object.logger.info("非官方多样性样本 {} 导入sg_split_raw_qc成功".format(sample_id))
                    else:
                        raise Exception("sample的命名有问题")
            self.bind_object.logger.info("split_id {} 导入sg_split_raw_qc成功".format(split_id.__str__()))
        elif process == "meta_clean_stat":
            with open(info_file, "r") as f:
                f_csv = csv.reader(f, delimiter="\t")
                headers = next(f_csv)
                meta_clean_info_nt = namedtuple('meta_clean_info_nt', headers)
                for row in f_csv:
                    each_row = meta_clean_info_nt(*row)
                    if len(each_row.Sample_ID.split("--")) == 2: # 最后的质控为0
                        lane_name, library_number = each_row.Sample_ID.split("--")
                        doc_results = self.db["sg_split_specimen"].find({"split_id": split_id, "library_number":library_number})
                        for doc in doc_results:
                            specimen_name = doc["specimen_name"] + "." + doc["primer"]
                            insert_data = {
                                "split_id": split_id,
                                "library_number": library_number,
                                "specimen_name": specimen_name,
                                "project_sn": doc["project_sn"],
                                "product_type": doc["product_type"],
                                "insert_len": doc["insert_size"],
                                "specimen_id": doc["_id"],
                                "seq_model": "PE",
                                "total_reads": 0,
                                "total_bases": 0,
                                "clean_data": 0,
                                "a_rate": 0,
                                "t_rate": 0,
                                "c_rate": 0,
                                "g_rate": 0,
                                "n_rate": 0,
                                "gc_rate": 0,
                                "q20_rate": 0,
                                "q30_rate": 0,
                                "error_rate": 0,
                                "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            if self.db[collection].find({"split_id": split_id, "library_number":library_number, "specimen_name": specimen_name}).count() == 0:
                                self.db[collection].insert_one(insert_data)
                            else:
                                self.db[collection].update_one({"split_id": split_id, "library_number":library_number, "specimen_name": specimen_name}, {'$set': insert_data}, upsert=True)
                            self.bind_object.logger.info("结果为空的文库 {} 样本 {} 导入sg_split_clean_qc成功".format(library_number, specimen_name))
                    elif len(each_row.Sample_ID.split("--")) == 4:
                        project_sn, library_number, specimen_id, sample_id = each_row.Sample_ID.split("--")
                        doc_result= self.db["sg_split_specimen"].find_one({"split_id": split_id, "library_number":library_number, "_id": ObjectId(specimen_id)})
                        insert_data = {
                                "split_id": split_id,
                                "library_number": library_number,
                                "specimen_name": sample_id,
                                "project_sn": doc_result["project_sn"],
                                "product_type": doc_result["product_type"],
                                "insert_len": doc_result["insert_size"],
                                "specimen_id": doc_result["_id"],
                                "seq_model": "PE",
                                "total_reads": int(each_row.Total_Reads),
                                "total_bases": int(each_row.Total_Bases),
                                "clean_data": self.friendly_size(float(each_row.Total_Bases)),
                                "a_rate": float(each_row.A),
                                "t_rate": float(each_row.T),
                                "c_rate": float(each_row.C),
                                "g_rate": float(each_row.G),
                                "n_rate": float(each_row.N),
                                "gc_rate": float(each_row.GC),
                                "q20_rate": float(each_row.Q20),
                                "q30_rate": float(each_row.Q30),
                                "error_rate": float(each_row.Error),
                                "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                        if self.db[collection].find({"split_id": split_id, "library_number":library_number, "specimen_id": ObjectId(specimen_id)}).count() == 0:
                            self.db[collection].insert_one(insert_data)
                        else:
                            self.db[collection].update_one({"split_id": split_id, "library_number":library_number, "specimen_id": ObjectId(specimen_id)}, {'$set': insert_data}, upsert=True)
                        self.bind_object.logger.info("多样性样本 {} 导入 {} 成功".format(sample_id, collection))
                    else:
                        raise Exception("sample的命名有问题")
            self.bind_object.logger.info("split_id {} 导入 {} 成功".format(split_id.__str__(), collection))
    
    def update_sample_split_path(self, collection, split_id, process, info_file, s3_upload_dir):
        split_id = self.check_objectid(split_id)
        self.check_exists(info_file)
        if process == "meta_raw_path":
            with open(info_file, "r") as f:
                for line in f:
                    sample_id, r1_work_path = line.strip().split("\t")
                    if r1_work_path.endswith(".R1.fastq.gz"):
                        r2_work_path = r1_work_path.replace(".R1.fastq.gz", ".R2.fastq.gz")
                    elif r1_work_path.endswith(".R1.raw.fastq.gz"):
                        r2_work_path = r1_work_path.replace(".R1.raw.fastq.gz", ".R2.raw.fastq.gz")
                    else:
                        continue
                    r1_size = str(os.path.getsize(r1_work_path))
                    r2_size = str(os.path.getsize(r2_work_path))
                    r1_basename = os.path.basename(r1_work_path)
                    r2_basename = os.path.basename(r2_work_path)
                    raw_r1_path = os.path.join(s3_upload_dir, "meta_raw_data", r1_basename)
                    raw_r2_path = os.path.join(s3_upload_dir, "meta_raw_data", r2_basename)
                    sample_id_list = sample_id.split("--")
                    if len(sample_id_list) == 2: # 官方多样性文库，modified by yuan.xu 20230620,如果是官方多样性文库，不用更新raw_path
                        lane_name, library_number = sample_id_list
                        # if self.db[collection].find({"split_id": split_id, "library_number":library_number}).count() == 1:
                        if self.db["sg_split_library"].find({"split_id": split_id, "lane_name": lane_name, "library_number":library_number}).count() == 1:
                            doc_result= self.db["sg_split_library"].find_one({"split_id": split_id, "lane_name": lane_name, "library_number":library_number})
                            lane_match = doc_result["lane"]
                            update_data = {
                                "work_path": doc_result["work_path"],
                                "raw_bytes": r1_size + ";" + r2_size,
                                "raw_path": doc_result["path"],
                                "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            self.db[collection].update_one({"split_id": split_id, "lane": lane_match, "library_number":library_number}, {'$set': update_data}, upsert=True)
                            self.bind_object.logger.info("官方多样性文库 {} 导入 {} 成功".format(library_number, collection))
                    elif len(sample_id_list) == 4:
                        project_sn, library_number, specimen_id, sample_id = sample_id_list
                        update_data = {
                                "work_path": r1_work_path + ";" + r2_work_path,
                                "raw_bytes": r1_size + ";" + r2_size,
                                "raw_path": raw_r1_path + ";" + raw_r2_path,
                                "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                        self.db[collection].update_one({"split_id": split_id, "library_number":library_number, "_id": ObjectId(specimen_id)}, {'$set': update_data}, upsert=True)
                        self.bind_object.logger.info("非官方多样性文库 {} 的样本 {} 导入 {} 成功".format(library_number, sample_id, collection))
                    else:
                        raise Exception("sample的命名有问题")
            self.bind_object.logger.info("split_id {} 导入 {} 成功".format(split_id.__str__(), collection))
        elif process == "meta_clean_path":
            with open(info_file, "r") as f:
                for line in f:
                    sample_id, clean_work_path = line.strip().split("\t")
                    file_size = str(os.path.getsize(clean_work_path))
                    file_basename = os.path.basename(clean_work_path)
                    clean_path = os.path.join(s3_upload_dir, "meta_clean_data", file_basename)
                    sample_id_list = sample_id.split("--")
                    if len(sample_id_list) == 2: # 为官方多样性文库空文件
                        lane_name, library_number = sample_id_list
                        if self.db[collection].find({"split_id": split_id, "library_number":library_number}).count() == 1:
                            update_data = {
                                "clean_work_path": clean_work_path,
                                "clean_bytes": file_size,
                                "clean_path": clean_path,
                                "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            self.db[collection].update_one({"split_id": split_id, "library_number":library_number}, {'$set': update_data}, upsert=True)
                            self.bind_object.logger.info("官方多样性文库 {} 导入 {} 成功".format(library_number, collection))
                    elif len(sample_id_list) == 4:
                        project_sn, library_number, specimen_id, sample_id = sample_id_list
                        update_data = {
                                "clean_work_path": clean_work_path,
                                "clean_bytes": file_size,
                                "clean_path": clean_path,
                                "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                        self.db[collection].update_one({"split_id": split_id, "library_number":library_number, "_id": ObjectId(specimen_id)}, {'$set': update_data}, upsert=True)
                        self.bind_object.logger.info("多样性文库 {} 的样本 {} 导入 {} 成功".format(library_number, sample_id, collection))
                    else:
                        raise Exception("sample的命名有问题")
            self.bind_object.logger.info("split_id {} 导入 {} 成功".format(split_id.__str__(), collection))
            
    def update_sample_split_md5sum(self, collection, split_id, process, info_file):
        split_id = self.check_objectid(split_id)
        if not os.path.exists(info_file):
            return
        #self.check_exists(info_file)
        if process == "meta_raw_data_md5sum":
            md5sum_dict = {}
            with open(info_file, "r") as f:
                for line in f:
                    md5sum, work_path = line.strip().split("  ")
                    if work_path.endswith(".R1.fastq.gz"):
                        work_path_basename = os.path.basename(work_path).replace(".R1.fastq.gz", "")
                        md5sum_dict.setdefault(work_path_basename, []).append((work_path, md5sum))
                    elif work_path.endswith(".R2.fastq.gz"):
                        work_path_basename = os.path.basename(work_path).replace(".R2.fastq.gz", "")
                        md5sum_dict.setdefault(work_path_basename, []).append((work_path, md5sum))
                    elif work_path.endswith(".R1.raw.fastq.gz"):
                        work_path_basename = os.path.basename(work_path).replace(".R1.raw.fastq.gz", "")
                        md5sum_dict.setdefault(work_path_basename, []).append((work_path, md5sum))
                    elif work_path.endswith(".R2.raw.fastq.gz"):
                        work_path_basename = os.path.basename(work_path).replace(".R2.raw.fastq.gz", "")
                        md5sum_dict.setdefault(work_path_basename, []).append((work_path, md5sum))
            for sample_id, md5_tuple in md5sum_dict.items():
                sample_id_list = sample_id.split("--")
                md5_tuple.sort()
                md5sum_list = [b for a,b in md5_tuple]
                if len(sample_id_list) == 2: # 官方多样性文库
                    lane_name, library_number = sample_id_list
                    if self.db[collection].find({"split_id": split_id, "library_number":library_number}).count() == 1:
                        update_data = {
                            "raw_md5sum": ";".join(md5sum_list),
                            "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        self.db[collection].update_one({"split_id": split_id, "library_number":library_number}, {'$set': update_data}, upsert=True)
                        self.bind_object.logger.info("官方多样性文库 {} 导入 {} 成功".format(library_number, collection))
                    else:
                        raise Exception("拆分任务split_id {} 有多个文库 {}".format(split_id, library_number))
                elif len(sample_id_list) == 4:
                    project_sn, library_number, specimen_id, sample_id = sample_id.split("--")
                    update_data = {
                            "raw_md5sum": ";".join(md5sum_list),
                            "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                    self.db[collection].update_one({"split_id": split_id, "library_number":library_number, "_id": ObjectId(specimen_id)}, {'$set': update_data}, upsert=True)
                    self.bind_object.logger.info("非官方多样性文库 {} 的样本 {} 导入 {} 成功".format(library_number, sample_id, collection))
                else:
                    raise Exception("sample的命名有问题")
            self.bind_object.logger.info("split_id {} 导入 {} 成功".format(split_id.__str__(), collection))
        elif process == "meta_clean_data_md5sum":
            md5sum_dict = {}
            with open(info_file, "r") as f:
                for line in f:
                    md5sum, clean_work_path = line.strip().split("  ")
                    if clean_work_path.endswith(".fastq.gz"):
                        work_path_basename = os.path.basename(clean_work_path).replace(".fastq.gz", "")
                    elif clean_work_path.endswith(".fq.gz"):
                        work_path_basename = os.path.basename(clean_work_path).replace(".fq.gz", "")
                    else:
                        raise Exception("{} 后缀有问题".format(clean_work_path))
                    sample_id_list = work_path_basename.split("--")
                    if len(sample_id_list) == 2: # 为官方多样性文库空文件
                        lane_name, library_number = sample_id_list
                        if self.db[collection].find({"split_id": split_id, "library_number":library_number}).count() == 1:
                            update_data = {
                                "clean_md5sum": md5sum,
                                "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            self.db[collection].update_one({"split_id": split_id, "library_number":library_number}, {'$set': update_data}, upsert=True)
                            self.bind_object.logger.info("官方多样性文库 {} 导入 {} 成功".format(library_number, collection))
                        else:
                            raise Exception("拆分任务split_id {} 有多个文库 {}".format(split_id, library_number))
                    elif len(sample_id_list) == 4:
                        project_sn, library_number, specimen_id, sample_id = sample_id_list
                        update_data = {
                                "clean_md5sum": md5sum,
                                "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                        self.db[collection].update_one({"split_id": split_id, "library_number":library_number, "_id": ObjectId(specimen_id)}, {'$set': update_data}, upsert=True)
                        self.bind_object.logger.info("多样性文库 {} 的样本 {} 导入 {} 成功".format(library_number, sample_id, collection))
                    else:
                        raise Exception("sample的命名有问题")
            self.bind_object.logger.info("split_id {} 导入 {} 成功".format(split_id.__str__(), collection))
            
    def update_no_meta(self, collection, split_id, info_file):
        split_id = self.check_objectid(split_id)
        self.check_exists(info_file)
        count = len(open(info_file,'rU').readlines())
        if count == 1:
            return
        else:   
            with open(info_file, "r") as f:
                f_csv = csv.reader(f, delimiter="\t")
                headers = next(f_csv)
                no_meta_info_nt = namedtuple('no_meta_info_nt', headers)
                for row in f_csv:
                    each_row = no_meta_info_nt(*row)
                    update_data = {
                        "raw_path": each_row.library_s3_path,
                        "work_path": each_row.library_work_path,
                        "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    self.db[collection].update_one({"_id": ObjectId(each_row.specimen_id), "library_number": each_row.library_number}, {'$set': update_data}, upsert=True)
                    self.bind_object.logger.info("非多样性样本 {} 导入 {} 成功".format(each_row.specimen_name, collection))
            self.bind_object.logger.info("非多样性样本路径导表完成")