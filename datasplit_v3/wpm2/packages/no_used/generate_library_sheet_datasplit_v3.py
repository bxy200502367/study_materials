# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230204
# last_modified: 20230204

"""
生成library_sheet
"""

import argparse
from itertools import islice


def generate_library_sheet(infile: str, outfile: str) -> None:
    with open(infile, "r", encoding='utf-8') as f, open(outfile, "w", encoding="utf-8") as w:
        for line in islice(f, 0, 1):
            line_list = line.strip().split("\t")
            if len(line_list) == 12:
                header_1 = "[Data],,,,,,,,,,"
                header_list_2 = ["Lane", "Sample_ID", "Sample_Name", "Sample_Plate", "Sample_Well", "I7_Index_ID",
                                 "index", "I5_Index_ID", "index2", "Sample_Project", "Description"]
                w.write(header_1)
                w.write("\n")
                w.write(",".join(header_list_2))
                w.write("\n")
            elif len(line_list) == 11:
                header_1 = "[Data],,,,,,,,"
                header_list_2 = ["Lane", "Sample_ID", "Sample_Name", "Sample_Plate", "Sample_Well", "I7_Index_ID",
                                 "index", "Sample_Project", "Description"]
                w.write(header_1)
                w.write("\n")
                w.write(",".join(header_list_2))
                w.write("\n")
            else:
                raise Exception("library_info.txt不为11或者12列,所以报错")
        for line in islice(f, 1, None):
            line_list = line.strip().split("\t")
            if len(line_list) == 12:
                library_id, board_id, lane_id, lane_name, lane_match, library_number, library_type, seq_type, \
                    specimen_num, index_id, index, index2 = line_list
                sample_id = lane_name + "_" + library_number
                new_line_list = [lane_match, sample_id, library_number, "", "", index_id, index, "", index2, "Fastq", ""]
                w.write(",".join(new_line_list))
                w.write("\n")
            elif len(line_list) == 11:
                library_id, board_id, lane_id, lane_name, lane_match, library_number, library_type, seq_type, \
                    specimen_num, index_id, index = line_list
                sample_id = lane_name + "_" + library_number
                new_line_list = [lane_match, sample_id, library_number, "", "", index_id, index, "Fastq", ""]
                w.write(",".join(new_line_list))
                w.write("\n")
            else:
                raise Exception("library_info.txt不为11或者12列,所以报错")


parser = argparse.ArgumentParser(description="生成library_sheet.csv")
parser.add_argument("-i", "--infile", required=True)
parser.add_argument("-o", "--outfile", required=True)
args = vars(parser.parse_args())
generate_library_sheet(args["infile"], args["outfile"])
