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

class DataRelease(ApiBase):
    def __init__(self, bind_object):
        super(DataRelease, self).__init__(bind_object)
        self._project_type = "datasplit_v3"
        self._api_factory.update({
            "update_sg_data_release_specimen": self.update_sg_data_release_specimen,
            "renew_old_col": self.renew_old_col,
            "renew_qc_status": self.renew_qc_status,
            "update_main_status": self.update_main_status
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
          
    def update_sg_data_release_specimen(self, collection, release_id, result_dir, s3_upload_dir):
        release_id = self.check_objectid(release_id)
        release_dir_list = [os.path.join(result_dir,i) for i in os.listdir(result_dir) if os.path.isdir(os.path.join(result_dir, i))]
        for dir in release_dir_list:
            release_specimen_id = self.check_objectid(os.path.basename(dir))
            query_dict = {
                    "_id": release_specimen_id,
                    "main_id":release_id
                }
            product_type = os.listdir(dir)[0]
            if product_type == "mirna":
                process_result_dir = os.path.join(dir, product_type)
                if len(os.listdir(process_result_dir)) == 0:
                    sg_data_release_specimen_doc = self.db[collection].find_one(query_dict)
                    mongo_specimen_id = self.check_objectid(sg_data_release_specimen_doc["merge_samples"][0]["mongo_specimen_id"])
                    sg_split_specimen_doc = self.db["sg_split_specimen"].find_one({"_id": mongo_specimen_id})
                    update_dict = {
                        "release_raw_path": sg_split_specimen_doc["raw_path"],
                        "release_raw_work_path": sg_split_specimen_doc["work_path"],
                        "release_raw_md5sum": sg_split_specimen_doc["raw_md5sum"],
                        "release_raw_bytes": sg_split_specimen_doc["raw_bytes"],
                        "release_clean_path": sg_split_specimen_doc["clean_path"],
                        "release_clean_work_path": sg_split_specimen_doc["clean_work_path"],
                        "release_clean_md5sum": sg_split_specimen_doc["clean_md5sum"],
                        "release_clean_bytes": sg_split_specimen_doc["clean_bytes"],
                        "release_raw75_path": sg_split_specimen_doc["raw75_path"],
                        "release_raw75_md5sum": sg_split_specimen_doc["raw75_md5sum"],
                        "release_raw75_bytes": sg_split_specimen_doc["raw75_bytes"],
                        "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "end"
                    }
                    self.bind_object.logger.info("开始更新需要不需要process的 {} 样本".format(product_type))
                    self.db[collection].update_one(query_dict, {'$set': update_dict}, upsert=True)
                    self.bind_object.logger.info("sg_data_release_specimen的记录 {} 更新成功".format(str(release_specimen_id)))
                else:
                    md5sum_file = os.path.join(dir, product_type, product_type, "md5sum.txt")
                    with open(md5sum_file, "r") as f:
                        for line in f:
                            md5sum, file = line.strip().split("  ")
                            if file.endswith("R1.raw.fastq.gz"):
                                r1_raw_file = os.path.basename(file)
                                r1_raw_md5sum = md5sum
                                r1_raw_bytes = str(os.path.getsize(file))
                            elif file.endswith("R2.raw.fastq.gz"):
                                r2_raw_file = os.path.basename(file)
                                r2_raw_md5sum = md5sum
                                r2_raw_bytes = str(os.path.getsize(file))
                            elif file.endswith("fastq.gz"):
                                raw75_file = os.path.basename(file)
                                raw75_md5sum = md5sum
                                raw75_bytes = str(os.path.getsize(file))
                            elif file.endswith("fasta.gz"):
                                clean_file = os.path.basename(file)
                                clean_md5sum = md5sum
                                clean_bytes = str(os.path.getsize(file))
                            else:
                                continue
                    r1_raw_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r1_raw_file)
                    r1_raw_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r1_raw_file)
                    r2_raw_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r2_raw_file)
                    r2_raw_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r2_raw_file)
                    clean_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, clean_file)
                    clean_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, clean_file)
                    raw75_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, raw75_file)
                    raw75_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, raw75_file)
                    update_dict = {
                        "release_raw_path": r1_raw_file_s3 + ";" + r2_raw_file_s3,
                        "release_raw_work_path": r1_raw_file_work_path + ";" + r2_raw_file_work_path,
                        "release_raw_md5sum": r1_raw_md5sum + ";" + r2_raw_md5sum,
                        "release_raw_bytes": r1_raw_bytes + ";" + r2_raw_bytes,
                        "release_clean_path": clean_file_s3,
                        "release_clean_work_path": clean_file_work_path,
                        "release_clean_md5sum": clean_md5sum,
                        "release_clean_bytes": clean_bytes,
                        "release_raw75_path": raw75_file_s3,
                        "release_raw75_work_path": raw75_file_work_path,
                        "release_raw75_md5sum": raw75_md5sum,
                        "release_raw75_bytes": raw75_bytes,
                        "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "end"
                    }
                    self.bind_object.logger.info("开始更新需要process的 {} 样本".format(product_type))
                    self.db[collection].update_one(query_dict, {'$set': update_dict}, upsert=True)
                    self.bind_object.logger.info("sg_data_release_specimen的记录 {} 更新成功".format(str(release_specimen_id)))
            elif product_type == "meta":
                need_no_primer = False
                process_result_dir = os.path.join(dir, product_type)
                md5sum_file = os.path.join(dir, product_type, product_type, "md5sum.txt")
                with open(md5sum_file, "r") as f:
                    for line in f:
                        md5sum, file = line.strip().split("  ")
                        if file.endswith("R1.noprimer.raw.fastq.gz"):
                            need_no_primer = True
                            r1_raw_no_primer_file = os.path.basename(file)
                            r1_raw_no_primer_md5sum = md5sum
                            r1_raw_no_primer_bytes = str(os.path.getsize(file))
                        if file.endswith("R2.noprimer.raw.fastq.gz"):
                            r2_raw_no_primer_file = os.path.basename(file)
                            r2_raw_no_primer_md5sum = md5sum
                            r2_raw_no_primer_bytes = str(os.path.getsize(file))
                        elif file.endswith("R1.raw.fastq.gz"):
                            r1_raw_file = os.path.basename(file)
                            r1_raw_md5sum = md5sum
                            r1_raw_bytes = str(os.path.getsize(file))
                        elif file.endswith("R2.raw.fastq.gz"):
                            r2_raw_file = os.path.basename(file)
                            r2_raw_md5sum = md5sum
                            r2_raw_bytes = str(os.path.getsize(file))
                        elif file.endswith("clean.fastq.gz"):
                            clean_file = os.path.basename(file)
                            clean_md5sum = md5sum
                            clean_bytes = str(os.path.getsize(file))
                        else:
                            continue
                r1_raw_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r1_raw_file)
                r1_raw_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r1_raw_file)
                r2_raw_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r2_raw_file)
                r2_raw_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r2_raw_file)
                clean_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, clean_file)
                clean_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, clean_file)
                update_dict = {
                    "release_raw_path": r1_raw_file_s3 + ";" + r2_raw_file_s3,
                    "release_raw_work_path": r1_raw_file_work_path + ";" + r2_raw_file_work_path,
                    "release_raw_md5sum": r1_raw_md5sum + ";" + r2_raw_md5sum,
                    "release_raw_bytes": r1_raw_bytes + ";" + r2_raw_bytes,
                    "release_clean_path": clean_file_s3,
                    "release_clean_work_path": clean_file_work_path,
                    "release_clean_md5sum": clean_md5sum,
                    "release_clean_bytes": clean_bytes,
                    "release_raw_no_primer_path": "",
                    "release_raw_no_primer_work_path": "",
                    "release_raw_no_primer_md5sum": "",
                    "release_raw_no_primer_bytes": "",
                    "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "end"
                }
                if need_no_primer:
                    r1_raw_no_primer_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r1_raw_no_primer_file)
                    r1_raw_no_primer_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r1_raw_no_primer_file)
                    r2_raw_no_primer_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r2_raw_no_primer_file)
                    r2_raw_no_primer_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r2_raw_no_primer_file)
                    update_dict.update({
                        "release_raw_no_primer_path": r1_raw_no_primer_file_s3 + ";" + r2_raw_no_primer_file_s3,
                        "release_raw_no_primer_work_path": r1_raw_no_primer_file_work_path + ";" + r2_raw_no_primer_file_work_path,
                        "release_raw_no_primer_md5sum": r1_raw_no_primer_md5sum + ";" + r2_raw_no_primer_md5sum,
                        "release_raw_no_primer_bytes": r1_raw_no_primer_bytes + ";" + r2_raw_no_primer_bytes,
                        "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "end"
                    })
                self.bind_object.logger.info("开始更新需要process的 {} 样本".format(product_type))
                self.db[collection].update_one(query_dict, {'$set': update_dict}, upsert=True)
                self.bind_object.logger.info("sg_data_release_specimen的记录 {} 更新成功".format(str(release_specimen_id)))
            else:
                process_result_dir = os.path.join(dir, product_type)
                sg_data_release_specimen_doc = self.db[collection].find_one(query_dict)
                merge_st = str(sg_data_release_specimen_doc["merge_st"])
                qc_st = str(sg_data_release_specimen_doc["qc_st"])
                #rename_st = sg_data_release_specimen_doc["rename_st"]
                md5sum_file = os.path.join(dir, product_type, product_type, "md5sum.txt")
                if merge_st == "False" and qc_st == "True":
                    mongo_specimen_id = self.check_objectid(sg_data_release_specimen_doc["merge_samples"][0]["mongo_specimen_id"])
                    sg_split_specimen_doc = self.db["sg_split_specimen"].find_one({"_id": mongo_specimen_id})
                    with open(md5sum_file, "r") as f:
                        for line in f:
                            md5sum, file = line.strip().split("  ")
                            if file.endswith("R1.clean.fastq.gz"):
                                r1_clean_file = os.path.basename(file)
                                r1_clean_md5sum = md5sum
                                r1_clean_bytes = str(os.path.getsize(file))
                            elif file.endswith("R2.clean.fastq.gz"):
                                r2_clean_file = os.path.basename(file)
                                r2_clean_md5sum = md5sum
                                r2_clean_bytes = str(os.path.getsize(file))
                            else:
                                continue
                    r1_clean_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r1_clean_file)
                    r1_clean_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r1_clean_file)
                    r2_clean_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r2_clean_file)
                    r2_clean_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r2_clean_file)
                    update_dict = {
                        "release_raw_path": sg_split_specimen_doc["raw_path"],
                        "release_raw_work_path": sg_split_specimen_doc["work_path"],
                        "release_raw_md5sum": sg_split_specimen_doc["raw_md5sum"],
                        "release_raw_bytes": sg_split_specimen_doc["raw_bytes"],
                        "release_clean_path": r1_clean_file_s3 + ";" + r2_clean_file_s3,
                        "release_clean_work_path": r1_clean_file_work_path + ";" + r2_clean_file_work_path,
                        "release_clean_md5sum": r1_clean_md5sum + ";" + r2_clean_md5sum,
                        "release_clean_bytes": r1_clean_bytes + ";" + r2_clean_bytes,
                        "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "end"
                    }
                    self.bind_object.logger.info("开始更新merge_st为False,qc_st为True的 {} 样本".format(product_type))
                    self.db[collection].update_one(query_dict, {'$set': update_dict}, upsert=True)
                    self.bind_object.logger.info("sg_data_release_specimen的记录 {} 更新成功".format(str(release_specimen_id)))
                elif merge_st == "False" and qc_st == "False":
                    mongo_specimen_id = self.check_objectid(sg_data_release_specimen_doc["merge_samples"][0]["mongo_specimen_id"])
                    sg_split_specimen_doc = self.db["sg_split_specimen"].find_one({"_id": mongo_specimen_id})
                    update_dict = {
                        "release_raw_path": sg_split_specimen_doc["raw_path"],
                        "release_raw_work_path": sg_split_specimen_doc["work_path"],
                        "release_raw_md5sum": sg_split_specimen_doc["raw_md5sum"],
                        "release_raw_bytes": sg_split_specimen_doc["raw_bytes"],
                        "release_clean_path": "",
                        "release_clean_work_path": "",
                        "release_clean_md5sum": "",
                        "release_clean_bytes": "",
                        "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "end"
                    }
                    self.bind_object.logger.info("开始更新merge_st为False,qc_st为False的 {} 样本".format(product_type))
                    self.db[collection].update_one(query_dict, {'$set': update_dict}, upsert=True)
                    self.bind_object.logger.info("sg_data_release_specimen的记录 {} 更新成功".format(str(release_specimen_id)))
                elif merge_st == "True" and qc_st == "True":
                    with open(md5sum_file, "r") as f:
                        for line in f:
                            md5sum, file = line.strip().split("  ")
                            if file.endswith("R1.raw.fastq.gz"):
                                r1_raw_file = os.path.basename(file)
                                r1_raw_md5sum = md5sum
                                r1_raw_bytes = str(os.path.getsize(file))
                            if file.endswith("R2.raw.fastq.gz"):
                                r2_raw_file = os.path.basename(file)
                                r2_raw_md5sum = md5sum
                                r2_raw_bytes = str(os.path.getsize(file))
                            elif file.endswith("R1.clean.fastq.gz"):
                                r1_clean_file = os.path.basename(file)
                                r1_clean_md5sum = md5sum
                                r1_clean_bytes = str(os.path.getsize(file))
                            elif file.endswith("R2.clean.fastq.gz"):
                                r2_clean_file = os.path.basename(file)
                                r2_clean_md5sum = md5sum
                                r2_clean_bytes = str(os.path.getsize(file))
                            else:
                                continue
                    r1_raw_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r1_raw_file)
                    r1_raw_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r1_raw_file)
                    r2_raw_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r2_raw_file)
                    r2_raw_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r2_raw_file)
                    r1_clean_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r1_clean_file)
                    r1_clean_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r1_clean_file)
                    r2_clean_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r2_clean_file)
                    r2_clean_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r2_clean_file)
                    update_dict = {
                        "release_raw_path": r1_raw_file_s3 + ";" + r2_raw_file_s3,
                        "release_raw_work_path": r1_raw_file_work_path + ";" + r2_raw_file_work_path,
                        "release_raw_md5sum": r1_raw_md5sum + ";" + r2_raw_md5sum,
                        "release_raw_bytes": r1_raw_bytes + ";" + r2_raw_bytes,
                        "release_clean_path": r1_clean_file_s3 + ";" + r2_clean_file_s3,
                        "release_clean_work_path": r1_clean_file_work_path + ";" + r2_clean_file_work_path,
                        "release_clean_md5sum": r1_clean_md5sum + ";" + r2_clean_md5sum,
                        "release_clean_bytes": r1_clean_bytes + ";" + r2_clean_bytes,
                        "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "end"
                    }
                    self.bind_object.logger.info("开始更新merge_st为True,qc_st为True的 {} 样本".format(product_type))
                    self.db[collection].update_one(query_dict, {'$set': update_dict}, upsert=True)
                    self.bind_object.logger.info("sg_data_release_specimen的记录 {} 更新成功".format(str(release_specimen_id)))
                elif merge_st == "True" and qc_st == "False":
                    with open(md5sum_file, "r") as f:
                        for line in f:
                            md5sum, file = line.strip().split("  ")
                            if file.endswith("R1.raw.fastq.gz"):
                                r1_raw_file = os.path.basename(file)
                                r1_raw_md5sum = md5sum
                                r1_raw_bytes = str(os.path.getsize(file))
                            if file.endswith("R2.raw.fastq.gz"):
                                r2_raw_file = os.path.basename(file)
                                r2_raw_md5sum = md5sum
                                r2_raw_bytes = str(os.path.getsize(file))
                            else:
                                continue
                    r1_raw_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r1_raw_file)
                    r1_raw_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r1_raw_file)
                    r2_raw_file_work_path = os.path.join(result_dir, str(release_specimen_id), product_type, product_type, r2_raw_file)
                    r2_raw_file_s3 = os.path.join(s3_upload_dir, str(release_specimen_id), product_type, product_type, r2_raw_file)
                    update_dict = {
                        "release_raw_path": r1_raw_file_s3 + ";" + r2_raw_file_s3,
                        "release_raw_work_path": r1_raw_file_work_path + ";" + r2_raw_file_work_path,
                        "release_raw_md5sum": r1_raw_md5sum + ";" + r2_raw_md5sum,
                        "release_raw_bytes": r1_raw_bytes + ";" + r2_raw_bytes,
                        "release_clean_path": "",
                        "release_clean_work_path": "",
                        "release_clean_md5sum": "",
                        "release_clean_bytes": "",
                        "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "end"
                    }
                    self.bind_object.logger.info("开始更新merge_st为True,qc_st为False的 {} 样本".format(product_type))
                    self.db[collection].update_one(query_dict, {'$set': update_dict}, upsert=True)
                    self.bind_object.logger.info("sg_data_release_specimen的记录 {} 更新成功".format(str(release_specimen_id)))
            self.bind_object.logger.info("sg_data_release_specimen更新成功!")
            
    def renew_old_col(self, collection, main_id):
        main_id = self.check_objectid(main_id)
        sg_data_release_specimen_doc = self.db[collection].find({"main_id": main_id})
        for doc in sg_data_release_specimen_doc:
            sg_split_specimen_merge_id = doc.get("sg_split_specimen_merge_id", "")
            sg_split_specimen_rename_id = doc.get("sg_split_specimen_rename_id", "")
            sg_qc_specimen_id = doc.get("sg_qc_specimen_id", "")
            if sg_split_specimen_merge_id:
                query_dict = {
                    "_id": self.check_objectid(sg_split_specimen_merge_id)
                }
                update_dict = {
                    "raw_path": doc["release_raw_path"],
                    "raw_work_path": doc["release_raw_work_path"],
                    "raw_md5sum": doc["release_raw_md5sum"],
                    "raw_bytes": doc["release_raw_bytes"],
                    "clean_path": doc.get("release_clean_path", ""),
                    "clean_work_path": doc.get("release_clean_work_path", ""),
                    "clean_md5sum": doc.get("release_clean_md5sum", ""),
                    "clean_bytes": doc.get("release_clean_bytes", ""),
                    "raw75_path": doc.get("release_raw75_path", ""),
                    "raw75_work_path": doc.get("release_raw75_work_path", ""),
                    "raw75_md5sum": doc.get("release_raw75_md5sum", ""),
                    "raw75_bytes": doc.get("release_raw75_bytes", ""),
                    "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "end"
                }
                self.bind_object.logger.info("开始更新sg_split_specimen_merge表 {} 记录".format(sg_split_specimen_merge_id))
                self.db["sg_split_specimen_merge"].update_one(query_dict, {'$set': update_dict})
                self.bind_object.logger.info("sg_split_specimen_merge的记录 {} 更新成功".format(sg_split_specimen_merge_id))
            if sg_split_specimen_rename_id:
                query_dict = {
                    "_id": self.check_objectid(sg_split_specimen_rename_id)
                }
                update_dict = {
                    "raw_path": doc["release_raw_path"],
                    "raw_work_path": doc["release_raw_work_path"],
                    "raw_md5sum": doc["release_raw_md5sum"],
                    "raw_bytes": doc["release_raw_bytes"],
                    "clean_path": doc.get("release_clean_path", ""),
                    "clean_work_path": doc.get("release_clean_work_path", ""),
                    "clean_md5sum": doc.get("release_clean_md5sum", ""),
                    "clean_bytes": doc.get("release_clean_bytes", ""),
                    "raw75_path": doc.get("release_raw75_path", ""),
                    "raw75_work_path": doc.get("release_raw75_work_path", ""),
                    "raw75_md5sum": doc.get("release_raw75_md5sum", ""),
                    "raw75_bytes": doc.get("release_raw75_bytes", ""),
                    "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "end"
                }
                self.bind_object.logger.info("开始更新sg_split_specimen_merge表 {} 记录".format(sg_split_specimen_rename_id))
                self.db["sg_split_specimen_rename"].update_one(query_dict, {'$set': update_dict})
                self.bind_object.logger.info("sg_split_specimen_merge的记录 {} 更新成功".format(sg_split_specimen_rename_id))
            if sg_qc_specimen_id:
                query_dict = {
                    "_id": self.check_objectid(sg_qc_specimen_id)
                }
                update_dict = {
                    "raw_path": doc["release_raw_path"],
                    "raw_work_path": doc["release_raw_work_path"],
                    "raw_md5sum": doc["release_raw_md5sum"],
                    "raw_bytes": doc["release_raw_bytes"],
                    "clean_path": doc.get("release_clean_path", ""),
                    "clean_work_path": doc.get("release_clean_work_path", ""),
                    "clean_md5sum": doc.get("release_clean_md5sum", ""),
                    "clean_bytes": doc.get("release_clean_bytes", ""),
                    "raw75_path": doc.get("release_raw75_path", ""),
                    "raw75_work_path": doc.get("release_raw75_work_path", ""),
                    "raw75_md5sum": doc.get("release_raw75_md5sum", ""),
                    "raw75_bytes": doc.get("release_raw75_bytes", ""),
                    "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "end"
                }
                self.bind_object.logger.info("开始更新sg_qc_specimen表 {} 记录".format(sg_qc_specimen_id))
                self.db["sg_qc_specimen"].update_one(query_dict, {'$set': update_dict})
                self.bind_object.logger.info("sg_qc_specimen的记录 {} 更新成功".format(sg_qc_specimen_id))
        self.bind_object.logger.info("旧表更新成功!")
        
    def renew_qc_status(self, collection, main_id):
        main_id = self.check_objectid(main_id)
        sg_data_release_specimen_doc = self.db[collection].find_one({"main_id": main_id})
        sg_qc_id = sg_data_release_specimen_doc.get("sg_qc_id", "")
        if sg_qc_id:
            query_dict = {
                    "_id": self.check_objectid(sg_qc_id)
            }
            update_dict = {
                    "update_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "end"
            }
            self.bind_object.logger.info("开始更新sg_qc表 {} 记录".format(sg_qc_id))
            self.db["sg_qc"].update_one(query_dict, {'$set': update_dict})
            self.bind_object.logger.info("sg_qc的记录 {} 更新成功".format(sg_qc_id))
        self.bind_object.logger.info("sg_qc表更新成功!")
        
    def update_main_status(self, collection, main_id):
        main_id = self.check_objectid(main_id)
        query_dict = {
                    "_id": self.check_objectid(main_id)
                    }
        update_dict = {
                    "end_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "desc": "数据释放处理结束",
                    "status": "end"
                    }
        self.bind_object.logger.info("开始更新 sg_data_release 主表状态".format(str(main_id)))
        self.db[collection].update_one(query_dict, {'$set': update_dict})
        self.bind_object.logger.info("sg_data_release 状态更新成功".format(str(main_id)))