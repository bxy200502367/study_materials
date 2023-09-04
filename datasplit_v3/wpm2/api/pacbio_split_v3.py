# !usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__: yuan.xu
# first_modified: 20230220
# last_modified: 20230220

import os
import re
import json
import types
import datetime
from bson.objectid import ObjectId
from biocluster.api.database.base import Base, report_check
from itertools import islice

class PacbioSplitV3(Base):
    def __init__(self, bind_object):
        super(PacbioSplitV3, self).__init__(bind_object)
        self._project_type = 'datasplit_v2'

    def update_sg_pacbio(self, split_id, stat_file):
        print("主表更新")
        with open(stat_file, 'r') as f:
            for line in islice(f, 1, None):
                line_list = line.strip().split("\t")
                if len(line_list) == 3:
                    ccs_reads, reconize_reads, reconize_retio = line_list
                else:
                    raise Exception("lima_count.txt文件不为3列")
        query_dict = {
            "_id": ObjectId(split_id),
        }
        update_dict = {
            "ccs_reads": ccs_reads,
            "reconize_reads": reconize_reads,
            "reconize_retio": reconize_retio
        }
        self.db["sg_pacbio"].update(query_dict, {"$set": update_dict})

    def update_sg_pacbio_specimen(self, split_id, s3_upload_dir, raw_fastq_stat, clean_fastq_stat, split_type):
        print("样品信息表更新")
        if split_type == "different":
            with open(raw_fastq_stat, "r") as m:
                for line in islice(m, 1, None):
                    line_list = line.strip().split("\t")
                    if len(line_list) == 16:
                        file_name, format, type, num_seqs, sum_len, min_len, avg_len, max_len, q1, q2, q3, \
                            sum_gap, n50, q20, q30, gc = line_list
                        majorbio_number, primer_name, barcode_name, sample_name = file_name.replace(".ccs.fastq.gz", "").split("--")
                        query_dict = {
                            "import_id": ObjectId(split_id),
                            "majorbio_name": majorbio_number,
                            "barcode_name": barcode_name,
                            "sample_name": sample_name,
                            "primer_name": primer_name
                        }
                        update_dict = {
                            "reads": num_seqs,
                            "total_len": sum_len,
                            "ave_len": avg_len,
                            "q30": q30,
                            "gc": gc,
                            "raw_path": os.path.join(s3_upload_dir, "02.raw_fastq", file_name)
                        }
                        self.db["sg_pacbio_specimen"].update(query_dict, {"$set": update_dict})
                    else:
                        raise Exception("seqkit结果文件不为16列")
            with open(clean_fastq_stat, "r") as n:
                for line in islice(n, 1, None):
                    line_list = line.strip().split("\t")
                    if len(line_list) == 16:
                        file_name, format, type, num_seqs, sum_len, min_len, avg_len, max_len, q1, q2, q3, \
                            sum_gap, n50, q20, q30, gc = line_list
                        majorbio_number, primer_name, barcode_name, sample_name  = file_name.replace(".rename.value.fastq.gz", "").split("--")
                        query_dict = {
                            "import_id": ObjectId(split_id),
                            "majorbio_name": majorbio_number,
                            "barcode_name": barcode_name,
                            "sample_name": sample_name,
                            "primer_name": primer_name
                        }
                        update_dict = {
                            "qc_reads": num_seqs,
                            "reads_base": sum_len,
                            "clean_path": os.path.join(s3_upload_dir, "03.clean_fastq", file_name)
                        }
                        self.db["sg_pacbio_specimen"].update(query_dict, {"$set": update_dict})
                    else:
                        raise Exception("seqkit结果文件不为16列")
        elif split_type == "same":
            with open(raw_fastq_stat, "r") as m:
                for line in islice(m, 1, None):
                    line_list = line.strip().split("\t")
                    if len(line_list) == 16:
                        file_name, format, type, num_seqs, sum_len, min_len, avg_len, max_len, q1, q2, q3, \
                            sum_gap, n50, q20, q30, gc = line_list
                        majorbio_number, primer_name, barcode_name, sample_name = file_name.replace(".ccs.fastq.gz", "").split("--")
                        query_dict = {
                            "import_id": ObjectId(split_id),
                            "majorbio_name": majorbio_number,
                            "barcode_name": barcode_name,
                            "sample_name": sample_name,
                            "primer_name": primer_name
                        }
                        file_name_prefix = file_name.replace(".ccs.fastq.gz", "")
                        raw_path = os.path.join(s3_upload_dir, "01.bam_result", file_name_prefix + ".bam")
                        update_dict = {
                            "reads": num_seqs,
                            "total_len": sum_len,
                            "ave_len": avg_len,
                            "q30": q30,
                            "gc": gc,
                            "raw_path": raw_path,
                            "clean_path": raw_path,
                            "qc_reads": num_seqs,
                            "reads_base": sum_len
                        }
                        self.db["sg_pacbio_specimen"].update(query_dict, {"$set": update_dict})
                    else:
                        raise Exception("seqkit结果文件不为16列")
        else:
            raise Exception("source_data有误")

    def update_sg_pacbio_status(self, split_id):
        print("主表状态更新")
        query_dict = {
            "_id": ObjectId(split_id)
        }
        update_dict = {
            "status": "end"
        }
        self.db["sg_pacbio"].update(query_dict, {"$set": update_dict})


if __name__ == "__main__":
    a = PacbioSplit(None)
    split_id = "6136f57017b2bf11119ac9c3"
    s3_upload = "s3://rerewrweset/files/datasplit/2019/20190516sXten/5d09bed39dc6d6565858e0d4_20190621_131348"
    statread_new = "/mnt/ilustre/users/sanger-dev/workspace/20210917/PacbioSplit_SP20210915-1631687156_20210917_124744/PacbioStat/output/statReads.new.txt"
    stat_origin = "/mnt/ilustre/users/sanger-dev/workspace/20210917/PacbioSplit_SP20210915-1631687156_20210917_124744/PacbioStat/output/m64236_210806_111052"
    statistic = "/mnt/ilustre/users/sanger-dev/workspace/20210915/Single_qc_stat_233/PacbioQcStat/output/statistic"
    a.update_sg_pacbio_specimen(split_id, s3_upload, statistic)
    a.update_sg_pacbio(split_id, stat_origin)
    a.add_pacbio_bar(split_id, statread_new)
