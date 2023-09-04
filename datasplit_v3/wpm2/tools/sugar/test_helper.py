#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
自动生成data.json
"""

import json
import copy
import random
import datetime
import argparse
import os
import toml
import case_convert

parse = argparse.ArgumentParser(description="生成data.json格式的测试文件")
parse.add_argument("-i", "--inputtoml", help="输入toml", required=True)
parse.add_argument("-r",
                   "--run",
                   help="是否要运行runwork",
                   action='store_true',
                   default=False)
args = vars(parse.parse_args())


def make_data_json(data, tmpl, global_id, who_am_i, workflow_list):
    """生成data.json字符串

    Args:
        data (dict): toml中的workflow配置单元
        template (dict): 模板
        global_id (str): 全局id
        who_am_i (str): whoami
        workflow_list(dict): 渲染字典
    """
    random_seed = ''.join(
        random.sample('zyxwvutsrqponmlkjihgfedcba0123456789', 4))
    tmpl_bak = copy.copy(tmpl)
    work_id = "_".join(([global_id] if global_id else []) +
                       [data["id"], who_am_i, random_seed])
    tmpl_bak["id"] = work_id
    tmpl_bak["type"] = data["type"]
    tmpl_bak["options"] = {}
    for option_key, option_value in data["options"].items():
        tmpl_bak["options"][option_key] = option_value.format(
            **workflow_list) if isinstance(option_value, str) else option_value
    tmpl_bak["name"] = data["name"]
    tmpl_bak["add_time"] = datetime.datetime.now().strftime("%Y/%m/%d %X")
    return tmpl_bak


with open(
        os.path.join(
            os.path.split(os.path.realpath(__file__))[0], 'template.json'),
        'r') as tmplfile:
    template = json.load(tmplfile)

config = toml.load(args["inputtoml"])
newdir = os.path.dirname(args["inputtoml"])
date = datetime.datetime.now().strftime("%Y%m%d")
wf_list = {"PWD": os.path.dirname(os.path.realpath(args["inputtoml"]))}
for key, item in enumerate(config["workflow"]):
    json_data = make_data_json(item, template, config["id"], config["whoami"],
                               wf_list)
    wf_list["wf" + str(key)] = json_data["id"]
    with open(os.path.join(newdir, json_data["id"] + '.json'), 'w') as o:
        json.dump(json_data, o, indent=4)
    if args["run"]:
        PRODUCT = case_convert.pascal_case(item["name"].split(".")[0])
        PREFIX = case_convert.pascal_case(item["name"].split(".")[-1])
        os.system("~/wpm2/bin/run_work -j " +
                  os.path.join(newdir, json_data["id"] + '.json'))
        os.symlink(
            os.path.join("/mnt/lustre/sanger-dev_workspace" + PRODUCT, date,
                         PREFIX + "_" + json_data["id"]),
            os.path.join(newdir, json_data["id"] + '_workspace'))

for key, value in wf_list.items():
    print(key + " => " + value)
