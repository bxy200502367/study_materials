# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230202
# last modify: 20230202

from biocluster.config import Config
from bson.objectid import ObjectId
import os
import json
import shutil
import re

project_type = "datasplit"
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

def export_library_split_list(data, option_name, dir_path, bind_obj=None):
    """
        导出一拆的信息列表,每条lane一个文件，如果有多个lane则为多个文件
    """
    print data
    print option_name
    print bind_obj
    split_id = ObjectId(data)
    sg_split_collection = db["sg_split"]
    sg_board_lane_collection = db["sg_board_lane"]
    sg_split_library_collection = db["sg_split_library"]
    sg_split_record = sg_split_collection.find_one({"_id": split_id})
    board_id = sg_split_record["board_id"]
    split_params = json.loads(sg_split_record["params"])
    library_split_params = split_params["library_split"]
    for lane_name, lane_info in library_split_params.items():
        lane_name = lane_info["lane_name"]
        lane_match = lane_info["lane_match"]
        lane_seq_model = lane_info["seq_model"]
        # 通过board_id和lane_name从sg_board_lane获取lane_id
        if len(lane_seq_model.split(",")) == 3:
            split_type = "SE"
        elif lane_seq_model.split(",")[1] == "i6nnn":
            split_type = "SE"
        #elif "i6nn" in lane_seq_model:
            #split_type = "SE"
        elif lane_seq_model.split(",")[2].startswith("n") and lane_seq_model.split(",")[2].endswith("n"):
            split_type = "SE"
        elif end_num(lane_seq_model.split(",")[2]):
            split_type = "PE"
        else:
            split_type = "PE"
        split_info_dir = os.path.join(dir_path, "library_info_dir")
        make_dir(split_info_dir)
        library_info_list = os.path.join(dir_path, "library_info_dir", "{}.library_info.xls".format(lane_match))
        sg_board_lane_record = sg_board_lane_collection.find_one({"board_id": board_id, "lane_name": lane_name})
        lane_id = sg_board_lane_record["_id"]
        # 通过split_id,lane_name从sg_split_library获取信息生产library_split_info文件
        sg_split_library_records = sg_split_library_collection.find({"split_id": split_id, "board_id": board_id, "lane_name": lane_name})
        library_num = sg_split_library_records.count()
        if library_num > 0:
            if split_type == "PE":
                with open(library_info_list, "w") as w:
                    header_list = ["split_library_id", "split_id", "board_id", "lane_id", "library_id", "lane_name",
                                   "lane_match", "library_number", "library_type", "specimen_num", "index_id", "index",
                                   "index_id2", "index2"]
                    w.write("\t".join(header_list))
                    w.write("\n")
                    for record in sg_split_library_records:
                        record_split_library_id = record["_id"].__str__()
                        record_split_id = record["split_id"].__str__()
                        record_board_id = record["board_id"].__str__()
                        record_lane_id = lane_id.__str__()
                        record_library_id = record["origin_id"].__str__()
                        record_lane_name = record["lane_name"]
                        record_lane_match = lane_match
                        record_library_number = record["library_number"]
                        record_library_type = record["library_type"]
                        record_specimen_num = str(len(record["specimens"]))
                        record_index_id_i7 = record["i7_index_id"]
                        record_index_seq_i7 = record["i7_index_seq"]
                        record_index_id_i5 = record["i5_index_id"]
                        record_index_seq_i5 = record["i5_index_seq"]
                        if lane_seq_model.split(",")[1].startswith("i6"):
                            index_i7 = record_index_seq_i7[:6]
                        elif lane_seq_model.split(",")[1].startswith("i8"):
                            index_i7 = record_index_seq_i7[:8]
                        elif end_num(lane_seq_model.split(",")[1]):
                            slice_num = int(lane_seq_model.split(",")[1][-1])
                            index_i7 = record_index_seq_i7[-slice_num:]
                        else:
                            index_i7 = record_index_seq_i7
                        if lane_seq_model.split(",")[2].startswith("i6"):
                            index_i5 = record_index_seq_i5[:6]
                        elif lane_seq_model.split(",")[2].startswith("i8"):
                            index_i5 = record_index_seq_i5[:8]
                        elif end_num(lane_seq_model.split(",")[2]):
                            slice_num = int(lane_seq_model.split(",")[2][-1])
                            index_i5 = record_index_seq_i5[-slice_num:]
                        else:
                            index_i5 = record_index_seq_i5
                        line_list = [record_split_library_id, record_split_id, record_board_id, record_lane_id, record_library_id,
                                     record_lane_name, record_lane_match, record_library_number, record_library_type,
                                     record_specimen_num, record_index_id_i7, index_i7, record_index_id_i5, index_i5]
                        w.write("\t".join(line_list))
                        w.write("\n")
            elif split_type == "SE":
                with open(library_info_list, "w") as w:
                    header_list = ["split_library_id", "split_id", "board_id", "lane_id", "library_id", "lane_name",
                                   "lane_match", "library_number", "library_type", "specimen_num", "index_id", "index"]
                    w.write("\t".join(header_list))
                    w.write("\n")
                    for record in sg_split_library_records:
                        record_split_library_id = record["_id"].__str__()
                        record_split_id = record["split_id"].__str__()
                        record_board_id = record["board_id"].__str__()
                        record_lane_id = lane_id.__str__()
                        record_library_id = record["origin_id"].__str__()
                        record_lane_name = record["lane_name"]
                        record_lane_match = lane_match
                        record_library_number = record["library_number"]
                        record_library_type = record["library_type"]
                        record_specimen_num = str(len(record["specimens"]))
                        record_index_id_i7 = record["i7_index_id"]
                        record_index_seq_i7 = record["i7_index_seq"]
                        if "i8" in lane_seq_model:
                            index_i7 = record_index_seq_i7[:8]
                        elif "i6" in lane_seq_model:
                            index_i7 = record_index_seq_i7[:6]
                        else:
                            index_i7 = record_index_seq_i7
                        line_list = [record_split_library_id, record_split_id, record_board_id, record_lane_id, record_library_id,
                                     record_lane_name, record_lane_match, record_library_number, record_library_type,
                                     record_specimen_num, record_index_id_i7, index_i7]
                        w.write("\t".join(line_list))
                        w.write("\n")
            else:
                raise Exception("split_type不为SE也不为PE")

