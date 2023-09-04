# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/17
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import datetime
import web
import json
from bson.objectid import ObjectId
from mainapp.libs.signature import check_sig
from mainapp.models.mongo.submit.datasplit.datasplit import Datasplit
from mainapp.controllers.project.datasplit_controller import DatasplitController

class DataReleaseAction(DatasplitController):    
    """
    数据释放接口
    """
    def __init__(self):
        # super(DatasplitSampleMergeRenameAction, self).__init__(instant=True)
        super(DataReleaseAction, self).__init__(instant=False)
        
    @check_sig
    def POST(self):
        data = web.input()
        print("数据释放前端数据")
        print data
        print("数据释放前端数据")
        params = ["release_id"]
        for param in params:
            if not hasattr(data, param):
                info = {"success": False, "info": "Lack argument: {}".format(param)}
                return json.dumps(info)
        result = Datasplit("datasplit_v3").coll_find_one("sg_data_release", {"main_id": ObjectId(data.release_id)})
        print(Datasplit("datasplit_v3"))
        if not result:
            info = {"success": False, "info": "没有在主表sg_data_release里找到main_id: %s有需要释放的样本,请检查" % data.release_id}
            return json.dumps(info)
        update_info = {str(data.release_id): "sg_data_release"}
        options = {
            "update_info": json.dumps(update_info),
            "data_release_info": data.release_id,
            "sample_qc_params_dir": data.release_id,
            "release_id": data.release_id
        }
        to_files = [
            "datasplit_v3.data_release.data_release_v2.export_data_release_info(data_release_info)",
            "datasplit_v3.data_release.data_release_v2.export_sample_qc_params(sample_qc_params_dir)"
            ]
        table_id = "DataRelease_" + data.release_id
        seq_number = "DataRelease"
        self.set_sheet_data_data_release(
            name="datasplit_v3.data_release", 
            options=options, 
            table_id=table_id, 
            to_file=to_files, 
            seq_number=seq_number, 
            module_type="workflow",
            testmod = True,
            cluster = "clustre")
        task_info = super(DataReleaseAction, self).POST()
        update_dict = {
                "status": "start",
                "start_ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "desc": "开始数据释放"
        }
        Datasplit("datasplit_v3").update_db_record("sg_data_release", {"_id": ObjectId(data.release_id)}, update_dict)
        return json.dumps(task_info)