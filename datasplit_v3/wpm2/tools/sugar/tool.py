# -*- coding:utf-8 -*-
"""
Last-edit: 2023/3/10
Author: yiwei.tang
mail: yiwei.tang@majorbio.com
Description: 语法糖v2
"""

import os
import basic
import types

def set_output(cls, config):
    """
    publish output dir
    """
    if "mkoutdir" in config.keys():
        for outdir in config["mkoutdir"]:
            os.mkdir(
                os.path.join(cls.output_dir, outdir.format(**cls.sugar_var)))
    if "publish" in config.keys():
        for output in config["publish"]:
            pattern = output["pattern"]
            if "dir" not in output.keys():
                output["dir"] = ""
            if not os.path.exists(
                    os.path.join(cls.output_dir,
                                 output["dir"].format(**cls.sugar_var))):
                os.mkdir(
                    os.path.join(cls.output_dir,
                                 output["dir"].format(**cls.sugar_var)))
            os.system("rm -rf {}".format(
                os.path.join(cls.output_dir, pattern.format(**cls.sugar_var))))
            os.system("cp -rl {} {}".format(
                os.path.join(cls.work_dir, pattern.format(**cls.sugar_var)),
                os.path.join(cls.output_dir,
                             output["dir"].format(**cls.sugar_var))))


def agent_init(cls, parent):
    """
    agent初始化函数，挂载queue
    """
    super(type(cls), cls).__init__(parent)
    cls.add_option(cls.sugar_config["options"])
    #queue = cls.sugar_config["queue"] if "queue" in cls.sugar_config.keys() else ""
    queue = cls.sugar_config.get("queue", "")
    if queue:
        cls.queue = queue
        cls.logger.debug("[Sugar Alert] Agent队列已设置为" + queue)
    # 增加内存增加步骤，modified by yuan.xu 20230821
    memory_increase_step = cls.sugar_config.get("memory_increase_step", 0)
    if memory_increase_step:
        cls._memory_increase_step = memory_increase_step
        cls.logger.debug("[Sugar Alert] memory_increase_step已设置为" + str(memory_increase_step))
    

def set_resource(cls):
    """
    设置内存和cpu
    """
    cpu = cls.sugar_config["cpu"]
    if isinstance(cpu, str) and cpu.startswith(
            "$") and cpu[1:] in cls.sugar_function.keys():
        cls.cpu = cls.sugar_function[cpu[1:]](cls)
        cls.logger.debug("[Sugar Alert] Tool Cpu已设置为" +
                         str(cls.sugar_function[cpu[1:]](cls)))
    else:
        cls.cpu = int(cpu)
        cls.logger.debug("[Sugar Alert] Tool Cpu已设置为" + str(cpu))
    mem = cls.sugar_config["mem"]
    if isinstance(mem, str) and mem.startswith(
            "$") and mem[1:] in cls.sugar_function.keys():
        cls.memory = cls.sugar_function[mem[1:]](cls)
        cls.logger.debug("[Sugar Alert] Tool mem已设置为" +
                         str(cls.sugar_function[mem[1:]](cls)))
    else:
        cls.memory = str(mem)
        cls.logger.debug("[Sugar Alert] Tool mem已设置为" + str(mem))


def agent_end(cls):
    """
    agent end
    """
    super(type(cls), cls).end()


def tool_init(cls, parent):
    """
    tool初始化函数，生成sugar_var
    """
    super(type(cls), cls).__init__(parent)
    cls.sugar_var = {}
    cls.sugar_var["output_dir"] = cls.output_dir
    cls.sugar_var["work_dir"] = cls.work_dir
    cls.sugar_var["package_dir"] = cls.config.PACKAGE_DIR
    cls.sugar_var["software_dir"] = cls.config.SOFTWARE_DIR


def tool_run(cls):
    """
    tool主体运行函数
    """
    super(type(cls), cls).run()
    cls.runtool()
    cls.set_output(cls.sugar_config)
    cls.end()


