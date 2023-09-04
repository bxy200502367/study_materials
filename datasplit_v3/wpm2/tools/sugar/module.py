# -*- coding: utf-8 -*-
"""
Last-edit: 2023/3/10
Author: yiwei.tang
mail: yiwei.tang@majorbio.com
Description: |
语法糖v2
"""

import shutil
import os
import copy
import random
import operator
import basic
from sugarbus import SugarBus
import gevent


def os_link_recursion(src, desc):
    """
    遍历文件夹下的文件，硬链接到另一个文件夹
    """
    if not os.path.exists(desc):
        os.mkdir(desc)
    for path in os.listdir(src):
        old_path = os.path.join(src, path)
        new_desc_path = os.path.join(desc, path)
        if os.path.isdir(old_path):
            if not os.path.exists(new_desc_path):
                os.mkdir(new_desc_path)
            os_link_recursion(old_path, new_desc_path)
        else:
            os.link(old_path, new_desc_path)
    
def link_dir(cls, dirpath, dirname=""):
    """
    批量硬链接文件夹
    """
    allfiles = os.listdir(dirpath)
    newdir = os.path.join(cls.output_dir, dirname)
    if not os.path.exists(newdir):
        os.mkdir(newdir)
    paired_files = [{
        "old": os.path.join(dirpath, i),
        "new": os.path.join(newdir, i)
    } for i in allfiles]
    for item in paired_files:
        # modified by yuan.xu 20230704:避免os.system导致的workflow通讯问题
        if os.path.exists(item["new"]) and os.path.isdir(item["new"]):
            #os.system(' '.join(["rm", "-r", item["new"]]))
            shutil.rmtree(item["new"])
        elif os.path.exists(item["new"]) and os.path.isfile(item["new"]):
            os.remove(item["new"])
        #os.system(' '.join(["cp", "-rl", item["old"], newdir]))
        if os.path.isdir(item["old"]):
            #shutil.copytree(item["old"], newdir, copy_function=os.link)
            os_link_recursion(item["old"], item["new"])
        else: 
            #os.path.isfile(item["old"])
            os.link(item["old"], item["new"])
            
def gen_set_outputs(cls, generator):
    """
    根据generator生成link_dir的参数，适用于并行时设置输出文件夹
    """

    def set_outputs(tools):
        for tool in tools:
            if callable(generator):
                cls.logger.debug("[Sugar Alert] Try to move all files from " +
                                 tool.output_dir + " to output/" +
                                 generator(tool))
                cls.link_dir(tool.output_dir, generator(tool))
            elif isinstance(generator, str):
                if generator.startswith("$"):
                    if not generator[1:] in cls.sugar_function.keys():
                        cls.logger.debug(
                            "[Sugar Alert] gen_set_outputs error! Function not found"
                        )
                    else:
                        real_generator = cls.sugar_function[generator[1:]]
                        cls.logger.debug(
                            "[Sugar Alert] Try to move all files from " +
                            tool.output_dir + " to output/" +
                            real_generator(tool))
                        cls.link_dir(tool.output_dir, real_generator(tool))
                else:
                    cls.logger.debug(
                        "[Sugar Alert] Try to move all files from " +
                        tool.output_dir + " to output/" + generator.format(
                            **dict(cls.sugar_var, **tool.sugar_props)))
                    cls.link_dir(
                        tool.output_dir,
                        generator.format(
                            **dict(cls.sugar_var, **tool.sugar_props)))
            else:
                cls.logger.debug("[Sugar Alert] Try to move all files from " +
                                 tool.output_dir + " to output/")
                cls.link_dir(tool.output_dir)

    return set_outputs


def module_init(cls, work_id):
    """
    module初始化函数，生成sugar_var
    """
    super(type(cls), cls).__init__(work_id)
    cls.logger.debug("[Sugar Alert] Module Options: " +
                     str(cls.sugar_config["options"]))
    cls.add_option(cls.sugar_config["options"])
    cls.sugar_var = {}
    cls.sugar_var["output_dir"] = cls.output_dir
    cls.sugar_var["work_dir"] = cls.work_dir
    cls.sugar_bus = SugarBus()


