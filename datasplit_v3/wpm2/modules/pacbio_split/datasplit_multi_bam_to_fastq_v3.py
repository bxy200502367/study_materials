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

def multi_bam_to_fastq(self):
    configs = []
    sample_list = self.option("sample_list")
    split_result_dir = self.option("split_result_dir")
    with open(sample_list, "r") as f:
        for line in f:
            line_list = line.split("\t")
            if len(line_list) == 10:
                majorbio_name, sample_name, barcode_name, f_name, r_name, product_type, primer_name, \
                forward_primer, reverse_primer, primer_range = line_list
                bam_file = majorbio_name + "--" + primer_name + "--" + barcode_name+ "--" + sample_name + ".bam"
                bam_file_path = os.path.join(split_result_dir, bam_file)
                fastq_file_prefix = majorbio_name + "--" + primer_name + "--" + barcode_name+ "--" + sample_name + ".ccs"
                fastq_file_prefix_path = os.path.join(self.output_dir, fastq_file_prefix)
                fastq_file = fastq_file_prefix_path + ".fastq.gz"
                if os.path.exists(bam_file_path) and os.path.isfile(bam_file_path):
                    conf = {
                        "name": "datasplit_v3.pacbio_split.datasplit_bam_to_fastq_v3",
                        "option": {
                            "bam_file": bam_file_path,
                            "out_prefix": fastq_file_prefix_path
                        }
                    }
                    configs.append([conf])
                else:
                    pathlib.Path(fastq_file).touch()
            else:
                raise Exception("sample_list.txt不为10列,所以报错")
        return configs

sugar_config = {
    "name":
    "Multi Bam To Fastq",
    "options": [{
        "name": "sample_list",
        "type": "string",
        "required": True
    }, {
        "name": "split_result_dir",
        "type": "string",
        "required": True
    }],
    "phase_configs":
    lambda self: [{
        "routine_configs": multi_bam_to_fastq(self)
    }]
}

DatasplitMultiBamToFastqV3Module = type("DatasplitMultiBamToFastqV3Module", (Module, ),
                                          create_module_dict(sugar_config))



