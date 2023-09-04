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

project_type = "datasplit"
client = Config().get_mongo_client(mtype=project_type)
db = client[Config().get_mongo_dbname(project_type)]


def make_dir(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
    else:
        os.makedirs(dir_path)

def export_data_release_list(data, option_name, dir_path, bind_obj=None):
    """
        导出一拆的信息列表,每条lane一个文件，如果有多个lane则为多个文件
    """
    print data
    print option_name
    print bind_obj
    order_sn = data
    sg_board_specimen_collection = db["sg_board_specimen"]
    sg_board_specimen_documents = sg_board_specimen_collection.find({"order_sn": order_sn})
    for document in sg_board_specimen_documents:
        order_sn_doc = document["order_sn"]
        specimen_name_doc = document["specimen_name"]
        majorbio_name_doc = document["majorbio_name"]
        project_sn_doc = document["project_sn"]
        project_type_doc = document["project_type"]
        primer_doc = document["primer"]
        primer_seq = document["primer_seq"]





    sg_board_collection = db["sg_board"]
    sg_board_lane_collection = db["sg_board_lane"]
    sg_board_library_collection = db["sg_board_library"]
    # 从sg_split表中获取board_id还有对应的split_lane_dict
    sg_split_record = sg_split_collection.find_one({"_id": split_id})
    board_id = sg_split_record["board_id"]
    split_lane_dict = json.loads(sg_split_record["split_lane_dict"])
    for lane_name_info, lane_info in split_lane_dict.items():
        lane_name = lane_info["lane_name"]
        lane_match = lane_info["lane_match"]
        seq_model = lane_info["seq_model"]
        if "i6nn" in seq_model:
            split_type = "SE"
        elif seq_model.split(",")[2].startswith("n"):
            split_type = "SE"
        else:
            split_type = "PE"
        mismatch = lane_info["mismatch"]
        ignore_error = lane_info["ignore_error"]
        split_path = lane_info["split_path"]
        # 通过board_id和lane_name从sg_board_lane获取lane_id
        split_info_dir = os.path.join(dir_path, "split_info_dir", lane_match)
        make_dir(split_info_dir)
        library_info_list = os.path.join(dir_path, "split_info_dir", lane_match,
                                         "{}.library_info.txt".format(lane_match))
        sg_board_lane_record = sg_board_lane_collection.find_one({"board_id": board_id, "lane_name": lane_name})
        lane_id = sg_board_lane_record["_id"]
        # 通过board_id和lane_id从sg_board_library获取信息生产library_split_info文件
        sg_board_library_records = sg_board_library_collection.find({"board_id": board_id, "lane_id": lane_id})
        library_num = sg_board_library_records.count()
        if library_num > 0:
            if split_type == "PE":
                with open(library_info_list, "w") as w:
                    header_list = ["libray_id", "board_id", "lane_id", "lane_name", "lane_match", "library_number",
                                   "library_type", "seq_type", "specimen_num", "index_id", "index", "index2"]
                    w.write("\t".join(header_list))
                    w.write("\n")
                    for record in sg_board_library_records:
                        record_library_id = record["_id"].__str__()
                        record_board_id = record["board_id"].__str__()
                        record_lane_id = record["lane_id"].__str__()
                        record_lane_name = record["lane_name"]
                        record_lane_match = lane_match
                        record_library_number = record["library_number"]
                        record_library_type = record["library_type"]
                        record_seq_type = record["seq_type"]
                        record_specimen_num = str(record["specimen_num"])
                        record_index_id = record["index_id"]
                        record_index_seq = record["index_seq"]
                        record_index_seq_list = record_index_seq.split(",")
                        if len(record_index_seq_list) == 1:
                            index_i7 = record_index_seq_list[0]
                            index_i5 = ""
                        elif len(record_index_seq_list) == 2:
                            if "i8" in seq_model:
                                index_i7 = record_index_seq_list[0][:8]
                                index_i5 = record_index_seq_list[1][:8]
                            elif "i6" in seq_model:
                                index_i7 = record_index_seq_list[0][:6]
                                index_i5 = record_index_seq_list[1][:6]
                            else:
                                index_i7 = record_index_seq_list[0]
                                index_i5 = record_index_seq_list[1]
                        else:
                            raise Exception("有超过两个index")
                        line_list = [record_library_id, record_board_id, record_lane_id, record_lane_name,
                                     record_lane_match, record_library_number, record_library_type,
                                     record_seq_type, record_specimen_num, record_index_id, index_i7, index_i5]
                        w.write("\t".join(line_list))
                        w.write("\n")
            elif split_type == "SE":
                with open(library_info_list, "w") as w:
                    header_list = ["libray_id", "board_id", "lane_id", "lane_name", "lane_match", "library_number",
                                   "library_type", "seq_type", "specimen_num", "index_id", "index"]
                    w.write("\t".join(header_list))
                    w.write("\n")
                    for record in sg_board_library_records:
                        record_library_id = record["_id"].__str__()
                        record_board_id = record["board_id"].__str__()
                        record_lane_id = record["lane_id"].__str__()
                        record_lane_name = record["lane_name"]
                        record_lane_match = lane_match
                        record_library_number = record["library_number"]
                        record_library_type = record["library_type"]
                        record_seq_type = record["seq_type"]
                        record_specimen_num = str(record["specimen_num"])
                        record_index_id = record["index_id"]
                        record_index_seq = record["index_seq"]
                        record_index_seq_list = record_index_seq.split(",")
                        if len(record_index_seq_list) == 1:
                            index_i7 = record_index_seq_list[0]
                            index_i5 = ""
                        elif len(record_index_seq_list) == 2:
                            if "i8" in seq_model:
                                index_i7 = record_index_seq_list[0][:8]
                                index_i5 = ""
                            elif "i6" in seq_model:
                                index_i7 = record_index_seq_list[0][:6]
                                index_i5 = ""
                            else:
                                index_i7 = record_index_seq_list[0]
                                index_i5 = ""
                        else:
                            raise Exception("有超过两个index")
                        line_list = [record_library_id, record_board_id, record_lane_id, record_lane_name,
                                     record_lane_match, record_library_number, record_library_type,
                                     record_seq_type, record_specimen_num, record_index_id, index_i7]
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
    sg_split_document = sg_split_collection.find_one({"_id": split_id})
    split_lane_dict = json.loads(sg_split_document["split_lane_dict"])
    for lane_name_info, lane_info in split_lane_dict.items():
        lane_name = lane_info["lane_name"]
        lane_match = lane_info["lane_match"]
        library_split_params_file = os.path.join(dir_path, "split_info_dir", lane_match,
                                                 "{}.library_split.json".format(lane_match))
        with open(library_split_params_file, "w") as w:
            w.write(json.dumps(lane_info) + "\n")

def export_pacbio_split_list(data, option_name, dir_path, bind_obj=None):
    """
    导出三代测序数据文库信息
    """
    split_id = ObjectId(data)
    pacbio_sample_sheet = os.path.join(dir_path,"pacbio_sample_sheet.txt")
    with open(pacbio_sample_sheet, "w") as w:
        result_records = db["sg_pacbio_specimen"].find({"import_id": split_id})
        header_list = ["cell_name", "majorbio_name" , "sample_name", "barcode_name", "data_type", "type", "project_type",
                       "f_name", "r_name", "f_barcode", "r_barcode", "primer_name", "primer_f_base", "primer_r_base",
                       "primer_length", "primer_range"]
        w.write("\t".join(header_list))
        w.write("\n")
        for record in result_records:
            if record["is_split"] == "false":
                continue
            record_cell_name = record["cell_name"]
            record_majorbio_name = record["majorbio_name"]
            record_sample_name = record["sample_name"]
            record_barcode_name = record["barcode_name"]
            record_data_type = record["data_type"]
            record_type = record["type"]
            record_project_type = record["project_type"]
            record_f_name = record["f_name"]
            record_r_name = record["r_name"]
            record_f_barcode = record["f_barcode"]
            record_r_barcode = record["r_barcode"]
            record_primer_name = record["primer_name"]
            record_primer_f_base = str(record["primer_f_base"])
            record_primer_r_base = str(record["primer_r_base"])
            record_primer_length = str(record["primer_length"])
            record_primer_range = str(record["primer_range"])
            new_line_list = [record_cell_name, record_majorbio_name, record_sample_name, record_barcode_name, record_data_type,
                             record_type, record_project_type, record_f_name, record_r_name, record_f_barcode, record_r_barcode,
                             record_primer_name, record_primer_f_base, record_primer_r_base, record_primer_length, record_primer_range]
            w.write("\t".join(new_line_list))
            w.write("\n")
    return pacbio_sample_sheet

def export_pacbio_split_params(data, option_name, dir_path, bind_obj=None):
    """
    导出三代测序数据文库信息
    """
    split_id = ObjectId(data)
    pacbio_split_params_json = os.path.join(dir_path, "pacbio_split_params.json")
    pacbio_split_param = {}
    result = db["sg_pacbio"].find_one({"_id": split_id})
    print result
    record_bam_path = result["bam_path"]
    record_sample_sheet = os.path.join(dir_path, "pacbio_sample_sheet.txt")
    pacbio_split_param["bam_path"] = record_bam_path
    pacbio_split_param["sample_sheet"] = record_sample_sheet
    pacbio_split_params = {"pacbio_split": pacbio_split_param}
    with open(pacbio_split_params_json, "w") as w:
        w.write(json.dumps(pacbio_split_params) + "\n")
    return pacbio_split_params_json

if __name__ == '__main__':
    export_library_split_list(data="63c756997a733e190b16e930",
                              option_name="",
                              dir_path="/mnt/clustre/users/sanger-dev/users/yuan.xu/Datasplit_v3/test",
                              bind_obj=None)