def mount_env(cls, config, global_config):
    """
    设置环境变量，如果有的话
    env 是一个函数生成env的字典
    """
    if "env" in config.keys():
        env_dict = {}
        if isinstance(config["env"], dict):
            for key, value in config["env"].items():
                if not isinstance(value, types.StringTypes):
                    cls.logger.debug("[Sugar Alert] env <" + key +
                                     "> should be string!")
                else:
                    env_dict[key] = value.format(**cls.sugar_var)
                    cls.logger.debug("[Sugar Alert] env: {}={}".format(
                        key, value.format(**cls.sugar_var)))
            cls.set_environ(**env_dict)
        elif callable(config["env"]):
            env_dict = config["env"](cls.sugar_var)
            cls.set_environ(**env_dict)
        elif ("env" in global_config.keys()) and isinstance(
                config["env"], list):
            for envname in config["env"]:
                if envname in global_config["env"].keys():
                    env_dict[envname] = global_config["env"][envname].format(
                        **cls.sugar_var)
                    cls.logger.debug("[Sugar Alert] env: {}={}".format(
                        envname,
                        global_config["env"][envname].format(**cls.sugar_var)))
            cls.set_environ(**env_dict)
        else:
            cls.logger.debug("[Sugar Alert] env type error!")


def agent_run(cls):
    """agent run
    重写以挂载function
    """
    super(type(cls), cls).run()


def run_callback(cls, callback):
    """
    执行回调函数
    """
    if callable(callback):
        callback(cls)
    elif isinstance(callback, types.StringTypes) and callback.startswith("$"):
        if callback[1:] in cls.sugar_function.keys():
            cls.sugar_function[callback[1:]](cls)
        else:
            cls.logger.debug("[Sugar Alert] cmd callback function not found!")
    else:
        cls.logger.debug("[Sugar Alert] cmd callback type error!")


def local_link(cls, source, to_file):
    """
    硬链接文件
    """
    if os.path.exists(to_file.format(**cls.sugar_var)):
        os.remove(to_file.format(**cls.sugar_var))
    os.link(source.format(**cls.sugar_var), to_file.format(**cls.sugar_var))


def cmd_link(cls, cmd):
    """
    执行命令前link
    """
    for link in cmd["link"]:
        if not link["from"] or not link["to"]:
            cls.logger.debug("[Sugar Alert] cmd link file error!")
        else:
            cls.local_link(link["from"], link["to"])


def cmd_link_after(cls, cmd):
    """
    执行命令后link
    """
    for link in cmd["link_after"]:
        if not link["from"] or not link["to"]:
            cls.logger.debug("[Sugar Alert] cmd link file after cmd error!")
        else:
            cls.local_link(link["from"], link["to"])


def run_cmd(cls, cmd, formatter="formatter", formatter_split="<--##-->"):
    """
    单命令block运行逻辑
    """
    if "link" in cmd.keys():
        cmd_link(cls, cmd)
    if formatter in cmd.keys():
        if isinstance(cmd[formatter], list):
            cmds_list = map(lambda c: c.format(**cls.sugar_var),
                            cmd[formatter])
        elif isinstance(cmd[formatter], types.StringTypes):
            cmds_list = map(lambda c: c.format(**cls.sugar_var),
                            cmd[formatter].strip().split(formatter_split))
        else:
            cls.logger.debug("[Sugar Alert] cmd formatter type error!")
        for index, cmd_ in enumerate(cmds_list):
            strindex = str(index) if index > 0 else ""
            cls.logger.debug("[Sugar Alert] " + cmd["name"] + strindex + ": " +
                             cmd_.strip())
            use_shell = ("shell" in cmd.keys() and cmd["shell"])
            # 默认状态码
            ignore_error = ("ignore_error" in cmd.keys() and cmd["ignore_error"])
            default_return_code = cmd.get("default_return_code", 0)
            cmd_r = cls.add_command(
                cmd["name"] + strindex,
                cmd_.strip(),
                shell = use_shell,
                ignore_error = ignore_error,
                default_return_code = default_return_code).run()
            cls.wait(cmd_r)
            if cmd_r.return_code == default_return_code:
                cls.logger.debug("[Sugar Alert] " + cmd["name"] + strindex +
                                 " 完成!")
            else:
                cls.logger.debug("[Sugar Alert] " + cmd["name"] + strindex +
                                 " 失败!")
                cls.set_error("[Sugar Alert] " + cmd["name"] + strindex +
                              " 报错!")
    if "callback" in cmd.keys():
        cls.run_callback(cmd["callback"])
    if "link_after" in cmd.keys():
        cmd_link_after(cls, cmd)


