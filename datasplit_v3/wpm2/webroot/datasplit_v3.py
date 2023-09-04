# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230221
# last_modified: 20230221

import os
import web
import json
from bson.objectid import ObjectId
from mainapp.libs.signature import check_sig
from mainapp.models.workflow import Workflow
from mainapp.models.mongo.submit.datasplit.datasplit import Datasplit
from mainapp.controllers.project.datasplit_controller import DatasplitController

class DatasplitV3Action(DatasplitController):
    """
    数据拆分,一次拆分及自动拆分的接口
    """
    @check_sig
    def POST(self):
        data = web.input()
        print data
        params = ["split_id", "data_source"]
        for name in params:
            if not hasattr(data, name):
                info = {"success": False, "info": "参数{}不存,请检查".format(name)}
                return json.dumps(info)
        result = Datasplit("datasplit").coll_find_one("sg_split", {"_id": ObjectId(data.split_id)})
        task_sn = result["task_sn"]
        seq_number = result["board_number"]
        split_status = result["split_status"]
        update_info = {str(data.split_id): "sg_split"}
        if data.data_source == "library":
            options = {"update_info": json.dumps(update_info),
                   "split_id": data.split_id, 
                   "library_info_dir": data.split_id, 
                   "all_sample_info": data.split_id,
                   "self_library_info": data.split_id}
            task_name = "datasplit_v3.library_split"
            to_file = ["datasplit_v3.library_split.library_split.export_library_info_dir(library_info_dir)",
                       "datasplit_v3.library_split.library_split.export_specimen_info(all_sample_info)",
                       "datasplit_v3.library_split.library_split.export_self_library_info(self_library_info)"]
            split_status["first_split"] = "start"
            split_status["cpc"] = "--"
            cpc = "no"
            update_dict = {
                "split_status": split_status,
                "status": "start",
                "cpc": cpc,
                "desc": "开始进行文库拆分"
            }
        elif data.data_source in ["specimen", "meta_raw"]:
            options = {"update_info": json.dumps(update_info),
                       "split_id": data.split_id, 
                       "sample_split_info": data.split_id, 
                       "meta_params": data.split_id}
            task_name = "datasplit_v3.sample_split"
            to_file = ["datasplit_v3.sample_split.sample_split.export_sample_split_info(sample_split_info)",
                       "datasplit_v3.sample_split.sample_split.export_sample_split_params(meta_params)"]
            split_status["second_split"] = "start"
            split_status["cpc"] = "--"
            cpc = "no"
            update_dict = {
                "split_status": split_status,
                "status": "start",
                "cpc": cpc,
                "desc": "开始进行样本拆分"
            }
        else:
            info = {"success": False, "info": "参数数据来源:%s不正确,请检查".format(data.data_source)}
            return json.dumps(info)
        Datasplit("datasplit").update_db_record("sg_split", {"_id": ObjectId(data.split_id)}, update_dict)
        self.set_sheet_data(name=task_name, options=options, table_id=task_sn, to_file=to_file, seq_number=seq_number)
        task_info = super(DatasplitV3Action, self).POST()
        back_result = {"success":False,"info": "返回数据不是json或者dict：{}".format(task_info)}
        try:
            back_result = json.loads(task_info)
        except:
            if isinstance(task_info,dict):
                back_result  =task_info
        if "success" in back_result.keys():
            if back_result["success"] == False:
                if data.data_source == "library":
                    split_status["first_split"] = "failed"
                    update_dict = {
                            "split_status": split_status,
                            "status": "failed",
                            "desc": "{}".format(back_result["info"])
                    }
                # elif data.data_source in ["specimen", "meta_raw"] or split_type == "second_split":
                elif data.data_source in ["specimen", "meta_raw"]:
                    split_status["second_split"] = "failed"
                    update_dict = {
                        "split_status": split_status,
                        "status": "failed",
                        "desc": "{}".format(back_result["info"])
                        }
                # elif data.data_source in ["other_raw", "qc"] or split_type == "qc":
                elif data.data_source in ["other_raw", "qc"]:
                    split_status["qc"] = "failed"
                    update_dict = {
                        "split_status": split_status,
                        "status": "failed",
                        "desc": "{}".format(back_result["info"])
                    }
                elif data.data_source == "cpc":
                    split_status["cpc"] = "failed"
                    update_dict = {
                        "split_status": split_status,
                        "cpc": "failed",
                        "desc": "{}".format(back_result["info"])
                }
                Datasplit("datasplit").update_db_record("sg_split", {"_id": ObjectId(data.split_id)}, update_dict)
        return json.dumps(task_info)