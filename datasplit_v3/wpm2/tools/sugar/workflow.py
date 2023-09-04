# -*- coding: utf-8 -*-
"""
Last-edit: 2023/3/13
Author: yiwei.tang
mail: yiwei.tang@majorbio.com
Description: |
语法糖v2
"""

import os
import datetime
import json
import basic
import module
from sugarbus import SugarBus


def workflow_init(cls, wsheet_object):
    """
    workflow初始化函数，生成sugar_var
    """
    super(type(cls), cls).__init__(wsheet_object)
    cls.logger.debug("[Sugar Alert] Workflow Options: " +
                     str(cls.sugar_config["options"]))
    cls.add_option(cls.sugar_config["options"])
    cls.set_options(cls.sheet.options())
    cls.logger.debug("[Sugar Alert] Set Options Finished!")
    cls.sugar_flow = {}
    cls.sugar_var = {}
    cls.sugar_var["output_dir"] = cls.output_dir
    cls.sugar_var["work_dir"] = cls.work_dir
    cls.sugar_var["s3_base_dir"] = cls.sheet.output
    cls.sugar_var["sheet_id"] = cls.sheet.id
    cls.sugar_var["sheet_params"] = json.dumps(cls.sheet.options(),
                                               sort_keys=True,
                                               separators=(',', ':'))
    cls.sugar_var["project_sn"] = cls.sheet.project_sn
    cls.sugar_var["member_type"] = cls.sheet.member_type
    cls.sugar_var["member_id"] = cls.sheet.member_id
    cls.sugar_base = {}
    cls.sugar_bus = SugarBus()
    cls.logger.debug("[Sugar Alert] Workflow Init Finished!")


def recursive_format(data_dict, sugar_var):
    """递归formatting字典

    Args:
        data_dict (dict): 字典
    """
    outdict = {}
    for key, value in data_dict.items():
        if isinstance(value, dict):
            outdict[key] = recursive_format(value, sugar_var)
        elif isinstance(value, str):
            outdict[key] = value.format(
                create_ts=datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"),
                **sugar_var)
    return outdict


def run_workflow(cls):
    """
    workflow运行逻辑函数
    """
    config = cls.sugar_config
    cls.logger.debug("[Sugar Alert] 开始挂载常量!")
    cls.mount_var(config)
    cls.mount_option(config)
    cls.mount_bindings(config)
    cls.logger.debug("[Sugar Info] Workflow sugar vars: " + str(cls.sugar_var))
    cls.sugar_bus.add_subscriber("[*]", cls.end)
    cls.mount_all_phases()
    cls.mount_diagram()
    cls.logger.debug("[Sugar Info] Workflow mount phases finished.")
    cls.logger.debug("[Sugar Info] Workflow sugar bus cases: " + str(cls.sugar_bus.casenames))
    cls.logger.debug("[Sugar Info] Workflow sugar bus subscriber: " + str(cls.sugar_bus.subscribernames))
    cls.sugar_bus.emit("[*]")
    cls.logger.debug("[Sugar Alert] 开始运行" + config["name"] + "!")


def workflow_end(cls):
    """
    end函数，完成文件结构整理，导表以及上传数据
    """
    cls.logger.debug("[Sugar Alert] 开始执行运行后程序")
    cls.run_api()
    cls.upload_files()
    super(type(cls), cls).end()


def run_api(cls):
    """
    按需导表
    """
    if "import" in cls.sugar_config.keys():
        for imports in cls.sugar_config["import"]:
            if "api" not in imports.keys():
                continue
            if "type" not in imports.keys():
                continue
            if "collect" not in imports.keys():
                continue
            if "options" not in imports.keys():
                continue
            cls.logger.debug("[Sugar Alert] 正在导表 => " + imports["collect"])
            if imports["api"] not in cls.sugar_base.keys():
                cls.sugar_base[imports["api"]] = cls.api.api(imports["api"])
            cls.sugar_base[imports["api"]].api_factory(
                imports["collect"], imports["type"],
                **recursive_format(imports["options"], cls.sugar_var))
        cls.logger.debug("[Sugar Alert] 全部导表完成")


def upload_files(cls):
    """
    上传文件至S3
    """
    if "upload" in cls.sugar_config.keys():
        for rdir in cls.sugar_config["upload"]:
            if "basedir" not in rdir.keys():
                continue
            result_dir = cls.add_upload_dir(
                os.path.join(cls.output_dir, rdir["basedir"]))
            if "relpath" in rdir.keys():
                relpath_rules = []
                for rule in rdir["relpath"]:
                    relpath_rules.append([
                        rule["path"],
                        rule["format"],
                        rule["desc"],
                        rule["lock"] if "lock" in rule.keys() else 0,
                        rule["code"] if "code" in rule.keys() else "001",
                        rule["is_hide"] if "is_hide" in rule.keys() else False,
                    ])
                result_dir.add_relpath_rules(relpath_rules)
        cls.logger.debug("[Sugar Alert] 结果文件上传S3完成")


def workflow_run(cls):
    """
    workflow主体运行函数
    """
    cls.logger.debug("[Sugar Alert] start running!")
    cls.sugar_workflow_items = cls.run_workflow()
    super(type(cls), cls).run()


def create_workflow_dict(config,
                         workflow_check_option=basic.zero_check,
                         **sugar_function):
    """
    用于生成workflow类的字典
    """
    return {
        "__init__": workflow_init,
        "sugar_config": config,
        "sugar_function": sugar_function,
        "check_option": basic.check_option,
        "more_check_options": workflow_check_option,
        "sugar_check_single_option": basic.sugar_check_single_option,
        "sugar_check_options": basic.sugar_check_options,
        "mount_var": basic.mount_var,
        "mount_option": basic.mount_option,
        "mount_bindings": basic.mount_bindings,
        "run_workflow": run_workflow,
        "mount_tool": module.mount_tool,
        "get_scatter": module.get_scatter,
        "run_tool_item": module.run_tool_item,
        "phase_end": module.phase_end,
        "mount_phase": module.mount_phase,
        "mount_all_phases": module.mount_all_phases,
        "mount_diagram": module.mount_diagram,
        "gen_set_outputs": module.gen_set_outputs,
        "run": workflow_run,
        "link_dir": module.link_dir,
        "run_api": run_api,
        "end": workflow_end,
        "upload_files": upload_files
    }


def create_workflow_dict_by_yaml(content,
                                 workflow_check_option=basic.zero_check,
                                 **sugar_function):
    """
    读取并解码yaml格式的sugar_config生成workflow类的字典
    """
    return create_workflow_dict(basic.read_yaml(content),
                                workflow_check_option, **sugar_function)
