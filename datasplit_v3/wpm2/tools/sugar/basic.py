# -*- coding:utf-8 -*-
"""
Last-edit: 2023/3/10
Author: yiwei.tang
mail: yiwei.tang@majorbio.com
Description: 语法糖v2
"""
import os
import operator
from biocluster.core.exceptions import OptionError
import yaml
import types

def read_local_file(selfpath, filename):
    """
    读取相对路径的文件
    """
    with open(
            os.path.join(
                os.path.split(os.path.realpath(selfpath))[0], filename),
            "r") as localf:
        filestr = localf.read()
    return filestr


def read_yaml(yaml_str):
    """
    读取yaml字符串
    """
    return yaml.safe_load(yaml_str)


OP = {
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda b, a: operator.contains(a, b),
    "contain": operator.contains,
    "endswith": lambda a, b: a.endswith(b),
    "startswith": lambda a, b: a.startswith(b)
}


def zero_check(cls):
    """
    空检查函数
    """
    cls.logger.debug("[Sugar Alert] 无自定义检查选项。")


def sugar_check_single_option(cls, option):
    """
    单选项检查
    """
    #_required = option["required"] if "required" in option.keys() else False
    _required = option.get("required", False)
    _picker = list(option["picker"]) if "picker" in option.keys() else False
    if _required:
        if option["type"] in ["infile", "outfile"] and cls.option(
                option["name"]).is_set:
            pass
        elif option["type"] not in ["infile", "outfile"] and cls.option(
                option["name"]):
            pass
        else:
            raise OptionError("请设置：" + option["name"])
    if _picker:
        if cls.option(option["name"]) not in _picker:
            raise OptionError(option["name"] + "设置错误，应为：" +
                              "|".join(map(str, _picker)))


def sugar_check_options(cls, callback):
    """
    所有选项检查，添加callback以增加自定义检查方式
    """
    for option in cls.sugar_config["options"]:
        cls.sugar_check_single_option(option)
    callback(cls)


def check_option(cls):
    """
    选项检查接口
    """
    cls.sugar_check_option(cls.more_check_options)


def mount_bindings(cls, config):
    """
    将bindings挂载到sugar_var，常用于infile等复杂option的计算
    """
    if "bindings" in config.keys():
        for name, binding in config["bindings"].items():
            if isinstance(binding, types.StringTypes) and binding.startswith("$"):
                if binding[1:] in cls.sugar_function.keys():
                    cls.sugar_var[name] = cls.sugar_function[binding[1:]](cls)
                elif "." in binding[1:]:
                    s_list = binding[1:].split(".")
                    cls.sugar_var[name] = operator.getitem(
                        cls.option(s_list[0]).prop, s_list[1])
                else:
                    cls.logger.debug(
                        "[Sugar Alert] bindings function not found!")
            elif callable(binding):
                cls.sugar_var[name] = binding(cls)
            else:
                cls.logger.debug("[Sugar Alert] bindings type error!")


def mount_option(cls, config):
    """
    挂载option 如果option和var冲突，以var为主，冲突会前缀option_
    """
    for option in config["options"]:
        var_name = option["name"]
        if var_name in cls.sugar_var.keys():
            var_name = "option_" + var_name
        if option["type"] in ["infile", "outfile"]:
            if cls.option(option["name"]).is_set:
                cls.sugar_var[var_name] = cls.option(option["name"]).path
            else:
                cls.sugar_var[var_name] = ""
        else:
            cls.sugar_var[var_name] = cls.option(option["name"])


def mount_var(cls, config, global_config=None):
    """
    优先挂载var变量，字段global_var用于引入global_config的var变量
    """
    if global_config is None:
        global_config = {}
    if "global_var" in config.keys() and "var" in global_config.keys():
        for key in config["global_var"]:
            cls.sugar_var[key] = global_config["var"][key].format(
                **cls.sugar_var)
    if "var" in config.keys():
        for key, value in config["var"].items():
            cls.sugar_var[key] = value.format(**cls.sugar_var)
