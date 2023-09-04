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


def multi_library_split(self):
    # 根据split_info_dir生成多个routine_configs
    configs = []
    split_info_dir = self.option("split_info_dir")
    dir_list = os.listdir(split_info_dir)
    for dir in dir_list:
        library_info_file = os.path.join(split_info_dir, dir, dir + ".library_info.txt")
        library_split_params = os.path.join(split_info_dir, dir, dir + '.library_split.json')
        with open(library_split_params, "r") as f:
            params = json.load(f)
        conf = {
            "name": "datasplit_v3.library_split.datasplit_library_split_v3",
            "type": "module",
            "option": {
                "data_path": params["split_path"],
                "lane_match": params["lane_match"],
                "library_info_file": library_info_file,
                "bases_mask": params["seq_model"],
                "barcode_mismatch": params["mismatch"],
                "ignore_error": params["ignore_error"]
            }
        }
        configs.append([conf])
        return configs

sugar_config = {
    "name":
    "Multi Datasplit Library Split",
    "options": [{
        "name": "split_info_dir",
        "type": "string",
        "required": True
    }],
    "phase_configs":
    lambda self: [{
        "routine_configs": multi_library_split(self),
        "onfinish": self.gen_set_outputs(lambda x: "")
    }]
}

DatasplitMultiLibrarySplitV3Module = type("DatasplitMultiLibrarySplitV3Module", (Module, ),
                                          create_module_dict(sugar_config))