def export_library_split_params(data, option_name, dir_path, bind_obj=None):
    """
        导出一拆的拆分参数信息
    """
    print data
    print option_name
    print bind_obj
    split_id = ObjectId(data)
    sg_split_collection = db["sg_split"]
    sg_split_record = sg_split_collection.find_one({"_id": split_id})
    split_params = json.loads(sg_split_record["params"])
    library_split_params = split_params["library_split"]
    split_info_dir = os.path.join(dir_path, "library_info_dir")
    make_dir(split_info_dir)
    for lane_name, lane_info in library_split_params.items():
        lane_name = lane_info["lane_name"]
        lane_match = lane_info["lane_match"]
        lane_seq_model = lane_info["seq_model"]
        lane_mismatch = lane_info["mismatch"]
        lane_ignore_error = lane_info["ignore_error"]
        lane_split_path = lane_info["split_path"]
        library_split_params_one_file = os.path.join(dir_path, "library_info_dir", "{}.library_split.json".format(lane_match))
        library_split_params_one = {
            "lane_match": lane_match,
            "bases_mask": lane_seq_model,
            "barcode_mismatch": lane_mismatch,
            "ignore_error": lane_ignore_error,
            "sample_sheet": os.path.join(dir_path, "library_info_dir", "{}.library_info.xls".format(lane_match)),
            "data_path": lane_split_path
        }
        with open(library_split_params_one_file, "w") as w:
            w.write(json.dumps(library_split_params_one) + "\n")

def export_rename_file(data, option_name, dir_path, bind_obj=None):
    print data
    print option_name
    print bind_obj
    split_id = ObjectId(data)
    sg_split_collection = db["sg_split"]
    sg_split_library_collection = db["sg_split_library"]
    sg_split_specimen_collection = db["sg_split_specimen"]
    sg_split_record = sg_split_collection.find_one({"_id": split_id})
    board_id = sg_split_record["board_id"]
    split_params = json.loads(sg_split_record["params"])
    library_split_params = split_params["library_split"]
    for lane_name, lane_info in library_split_params.items():
        rename_info = {}
        lane_name = lane_info["lane_name"]
        lane_match = lane_info["lane_match"]
        split_info_dir = os.path.join(dir_path, "library_info_dir")
        make_dir(split_info_dir)
        rename_file = os.path.join(dir_path, "library_info_dir", "{}.rename.xls".format(lane_match))
        # 通过split_id,board_id和lane_name从sg_split_library获取信息改名信息
        sg_split_library_records = sg_split_library_collection.find({"split_id": split_id, "board_id": board_id, "lane_name": lane_name})
        library_num = sg_split_library_records.count()
        if library_num > 0:
            for record in sg_split_library_records:
                sg_split_specimen_records = sg_split_specimen_collection.find({"split_id": split_id, "library_id": record["_id"]})
                if sg_split_specimen_records.count() == 1:
                    if lane_match not in rename_info:
                        rename_info[lane_match] = []
                    if sg_split_specimen_records[0]["product_type"] != "meta":
                        specimen_name = sg_split_specimen_records[0]["specimen_name"]
                    else:
                        specimen_name = sg_split_specimen_records[0]["specimen_name"] + "." + sg_split_specimen_records[0]["primer"]
                    sample_id = record["sample_id"]
                    rename_info[lane_match].append({"sample_id": sample_id, "library_number": sg_split_specimen_records[0]["library_number"],
                                        "project_sn": sg_split_specimen_records[0]["project_sn"], "specimen_name": specimen_name})
                else:
                    if lane_match not in rename_info:
                        rename_info[lane_match] = []
                    else:
                        continue
            with open(rename_file, "w") as w:
                w.write(json.dumps(rename_info) + "\n")

