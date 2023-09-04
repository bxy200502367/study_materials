# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230117
# last modify: 20230206

import os
import json
from biocluster.core.exceptions import OptionError
from biocluster.module import Module
from mbio.modules.datasplit_v3.sugarmodule import create_module_dict
import pathlib

def multi_pacbio_qc(self):
    configs = []
    sample_list = self.option("sample_list")
    fastq_result_dir = self.option("fastq_result_dir")
    with open(sample_list, "r") as f:
        for line in f:
            line_list = line.strip().split("\t")
            if len(line_list) == 10:
                majorbio_name, sample_name, barcode_name, f_name, r_name, product_type, primer_name, \
                forward_primer, reverse_primer, primer_range = line_list
                primer_range_list = primer_range.strip().split(",")
                if primer_range == "" or primer_range == "0-0" or primer_range == "0":
                    min_length = "1000"
                    max_length = "1800"
                elif len(primer_range_list) == 2:
                    min_length, max_length = primer_range_list
                else:
                    self.logger.info(primer_range)
                    raise Exception("引物质控范围有问题")
                sample_id = majorbio_name + "--" + primer_name + "--" + barcode_name + "--" + sample_name
                fastq_file = majorbio_name + "--" + primer_name + "--" + barcode_name + "--" + sample_name + ".ccs.fastq.gz"
                fastq_file_path = os.path.join(fastq_result_dir, fastq_file)
                conf = {
                    "name": "datasplit_v3.pacbio_split.datasplit_pacbio_qc_v3",
                    "type": "module",
                    "option": {
                        "fastq_file": fastq_file_path,
                        "min_length": min_length,
                        "max_length": max_length,
                        "sample_name": sample_id,
                        "forward_primer": forward_primer,
                        "reverse_primer": reverse_primer
                    }
                }
                configs.append([conf])
            elif len(line_list) == 6:
                majorbio_name, sample_name, barcode_name, f_name, r_name, product_type = line_list
                primer_name = ""
                sample_id = majorbio_name + "--" + primer_name + "--" + barcode_name + "--" + sample_name
                fastq_file = majorbio_name + "--" + primer_name + "--" + barcode_name + "--" + sample_name + ".ccs.fastq.gz"
                fastq_file_path = os.path.join(fastq_result_dir, fastq_file)
                new_fastq_file = majorbio_name + "--" + primer_name + "--" + barcode_name + "--" + sample_name + ".value.fastq.gz"
                new_fastq_file_path = os.path.join(self.output_dir, new_fastq_file)
                conf = {
                    "name": "datasplit_v3.pacbio_split.datasplit_rename_fastq_v3",
                    "type": "tool",
                    "option": {
                        "old_fastq_file": fastq_file_path,
                        "new_fastq_path": new_fastq_file_path
                    }
                }
                configs.append([conf])
            else:
                raise Exception("sample_list.txt不为6列也不为10列,所以报错")
        return configs

sugar_config = {
    "name":
    "Multi Pacbio Qc",
    "options": [{
        "name": "sample_list",
        "type": "string",
        "required": True
    }, {
        "name": "fastq_result_dir",
        "type": "string",
        "required": True
    }],
    "phase_configs":
    lambda self: [{
        "routine_configs": multi_pacbio_qc(self),
        "onfinish": self.gen_set_outputs(lambda x: "")
    }],
}

DatasplitMultiPacbioQcV3Module = type("DatasplitMultiPacbioQcV3Module", (Module, ),
                                          create_module_dict(sugar_config))