def run_module(cls):
    """
    module运行逻辑函数
    """
    config = cls.sugar_config
    cls.mount_var(config)
    cls.mount_option(config)
    cls.mount_bindings(config)
    cls.logger.debug("[Sugar Alert] Module sugar vars: " + str(cls.sugar_var))
    cls.sugar_bus.add_subscriber("[*]", cls.end)
    cls.mount_all_phases()
    cls.mount_diagram()
    cls.logger.debug("[Sugar Info] Module sugar bus cases: " +
                     str(cls.sugar_bus.casenames))
    cls.logger.debug("[Sugar Info] Module sugar bus subscriber: " +
                     str(cls.sugar_bus.subscribernames))
    cls.sugar_bus.emit("[*]")
    cls.logger.debug("[Sugar Alert] 开始运行" + config["name"] + "!")


def get_scatter(cls, tool_config):
    """
    根据tool_config生成scatter
    """
    if "scatter" not in tool_config.keys():
        return {}
    scatter = tool_config["scatter"]
    if isinstance(scatter, str) and scatter.startswith("$"):
        if scatter[1:] in cls.sugar_function.keys():
            scatters = cls.sugar_function[scatter[1:]](cls)
        elif "." in scatter[1:]:
            s_list = scatter[1:].split(".")
            scatters = operator.getitem(cls.option(s_list[0]).prop, s_list[1])
        else:
            cls.logger.debug("[Sugar Alert] scatter type error!")
    elif isinstance(scatter, dict):
        scatters = scatter
    else:
        cls.logger.debug("[Sugar Alert] scatter type error!")
    return scatters


def mount_tool(cls, tool_config):
    """
    挂载tool或者module并返回
    """
    if "type" not in tool_config.keys():
        tool_config["type"] = "tool"
    scatter = cls.get_scatter(tool_config)
    if len(scatter.keys()) == 0:
        if tool_config["type"] == "tool":
            tool = cls.add_tool(tool_config["name"])
        elif tool_config["type"] == "module":
            tool = cls.add_module(tool_config["name"])
        else:
            cls.logger.debug("[Sugar Alert] Tool type error!")
        tool.sugar_props = {}
        if "props" in tool_config.keys():
            tool.sugar_props.update(tool_config["props"])
        tool_item = {"tool": [tool], "config": tool_config, "scatter": {}}
    else:
        tool_list = []
        for scatter_key, scatter_value in scatter.items():
            if tool_config["type"] == "tool":
                tool = cls.add_tool(tool_config["name"])
            elif tool_config["type"] == "module":
                tool = cls.add_module(tool_config["name"])
            else:
                cls.logger.debug("[Sugar Alert] Tool type error!")
            tool.sugar_props = {}
            if "props" in tool_config.keys():
                tool.sugar_props.update(tool_config["props"])
            tool.sugar_props.update(scatter_key=scatter_key,
                                    scatter_value=scatter_value)
            tool_list.append(tool)
        tool_item = {
            "tool": tool_list,
            "config": tool_config,
            "scatter": scatter
        }
    return tool_item


def run_tool_item(cls, tool_item):
    """
    通用tool运行函数
    """
    for tool in tool_item["tool"]:
        options = copy.deepcopy(tool_item["config"]["option"])
        format_dict = dict(cls.sugar_var, **tool.sugar_props)
        for key in options.keys():
            if isinstance(options[key], str):
                options[key] = options[key].format(**format_dict)
        tool.set_options(options)
        if "log" in tool_item["config"].keys():
            cls.logger.debug("[Sugar Alert] " +
                             tool_item["config"]["log"].format(**format_dict))
        tool.run()
        gevent.sleep(1)