def export_library_info_dir(data, option_name, dir_path, bind_obj=None):
    split_id = ObjectId(data)
    sg_split_collection = db["sg_split"]
    sg_board_lane_collection = db["sg_board_lane"]
    sg_split_library_collection = db["sg_split_library"]
    sg_split_specimen_collection = db["sg_split_specimen"]
    sg_split_record = sg_split_collection.find_one({"_id": split_id})
    board_id = sg_split_record["board_id"]
    split_params = json.loads(sg_split_record["params"])
    library_split_params = split_params["library_split"]
    for lane_name, lane_info in library_split_params.items():
        rename_info = {}
        lane_name = lane_info["lane_name"]
        lane_match = lane_info["lane_match"]
        lane_seq_model = lane_info["seq_model"]
        lane_mismatch = lane_info["mismatch"]
        lane_ignore_error = lane_info["ignore_error"]
        lane_split_path = lane_info["split_path"]
        split_info_dir = os.path.join(dir_path, "library_info_dir")
        make_dir(split_info_dir)
        # 通过board_id和lane_name从sg_board_lane获取lane_id
        library_split_params_one_file = os.path.join(dir_path, "library_info_dir", "{}.library_split.json".format(lane_match))
        library_split_params_one = {
            "lane_name": lane_name, 
            "lane_match": lane_match,
            "bases_mask": lane_seq_model,
            "barcode_mismatch": lane_mismatch if lane_mismatch else 0,
            "ignore_error": lane_ignore_error,
            "sample_sheet": os.path.join(dir_path, "library_info_dir", "{}.library_info.xls".format(lane_match)),
            "data_path": lane_split_path
        }
        with open(library_split_params_one_file, "w") as w:
            w.write(json.dumps(library_split_params_one) + "\n")
        if len(lane_seq_model.split(",")) == 3:
            split_type = "SE"
        elif lane_seq_model.split(",")[1] == "i6nnn":
            split_type = "SE"
        #elif "i6nn" in lane_seq_model:
            #split_type = "SE"
        elif lane_seq_model.split(",")[2].startswith("n") and lane_seq_model.split(",")[2].endswith("n"):
            split_type = "SE"
        elif end_num(lane_seq_model.split(",")[2]):
            split_type = "PE"
        else:
            split_type = "PE"
        library_info_list = os.path.join(dir_path, "library_info_dir", "{}.library_info.xls".format(lane_match))
        sg_board_lane_record = sg_board_lane_collection.find_one({"board_id": board_id, "lane_name": lane_name})
        lane_id = sg_board_lane_record["_id"]
        # 通过split_id,lane_name从sg_split_library获取信息生产library_split_info文件
        sg_split_library_records = sg_split_library_collection.find({"split_id": split_id, "board_id": board_id, "lane_name": lane_name})
        library_num = sg_split_library_records.count()
        rename_file = os.path.join(dir_path, "library_info_dir", "{}.rename.xls".format(lane_match))
        if library_num > 0:
            if split_type == "PE":
                with open(library_info_list, "w") as w:
                    header_list = ["split_library_id", "split_id", "board_id", "lane_id", "library_id", "lane_name",
                                   "lane_match", "library_number", "library_type", "specimen_num", "index_id", "index",
                                   "index_id2", "index2"]
                    w.write("\t".join(header_list))
                    w.write("\n")
                    for record in sg_split_library_records:
                        record_split_library_id = record["_id"].__str__()
                        record_split_id = record["split_id"].__str__()
                        record_board_id = record["board_id"].__str__()
                        record_lane_id = lane_id.__str__()
                        record_library_id = record["origin_id"].__str__()
                        record_lane_name = record["lane_name"]
                        record_lane_match = lane_match
                        record_library_number = record["library_number"]
                        record_library_type = record["library_type"]
                        try:
                            record_specimen_num = str(len(record["specimens"]))
                        except:
                            record_specimen_num = "unknown"
                        record_index_id_i7 = record["i7_index_id"]
                        record_index_seq_i7 = record["i7_index_seq"]
                        record_index_id_i5 = record["i5_index_id"]
                        record_index_seq_i5 = record["i5_index_seq"]
                        if lane_seq_model.split(",")[1].startswith("i6"):
                            index_i7 = record_index_seq_i7[:6]
                        elif lane_seq_model.split(",")[1].startswith("i8"):
                            index_i7 = record_index_seq_i7[:8]
                        elif end_num(lane_seq_model.split(",")[1]):
                            slice_num = int(lane_seq_model.split(",")[1][-1])
                            index_i7 = record_index_seq_i7[-slice_num:]
                        else:
                            index_i7 = record_index_seq_i7
                        if lane_seq_model.split(",")[2].startswith("i6"):
                            index_i5 = record_index_seq_i5[:6]
                        elif lane_seq_model.split(",")[2].startswith("i8"):
                            index_i5 = record_index_seq_i5[:8]
                        elif end_num(lane_seq_model.split(",")[2]):
                            slice_num = int(lane_seq_model.split(",")[2][-1])
                            index_i5 = record_index_seq_i5[-slice_num:]
                        else:
                            index_i5 = record_index_seq_i5
                        line_list = [record_split_library_id, record_split_id, record_board_id, record_lane_id, record_library_id,
                                     record_lane_name, record_lane_match, record_library_number, record_library_type,
                                     record_specimen_num, record_index_id_i7, index_i7, record_index_id_i5, index_i5]
                        w.write("\t".join(line_list))
                        w.write("\n")
                        sg_split_specimen_records = sg_split_specimen_collection.find(
                            {"split_id": split_id, "library_id": record["_id"]})
                        if sg_split_specimen_records.count() == 1:
                            if lane_match not in rename_info:
                                rename_info[lane_match] = []
                            if sg_split_specimen_records[0]["product_type"] != "meta":
                                specimen_name = sg_split_specimen_records[0]["specimen_name"]
                            else:
                                specimen_name = sg_split_specimen_records[0]["specimen_name"] + "." + \
                                                sg_split_specimen_records[0]["primer"]
                            sample_id = record["sample_id"]
                            rename_info[lane_match].append({"sample_id": sample_id,
                                                            "library_number": sg_split_specimen_records[0][
                                                                "library_number"],
                                                            "project_sn": sg_split_specimen_records[0]["project_sn"],
                                                            "specimen_name": specimen_name})
                        else:
                            if lane_match not in rename_info:
                                rename_info[lane_match] = []
                            else:
                                continue
                    with open(rename_file, "w") as w:
                        w.write(json.dumps(rename_info) + "\n")
            elif split_type == "SE":
                with open(library_info_list, "w") as w:
                    header_list = ["split_library_id", "split_id", "board_id", "lane_id", "library_id", "lane_name",
                                   "lane_match", "library_number", "library_type", "specimen_num", "index_id", "index"]
                    w.write("\t".join(header_list))
                    w.write("\n")
                    for record in sg_split_library_records:
                        record_split_library_id = record["_id"].__str__()
                        record_split_id = record["split_id"].__str__()
                        record_board_id = record["board_id"].__str__()
                        record_lane_id = lane_id.__str__()
                        record_library_id = record["origin_id"].__str__()
                        record_lane_name = record["lane_name"]
                        record_lane_match = lane_match
                        record_library_number = record["library_number"]
                        record_library_type = record["library_type"]
                        try:
                            record_specimen_num = str(len(record["specimens"]))
                        except:
                            record_specimen_num = "unknown"
                        record_index_id_i7 = record["i7_index_id"]
                        record_index_seq_i7 = record["i7_index_seq"]
                        if "i8" in lane_seq_model:
                            index_i7 = record_index_seq_i7[:8]
                        elif "i6" in lane_seq_model:
                            index_i7 = record_index_seq_i7[:6]
                        else:
                            index_i7 = record_index_seq_i7
                        line_list = [record_split_library_id, record_split_id, record_board_id, record_lane_id, record_library_id,
                                     record_lane_name, record_lane_match, record_library_number, record_library_type,
                                     record_specimen_num, record_index_id_i7, index_i7]
                        w.write("\t".join(line_list))
                        w.write("\n")
                        sg_split_specimen_records = sg_split_specimen_collection.find(
                            {"split_id": split_id, "library_id": record["_id"]})
                        if sg_split_specimen_records.count() == 1:
                            if lane_match not in rename_info:
                                rename_info[lane_match] = []
                            if sg_split_specimen_records[0]["product_type"] != "meta":
                                specimen_name = sg_split_specimen_records[0]["specimen_name"]
                            else:
                                specimen_name = sg_split_specimen_records[0]["specimen_name"] + "." + \
                                                sg_split_specimen_records[0]["primer"]
                            sample_id = record["sample_id"]
                            rename_info[lane_match].append({"sample_id": sample_id,
                                                            "library_number": sg_split_specimen_records[0][
                                                                "library_number"],
                                                            "project_sn": sg_split_specimen_records[0]["project_sn"],
                                                            "specimen_name": specimen_name})
                        else:
                            if lane_match not in rename_info:
                                rename_info[lane_match] = []
                            else:
                                continue
                    with open(rename_file, "w") as w:
                        w.write(json.dumps(rename_info) + "\n")
            else:
                raise Exception("split_type不为SE也不为PE")
    return split_info_dir