def runtool(cls):
    """
    tool运行逻辑函数
    """
    cls.mount_var(cls.sugar_config, cls.sugar_global_config)
    cls.mount_option(cls.sugar_config)
    cls.mount_bindings(cls.sugar_config)
    cls.logger.debug("[Sugar Info] tool sugar vars: " + str(cls.sugar_var))
    cls.mount_env(cls.sugar_config, cls.sugar_global_config)
    cls.logger.debug("[Sugar Alert] 开始运行" + cls.sugar_config["name"] + "!")
    for cmd in cls.sugar_config["cmds"]:
        whenif = True
        if "whenif" in cmd.keys():
            if isinstance(cmd["whenif"],
                          dict) and "oprt" in cmd["whenif"].keys():
                whenif = basic.OP[cmd["whenif"]["oprt"]](
                    cls.sugar_var[cmd["whenif"]["var"]],
                    cmd["whenif"]["value"])
            elif isinstance(cmd["whenif"],
                            types.StringTypes) and cmd["whenif"][0] == '$' and cmd["whenif"][
                                1:] in cls.sugar_function.keys():
                whenif = cls.sugar_function[cmd["whenif"][1:]](cls)
            else:
                whenif = bool(cls.sugar_var[cmd["whenif"]])
        splitter = "<--##-->"
        if "formatter_split" in cmd.keys():
            splitter = cmd["formatter_split"]
        if whenif:
            cls.run_cmd(cmd, formatter_split=splitter)
        elif "whenelse" in cmd.keys():
            cls.run_cmd(cmd, "whenelse", formatter_split=splitter)
    cls.logger.debug("[Sugar Alert] " + cls.sugar_config["name"] + "运行完成!")


def create_agent_dict(config,
                      agent_check_options=basic.zero_check,
                      **sugar_function):
    """
    用于生成tool类的字典
    """
    return {
        "__init__": agent_init,
        "sugar_config": config,
        "check_option": basic.check_option,
        "more_check_options": agent_check_options,
        "sugar_check_single_option": basic.sugar_check_single_option,
        "sugar_check_options": basic.sugar_check_options,
        "set_resource": set_resource,
        "end": agent_end,
        "run": agent_run,
        "sugar_function": sugar_function
    }


def create_tool_dict(config, global_config=None, **sugar_function):
    """
    用于生成tool类的字典
    """
    return {
        "__init__": tool_init,
        "run": tool_run,
        "mount_var": basic.mount_var,
        "mount_option": basic.mount_option,
        "mount_env": mount_env,
        "mount_bindings": basic.mount_bindings,
        "sugar_config": config,
        "sugar_global_config": global_config or {},
        "run_cmd": run_cmd,
        "runtool": runtool,
        "local_link": local_link,
        "run_callback": run_callback,
        "sugar_function": sugar_function,
        "set_output": set_output
    }


def create_tool_dict_by_yaml(content, global_config=None, **sugar_function):
    """
    读取并解码yaml格式的sugar_config生成tool类的字典
    """
    sugar_config = basic.read_yaml(content)
    return create_tool_dict(config=sugar_config,
                            global_config=global_config,
                            **sugar_function)


def create_agent_dict_by_yaml(content,
                              agent_check_options=basic.zero_check,
                              **sugar_function):
    """
    读取并解码yaml格式的sugar_config生成agent类的字典
    """
    sugar_config = basic.read_yaml(content)
    return create_agent_dict(config=sugar_config,
                             agent_check_options=agent_check_options,
                             **sugar_function)
