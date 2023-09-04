# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230329
# last modify: 20230329

import os
import json
from biocluster.core.exceptions import OptionError
from biocluster.module import Module
from mbio.modules.datasplit_v3.sugarmodule import create_module_dict

def multi_rfam(self):
    configs = []
    sample_list = self.option("sample_list")
    with open(sample_list, "r") as f:
        for line in f:
            line_list = line.strip().split("\t")
            if len(line_list) == 4:
                fastq_path, sample_name, fastq_side, library_name = line_list
                if fastq_side == "l":
                    r1_fastq_path = fastq_path
                    continue
                elif fastq_side == "r":
                    r2_fastq_path = fastq_path
                    if os.path.exists(r1_fastq_path) and os.path.exists(r2_fastq_path) or r1_fastq_path.startswith("s3") and r2_fastq_path.startswith("s3"):
                        conf = {
                            "name": "datasplit_v3.rfam.datasplit_rfam_v3",
                            "type": "module",
                            "option": {
                                "r1_fastq_path": r1_fastq_path,
                                "r2_fastq_path": r2_fastq_path,
                                "random_number": 100,
                                "read_num": 50000,
                                "sample_name": sample_name,
                                "evalue": 0.00001,
                                "num_threads": 4,
                                "outfmt": 5,
                                "num_alignment": 1,
                            }
                        }
                    configs.append([conf])
                else:
                    raise Exception("r1或者r2的path不存在")
            else:
                raise Exception("sample_list.txt不为4列,所以报错")
        return configs

sugar_config = {
    "name":
    "Multi rfam",
    "options": [{
        "name": "sample_list",
        "type": "string",
        "required": True
    }],
    "phase_configs":
    lambda self: [{
        "routine_configs": multi_rfam(self),
        "onfinish": self.gen_set_outputs(lambda x: "")
    }]
}

DatasplitMultiRfamV3Module = type("DatasplitMultiRfamV3Module", (Module, ),
                                  create_module_dict(sugar_config))