def export_specimen_info(data, option_name, dir_path, bind_obj=None):
    #split_id = ObjectId("6464f0c4f53e484cf84494d8")
    split_id = ObjectId(data)
    sg_split_library_collection = db["sg_split_library"]
    sg_split_specimen_collection = db["sg_split_specimen"]
    sg_split_library_documents = sg_split_library_collection.find({"split_id": split_id})
    specimen_info_list = os.path.join(dir_path, "all_specimen_info.xls")
    with open(specimen_info_list, "w") as w:
        header_list = ["library_id", "lane_name", "library_number", "library_type", "product_type", "specimen_name", "majorbio_name", "barcode_tag", "f_barcode", "r_barcode"]
        w.write("\t".join(header_list))
        w.write("\n")
        for document in sg_split_library_documents:
            library_id = document["_id"]
            lane_name = document["lane_name"]
            library_number = document["library_number"]
            library_type = document["library_type"]
            sg_split_specimen_documents = sg_split_specimen_collection.find({"split_id": split_id, "library_id":library_id})
            for specimen_doc in sg_split_specimen_documents:
                product_type = specimen_doc["product_type"]
                specimen_name = specimen_doc["specimen_name"]
                majorbio_name = specimen_doc["majorbio_name"]
                barcode_tag = specimen_doc["barcode_tag"]
                f_barcode = specimen_doc["f_barcode"]
                r_barcode = specimen_doc["r_barcode"]
                new_line_list = [library_id.__str__(), lane_name, library_number, library_type, product_type, specimen_name, majorbio_name, barcode_tag, f_barcode, r_barcode]
                w.write("\t".join(new_line_list))
                w.write("\n")
    return specimen_info_list
                