def phase_end(cls, event):
    """
    挂载最小执行单元执行后的end event绑定函数
    """
    tool_item = event["data"]
    cls.logger.debug("[Sugar Alert] " + tool_item["config"]["phase_name"] +
                     " finished!")
    if "onfinish" in tool_item["config"].keys():
        if tool_item["config"]["onfinish"][1:] in cls.sugar_function.keys():
            cls.sugar_function[tool_item["config"]["onfinish"][1:]](
                tool_item["tool"])
        else:
            cls.logger.debug("[Sugar Alert] onfinish " +
                             tool_item["config"]["name"] +
                             " function not found!")
    if "publish" in tool_item["config"].keys():
        if isinstance(tool_item["config"]["publish"], str):
            if not tool_item["config"]["publish"].startswith("$"):
                cls.gen_set_outputs(tool_item["config"]["publish"])(
                    tool_item["tool"])
            else:
                cls.gen_set_outputs(
                    cls.sugar_function[tool_item["config"]["publish"][1:]])(
                        tool_item["tool"])
        else:
            cls.logger.debug("[Sugar Alert] publish " +
                             tool_item["config"]["name"] + " type error!")
    cls.sugar_bus.emit(tool_item["config"]["phase_name"])


def mount_phase(cls, tool_config):
    """
    挂载最小执行单元，引入whenif选项
    """
    if "phase_name" not in tool_config.keys():
        tool_config["phase_name"] = tool_config["name"] + "_" + "".join(
            random.sample('zyxwvutsrqponmlkjihgfedcba0123456789', 8))
    whenif = True
    if "whenif" in tool_config.keys():
        if isinstance(tool_config["whenif"],
                      dict) and "oprt" in tool_config["whenif"].keys():
            whenif = basic.OP[tool_config["whenif"]["oprt"]](
                cls.sugar_var[tool_config["whenif"]["var"]],
                tool_config["whenif"]["value"])
        elif isinstance(
                tool_config["whenif"],
                str) and tool_config["whenif"][0] == '$' and tool_config[
                    "whenif"][1:] in cls.sugar_function.keys():
            whenif = cls.sugar_function[tool_config["whenif"][1:]](cls)
        else:
            whenif = bool(cls.sugar_var[tool_config["whenif"]])
    if whenif:
        tool_item = cls.mount_tool(tool_config)
        cls.on_rely(tool_item["tool"], cls.phase_end, tool_item)
        cls.sugar_bus.add_subscriber(tool_config["phase_name"],
                                     cls.run_tool_item,
                                     tool_item=tool_item)
    else:
        cls.sugar_bus.add_subscriber(tool_config["phase_name"],
                                     cls.sugar_bus.emit,
                                     case=tool_config["phase_name"])


def mount_all_phases(cls):
    """
    挂载所有phases
    """
    for phase_config in cls.sugar_config["phase_configs"]:
        cls.mount_phase(phase_config)


def mount_diagram(cls):
    """
    挂载运行逻辑
    """
    diagstr_list = cls.sugar_config["diagram"].strip().split("\n")
    for diagstr in diagstr_list:
        emitter, subscriber = diagstr.split("-->")
        emitter = emitter.strip()
        subscriber = subscriber.strip()
        cls.sugar_bus.subscribe(subscriber, emitter)


def module_run(cls):
    """
    module主体运行函数
    """
    super(type(cls), cls).run()
    cls.sugar_module_items = cls.run_module()


def create_module_dict(config,
                       module_check_option=basic.zero_check,
                       **sugar_function):
    """
    用于生成module类的字典
    """
    return {
        "__init__": module_init,
        "sugar_config": config,
        "sugar_function": sugar_function,
        "check_option": basic.check_option,
        "more_check_options": module_check_option,
        "sugar_check_single_option": basic.sugar_check_single_option,
        "sugar_check_options": basic.sugar_check_options,
        "mount_tool": mount_tool,
        "get_scatter": get_scatter,
        "run_tool_item": run_tool_item,
        "phase_end": phase_end,
        "mount_phase": mount_phase,
        "mount_all_phases": mount_all_phases,
        "mount_diagram": mount_diagram,
        "mount_var": basic.mount_var,
        "mount_option": basic.mount_option,
        "mount_bindings": basic.mount_bindings,
        "run_module": run_module,
        "gen_set_outputs": gen_set_outputs,
        "run": module_run,
        "link_dir": link_dir
    }


def create_module_dict_by_yaml(content,
                               module_check_option=basic.zero_check,
                               **sugar_function):
    """
    读取并解码yaml格式的sugar_config生成module类的字典
    """
    return create_module_dict(basic.read_yaml(content), module_check_option,
                              **sugar_function)
