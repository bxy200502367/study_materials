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

class LibrarySplit(ApiBase):
    def __init__(self, bind_object):
        super(LibrarySplit, self).__init__(bind_object)
        self._project_type = "datasplit"
        self._api_factory.update({
            "update_sg_split": self.update_sg_split,
            "add_sg_split_summary": self.add_sg_split_summary,
            "add_sg_split_lane_summary": self.add_sg_split_lane_summary,
            "add_sg_split_lane_summary_detail": self.add_sg_split_lane_summary_detail,
            "add_sg_split_unknow_barcode": self.add_sg_split_unknow_barcode,
            "update_sg_split_library": self.update_sg_split_library,
            "update_sg_split_specimen": self.update_sg_split_specimen
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
          
    def update_sg_split(self, collection, split_id, library_split_workspace):
        split_id = self.check_objectid(split_id)
        query_dict = {
          "split_id": split_id
          }
        update_dict = {
          "library_split_workspace": library_split_workspace
        }
        self.db[collection].update_one(query_dict, {"$set": update_dict})
        
    def add_sg_split_summary(self, collection, split_id, library_result_dir):
        #datasplit_mongo_url = "mongodb://datasplit:m329ak8k39fm@10.11.1.102,10.11.1.106,10.11.1.110/datasplit?authMechanism=SCRAM-SHA-1"
        #client = pymongo.MongoClient(datasplit_mongo_url)
        #db = client["datasplit"]
        #sg_split_summary_collection = db["sg_split_summary"]
        split_id = self.check_objectid(split_id)
        lane_library_result_dir = [os.path.join(library_result_dir,i) for i in os.listdir(library_result_dir) if os.path.isdir(os.path.join(library_result_dir, i))]
        for dir in lane_library_result_dir:
            lane_match = os.path.basename(dir)
            lane_html = os.path.join(dir, "Reports", "lane.html")
            self.check_exists(lane_html)
            parser = HtmlFile()
            parser.set_path(lane_html)
            parser.get_info()
            tab_list = parser.tab_list
            insert_data = {
                "split_id": split_id,
                "lane": lane_match,
                "clusters_raw": tab_list[1][1][0],
                "clusters_pf": tab_list[1][1][1],
                "yield_nbases": tab_list[1][1][2],
                "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if self.db[collection].find({"split_id": split_id, "lane":lane_match}).count() == 0:
                self.db[collection].insert_one(insert_data)
            else:
                self.db[collection].update_one({"split_id": split_id, "lane":lane_match}, {'$set': insert_data}, upsert=True)
            self.bind_object.logger.info("lane {} 导入flowcell_summary成功".format(lane_match))
    
    def add_sg_split_lane_summary(self, collection, split_id, library_result_dir):
        lane_library_result_dir = [os.path.join(library_result_dir,i) for i in os.listdir(library_result_dir) if os.path.isdir(os.path.join(library_result_dir, i))]
        split_id = self.check_objectid(split_id)
        for dir in lane_library_result_dir:
            lane_match = os.path.basename(dir)
            lane_html = os.path.join(dir, "Reports", "lane.html")
            self.check_exists(lane_html)
            parser = HtmlFile()
            parser.set_path(lane_html)
            parser.get_info()
            tab_list = parser.tab_list
            for info in tab_list[2][1:]:
                insert_data = {
                    "split_id": split_id,
                    "lane": info[0],
                    "clusters_pf": info[1],
                    "lane_rate": info[2],
                    "perfect_barcode_rate": info[3],
                    "mis_barcode": info[4],
                    "yield": info[5],
                    "clusters_pf_rate": info[6],
                    "base_q30": info[7],
                    "quality_score": info[8],
                    "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                if self.db[collection].find({"split_id": split_id, "lane":lane_match}).count() == 0:
                    self.db[collection].insert_one(insert_data)
                else:
                    self.db[collection].update_one({"split_id": split_id, "lane":lane_match}, {'$set': insert_data}, upsert=True)
            self.bind_object.logger.info("lane {} 导入lane_summary成功".format(lane_match))
    
    def add_sg_split_lane_summary_detail(self, collection, split_id, library_result_dir):
        split_id = self.check_objectid(split_id)
        lane_library_result_dir = [os.path.join(library_result_dir,i) for i in os.listdir(library_result_dir) if os.path.isdir(os.path.join(library_result_dir, i))]
        for dir in lane_library_result_dir:
            lane_match = os.path.basename(dir)
            lane_barcode_html = os.path.join(dir, "Reports", "laneBarcode.html")
            self.check_exists(lane_barcode_html)
            parser2 = HtmlFile()
            parser2.set_path(lane_barcode_html)
            parser2.get_info()
            tab_list2 = parser2.tab_list
            for info in tab_list2[2][1:]:
                insert_data = {
                    "split_id": split_id,
                    "lane": info[0],
                    "project": info[1],
                    "library_name": info[2],
                    "barcode_seq": info[3],
                    "clusters_pf": info[4],
                    "lane_rate": info[5],
                    "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                if len(info) == 7:
                    insert_data["perfect_barcode"] = ""
                    insert_data["mis_barcode"] = ""
                    insert_data["yield"] = info[6]
                    insert_data["clusters_pf_rate"] = ""
                    insert_data["base_q30"] = ""
                    insert_data["quality_score"] = ""
                else:
                    insert_data["perfect_barcode"] = info[6]
                    insert_data["mis_barcode"] = info[7]
                    insert_data["yield"] = info[8]
                    insert_data["clusters_pf_rate"] = info[9]
                    insert_data["base_q30"] = info[10]
                    insert_data["quality_score"] = info[11]
                if self.db[collection].find({"split_id": split_id, "lane":lane_match, "library_name": info[2]}).count() == 0:
                    self.db[collection].insert_one(insert_data)
                else:
                    self.db[collection].update_one({"split_id": split_id, "lane":lane_match,"library_name": info[2]}, {'$set': insert_data}, upsert=True)
            self.bind_object.logger.info("lane {} 导入lane_summary_detail成功".format(lane_match))
    
    def add_sg_split_unknow_barcode(self, collection, split_id, library_result_dir):
        split_id = self.check_objectid(split_id)
        lane_library_result_dir = [os.path.join(library_result_dir,i) for i in os.listdir(library_result_dir) if os.path.isdir(os.path.join(library_result_dir, i))]
        for dir in lane_library_result_dir:
            lane_match = os.path.basename(dir)
            lane_barcode_html = os.path.join(dir, "Reports", "laneBarcode.html")
            self.check_exists(lane_barcode_html)
            parser2 = HtmlFile()
            parser2.set_path(lane_barcode_html)
            parser2.get_info()
            tab_list2 = parser2.tab_list
            head = tab_list2[3][1]
            lane_list = []
            for i in range(len(head) / 3):
                lane_list.append(head[i*3])
            revise_table_list = list(filter(None, tab_list2[3][1:])) #去空列表
            for info in revise_table_list:
                if len(info) == len(head):
                    for i in range(len(lane_list)):
                        lane = lane_list[i]
                        insert_data = {
                            "split_id": split_id,
                            "lane": lane,
                            "count": info[i*3+1],
                            "squence": info[i*3+2],
                            "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        if self.db[collection].find({"split_id": split_id, "lane":lane_match, "squence": info[i*3+2]}).count() == 0:
                            self.db[collection].insert_one(insert_data)
                        else:
                            self.db[collection].update_one({"split_id": split_id, "lane":lane_match, "squence": info[i*3+2]}, {'$set': insert_data}, upsert=True)
                else:
                    for i in range(len(lane_list)):
                        lane = lane_list[i]
                        insert_data = {
                            "split_id": split_id,
                            "lane": lane,
                            "count": info[i*2],
                            "squence": info[i*2+1],
                            "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        if self.db[collection].find({"split_id": split_id, "lane":lane_match, "squence": info[i*2+1]}).count() == 0:
                            self.db[collection].insert_one(insert_data)
                        else:
                            self.db[collection].update_one({"split_id": split_id, "lane":lane_match, "squence": info[i*2+1]}, {'$set': insert_data}, upsert=True)
            self.bind_object.logger.info("lane {} 导入top_unknown_barcodesl成功".format(lane_match))
        self.bind_object.logger.info("一次拆分结果导入成功")
    
    def update_sg_split_library(self, collection, split_id, library_result_dir, library_info_dir, s3_upload_dir):
        split_id = self.check_objectid(split_id)
        lane_library_result_dir = [os.path.join(library_result_dir,i) for i in os.listdir(library_result_dir) if os.path.isdir(os.path.join(library_result_dir, i))]
        for dir in lane_library_result_dir:
            lane_match = os.path.basename(dir)
            library_info_path = os.path.join(library_info_dir, lane_match + "." + "library_info.xls")
            library_dir_expect_dict = {}
            with open(library_info_path, "r") as f:
                f_csv = csv.reader(f, delimiter="\t")
                headers = next(f_csv)
                library_info_nt = namedtuple('library_info_nt', headers)
                for row in f_csv:
                    each_row = library_info_nt(*row)
                    library_dir_expect_dict[each_row.lane_name + "_" + each_row.library_number] = (each_row.lane_name, each_row.library_number)
            for library_fastq_dir in os.listdir(dir):
                query_dict = {
                    "split_id": split_id,
                    "lane_name": library_dir_expect_dict[library_fastq_dir][0],
                    "library_number": library_dir_expect_dict[library_fastq_dir][1]
                }
                library_fastq_dir_path = os.path.join(dir, library_fastq_dir)
                for file in os.listdir(library_fastq_dir_path):
                    if operator.contains(file, '_R1_') and not operator.contains(file, 'R2.raw'):
                        R1_fastq_file = file
                    elif operator.contains(file, 'R1.raw'):
                        R1_fastq_file = file
                    elif operator.contains(file, 'md5sum'):
                        md5sum_file = file
                    elif operator.contains(file, '_R2_'):
                        R2_fastq_file = file
                    elif operator.contains(file, "R2.raw"):
                        R2_fastq_file = file
                    else:
                        continue
                R1_s3_fastq_file = os.path.join(s3_upload_dir, lane_match, library_fastq_dir, R1_fastq_file)
                R2_s3_fastq_file = os.path.join(s3_upload_dir, lane_match, library_fastq_dir, R2_fastq_file)
                md5sum_dict = {}
                with open(os.path.join(library_fastq_dir_path, md5sum_file), "r") as f:
                    for line in f:
                        line_list = line.rstrip().split("  ")
                        md5sum_dict[line_list[1]] = line_list[0]
                update_dict = {
                    "path": R1_s3_fastq_file + ";" + R2_s3_fastq_file,
                    "work_path": os.path.join(library_fastq_dir_path, R1_fastq_file) + ";" + os.path.join(library_fastq_dir_path, R2_fastq_file),
                    "md5sum": md5sum_dict[R1_fastq_file] + ";" + md5sum_dict[R2_fastq_file],
                    "bytes": str(os.path.getsize(os.path.join(library_fastq_dir_path, R1_fastq_file))) + ";" + str(os.path.getsize(os.path.join(library_fastq_dir_path, R2_fastq_file))),
                    "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.db[collection].update_one(query_dict, {"$set": update_dict})
            self.bind_object.logger.info("lane {} 导入sg_split_library成功".format(lane_match))
        self.bind_object.logger.info("文库路径更新成功!")
            
    def update_sg_split_specimen(self, collection, split_id, library_result_dir, library_info_dir, s3_upload_dir):
        split_id = self.check_objectid(split_id)
        lane_library_result_dir = [os.path.join(library_result_dir,i) for i in os.listdir(library_result_dir) if os.path.isdir(os.path.join(library_result_dir, i))]
        for dir in lane_library_result_dir:
            lane_match = os.path.basename(dir)
            library_info_path = os.path.join(library_info_dir, lane_match + "." + "library_info.xls")
            library_dir_expect_dict = {}
            with open(library_info_path, "r") as f:
                f_csv = csv.reader(f, delimiter="\t")
                headers = next(f_csv)
                library_info_nt = namedtuple('library_info_nt', headers)
                for row in f_csv:
                    each_row = library_info_nt(*row)
                    library_dir_expect_dict[each_row.lane_name + "_" + each_row.library_number] = (each_row.lane_name, each_row.library_number)
            for library_fastq_dir in os.listdir(dir):
                query_dict = {
                    "split_id": split_id,
                    "library_number": library_dir_expect_dict[library_fastq_dir][1]
                }
                library_fastq_dir_path = os.path.join(dir, library_fastq_dir)
                for file in os.listdir(library_fastq_dir_path):
                    if operator.contains(file, '_R1_') and not operator.contains(file, 'R2.raw'):
                        R1_fastq_file = file
                    elif operator.contains(file, 'R1.raw'):
                        R1_fastq_file = file
                    elif operator.contains(file, 'md5sum'):
                        md5sum_file = file
                    elif operator.contains(file, '_R2_'):
                        R2_fastq_file = file
                    elif operator.contains(file, "R2.raw"):
                        R2_fastq_file = file
                    else:
                        continue
                R1_fastq_file_path = os.path.join(library_fastq_dir_path, R1_fastq_file)
                R2_fastq_file_path = os.path.join(library_fastq_dir_path, R2_fastq_file)
                R1_s3_fastq_file = os.path.join(s3_upload_dir, lane_match, library_fastq_dir, R1_fastq_file)
                R2_s3_fastq_file = os.path.join(s3_upload_dir, lane_match, library_fastq_dir, R2_fastq_file)
                md5sum_dict = {}
                with open(os.path.join(library_fastq_dir_path, md5sum_file), "r") as f:
                    for line in f:
                        line_list = line.rstrip().split("  ")
                        md5sum_dict[line_list[1]] = line_list[0]
                sg_split_specimen_records = self.db[collection].find(query_dict)
                if sg_split_specimen_records.count() == 1:
                    r1_raw_bytes = os.path.getsize(R1_fastq_file_path)
                    r2_raw_bytes = os.path.getsize(R2_fastq_file_path)
                    update_dict = {
                        "raw_md5sum": md5sum_dict[R1_fastq_file] + ";" + md5sum_dict[R2_fastq_file],
                        "raw_path": R1_s3_fastq_file + ";" + R2_s3_fastq_file,
                        "work_path": R1_fastq_file_path + ";" + R2_fastq_file_path,
                        "raw_bytes": str(r1_raw_bytes) + ";" + str(r2_raw_bytes),
                        "created_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.db[collection].update_one(query_dict, {"$set": update_dict})
            self.bind_object.logger.info("lane {} 更新sg_split_specimen成功".format(lane_match))
        self.bind_object.logger.info("非多样性样本更新成功!")
        
    
    def add_flowcell_summary(self, collection, query_dict, lane_html, lane_barcode_html):
        """
        用于更新表格的字段，暂时只是简单的更新一个表的对应字段，后面有需求再进行完善
        :param collection: 集合的名称
        :param query_dict: 查询的字段，可以有多个字段进行联合查询, 是一个字典
        :param query_dict: lane_html
        :param lane_barcode_html: lane_barcode_html
        :return:
        """
        self.check_exists(lane_html)
        self.check_exists(lane_barcode_html)
        parser = HtmlFile()
        parser.set_path(lane_html)
        parser.get_info()
        tab_list = parser.tab_list
        split_id = self.check_objectid(split_id)
        insert_data = {
            "split_id": split_id,
            "clusters_raw": tab_list[1][1][0],
            "clusters_pf": tab_list[1][1][1],
            "yield_nbases": tab_list[1][1][2]
        }
        self.db["sg_split_summary"].insert_one(insert_data)
        self.bind_object.logger.info("导入flowcell_summary成功")
        data_list = []
        for info in tab_list[2][1:]:
            insert_data = {
                "split_id": split_id,
                "lane": info[0],
                "clusters_pf": info[1],
                "lane_rate": info[2],
                "perfect_barcode_rate": info[3],
                "mis_barcode": info[4],
                "yield": info[5],
                "clusters_pf_rate": info[6],
                "base_q30": info[7],
                "quality_score": info[8]
            }
            data_list.append(insert_data)
        self.db["sg_split_lane_summary"].insert_many(data_list)
        self.bind_object.logger.info("导入lane_summary成功")
        parser2 = HtmlFile()
        parser2.set_path(lane_barcode_html)
        parser2.get_info()
        tab_list2 = parser2.tab_list
        data_list = []
        for info in tab_list2[2][1:]:
            insert_data = {
                "split_id": split_id,
                "lane": info[0],
                "project": info[1],
                "library_name": info[2],
                "barcode_seq": info[3],
                "clusters_pf": info[4],
                "lane_rate": info[5]
            }
            if len(info) == 7:
                insert_data["perfect_barcode"] = ""
                insert_data["mis_barcode"] = ""
                insert_data["yield"] = info[6]
                insert_data["clusters_pf_rate"] = ""
                insert_data["base_q30"] = ""
                insert_data["quality_score"] = ""
            else:
                insert_data["perfect_barcode"] = info[6]
                insert_data["mis_barcode"] = info[7]
                insert_data["yield"] = info[8]
                insert_data["clusters_pf_rate"] = info[9]
                insert_data["base_q30"] = info[10]
                insert_data["quality_score"] = info[11]
            data_list.append(insert_data)
        self.db["sg_split_lane_summary_detail"].insert_many(data_list)
        self.bind_object.logger.info("导入lane_summary_detail成功")
        data_list = []  # 第四张表格有点特殊，第一列合并lane,需要进行一些处理
        #有点乱码，需要调整
        head = tab_list2[3][1]
        lane_list = []
        for i in range(len(head) / 3):
            lane_list.append(head[i*3])
        revise_table_list = list(filter(None, tab_list2[3][1:])) #去空列表
        for info in revise_table_list:
            if len(info) == len(head):
                for i in range(len(lane_list)):
                    lane = lane_list[i]
                    insert_data = {
                        "split_id": split_id,
                        "lane": lane,
                        "count": info[i*3+1],
                        "squence": info[i*3+2]
                    }
                    data_list.append(insert_data)
            else:
                for i in range(len(lane_list)):
                    lane = lane_list[i]
                    insert_data = {
                        "split_id": split_id,
                        "lane": lane,
                        "count": info[i*2],
                        "squence": info[i*2+1]
                    }
                    data_list.append(insert_data)
        self.db["sg_split_unknow_barcode"].insert_many(data_list)
        self.bind_object.logger.info("导入top_unknown_barcodesl成功")
        self.bind_object.logger.info("一次拆分结果导入成功")