def export_self_library_info(data, option_name, dir_path, bind_obj=None):
    split_id = ObjectId(data)
    sg_split_library_collection = db["sg_split_library"]
    sg_split_library_documents = sg_split_library_collection.find({"split_id": split_id, "pure": "yes"})
    self_library_info_list = os.path.join(dir_path, "self_library_info.xls")
    with open(self_library_info_list, "w") as w:
        header_list = ["library_id", "lane", "lane_name", "library_number", "library_type", "sample_names", "pure"]
        w.write("\t".join(header_list))
        w.write("\n")
        for document in sg_split_library_documents:
            library_id = document["_id"]
            lane = str(document["lane"])
            lane_name = document["lane_name"]
            library_number = document["library_number"]
            library_type = document["library_type"]
            try:
              sample_names = document["sample_names"]
            except:
              sample_names = document["library_number"]
            pure = document["pure"]
            new_line_list = [library_id.__str__(), lane, lane_name, library_number, library_type, sample_names, pure]
            w.write("\t".join(new_line_list))
            w.write("\n")
    return self_library_info_list

if __name__ == '__main__':
    #export_library_split_list(data="644799001134104c5539cce2",option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_library_split_params(data="644799001134104c5539cce2", option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    #export_rename_file(data="644799001134104c5539cce2", option_name="",dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",bind_obj=None)
    '''
    export_library_info_dir(data="64599e4c4512fb386a12d9c1", option_name="",
                       dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",
                       bind_obj=None)
    '''
    export_specimen_info(data="6464f0c4f53e484cf84494d8", option_name="",
                       dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/majorbio_development/datasplit_v3/测试/to_file/",
                       bind_obj=None)