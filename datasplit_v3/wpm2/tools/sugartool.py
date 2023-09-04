# -*- coding:utf-8 -*-
"""
Last-edit: 2022/12/31
Author: yiwei.tang
mail: yiwei.tang@majorbio.com
Description: 语法糖v1.1
"""
import os
import operator
from biocluster.core.exceptions import OptionError
import yaml


def agent_init(cls, parent):
    """
    agent初始化函数，挂载queue
    """
    super(type(cls), cls).__init__(parent)
    cls.add_option(cls.sugar_config["options"])
    queue = cls.sugar_config["queue"] if "queue" in cls.sugar_config.keys(
    ) else ""
    if queue:
        cls.queue = queue
        cls.logger.debug("[Sugar Alert] Agent队列已设置为" + queue)


def set_resource(cls):
    """
    设置内存和cpu
    """
    cpu = cls.sugar_config["cpu"]
    if callable(cpu):
        cls.cpu = cpu(cls)
        cls.logger.debug("[Sugar Alert] Tool Cpu已设置为" + str(cpu(cls)))
    elif isinstance(cpu, str) and cpu.startswith(
            "$") and cpu[1:] in cls.sugar_function.keys():
        cls.cpu = cls.sugar_function[cpu[1:]](cls)
        cls.logger.debug("[Sugar Alert] Tool Cpu已设置为" +
                         str(cls.sugar_function[cpu[1:]](cls)))
    else:
        cls.cpu = cpu
        cls.logger.debug("[Sugar Alert] Tool Cpu已设置为" + str(cpu))
    mem = cls.sugar_config["mem"]
    if callable(mem):
        cls.memory = mem(cls)
        cls.logger.debug("[Sugar Alert] Tool mem已设置为" + str(mem(cls)))
    elif isinstance(mem, str) and mem.startswith(
            "$") and mem[1:] in cls.sugar_function.keys():
        cls.memory = cls.sugar_function[mem[1:]](cls)
        cls.logger.debug("[Sugar Alert] Tool mem已设置为" +
                         str(cls.sugar_function[mem[1:]](cls)))
    else:
        cls.memory = mem
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


def mount_var(cls, config, global_config):
    """
    优先挂载var变量，字段global_var用于引入global_config的var变量
    """
    if "global_var" in config.keys() and "var" in global_config.keys():
        for key in config["global_var"]:
            cls.sugar_var[key] = global_config["var"][key].format(
                **cls.sugar_var)
    if "var" in config.keys():
        for key, value in config["var"].items():
            cls.sugar_var[key] = value.format(**cls.sugar_var)


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


def mount_env(cls, config, global_config):
    """
    设置环境变量，如果有的话
    env 是一个函数生成env的字典
    """
    if "env" in config.keys():
        env_dict = {}
        if isinstance(config["env"], dict):
            for key, value in config["env"].items():
                if not isinstance(value, str):
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


def mount_bindings(cls, config):
    """
    将bindings挂载到sugar_var，常用于infile等复杂option的计算
    """
    if "bindings" in config.keys():
        for name, binding in config["bindings"].items():
            if isinstance(binding, str) and binding.startswith("$"):
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


def mount_functions(cls, config):
    """
    挂载自定义函数
    """
    if "functions" in config.keys():
        for func in config["functions"]:
            temp_global = {}
            exec(func["eval"], temp_global)
            temp_global[func["name"]].__doc__ = func["desc"]
            cls.sugar_function[func["name"]] = temp_global[func["name"]]


def run_callback(cls, callback):
    """
    执行回调函数
    """
    if callable(callback):
        callback(cls)
    elif isinstance(callback, str) and callback.startswith("$"):
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


def run_cmd(cls, cmd, formatter="formatter", formatter_split="<--##-->"):
    """
    单命令block运行逻辑
    """
    if "link" in cmd.keys():
        for link in cmd["link"]:
            if not link["from"] or not link["to"]:
                cls.logger.debug("[Sugar Alert] cmd link file error!")
            else:
                cls.local_link(link["from"], link["to"])
    if formatter in cmd.keys():
        if isinstance(cmd[formatter], list):
            cmds_list = map(lambda c: c.format(**cls.sugar_var),
                            cmd[formatter])
        elif callable(cmd[formatter]):
            cmds_list = cmd[formatter](cls)
        elif isinstance(cmd[formatter], str):
            cmds_list = map(lambda c: c.format(**cls.sugar_var),
                            cmd[formatter].strip().split(formatter_split))
        else:
            cls.logger.debug("[Sugar Alert] cmd formatter type error!")
        for index, cmd_ in enumerate(cmds_list):
            strindex = str(index) if index > 0 else ""
            cls.logger.debug("[Sugar Alert] " + cmd["name"] + strindex + ": " +
                             cmd_.strip())
            use_shell = ("shell" in cmd.keys() and cmd["shell"])
            cmd_r = cls.add_command(cmd["name"] + strindex,
                                    cmd_.strip(),
                                    shell=use_shell).run()
            cls.wait(cmd_r)
            if cmd_r.return_code == 0:
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
        for link in cmd["link_after"]:
            if not link["from"] or not link["to"]:
                cls.logger.debug(
                    "[Sugar Alert] cmd link file after cmd error!")
            else:
                cls.local_link(link["from"], link["to"])


op = {
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


def runtool(cls):
    """
    tool运行逻辑函数
    """
    cls.mount_var(cls.sugar_config, cls.sugar_global_config)
    cls.mount_option(cls.sugar_config)
    cls.mount_functions(cls.sugar_config)
    cls.mount_bindings(cls.sugar_config)
    cls.logger.debug("[Sugar Info] tool sugar vars: " + str(cls.sugar_var))
    cls.mount_env(cls.sugar_config, cls.sugar_global_config)
    cls.logger.debug("[Sugar Alert] 开始运行" + cls.sugar_config["name"] + "!")
    for cmd in cls.sugar_config["cmds"]:
        whenif = True
        if "whenif" in cmd.keys():
            if isinstance(cmd["whenif"],
                          dict) and "oprt" in cmd["whenif"].keys():
                whenif = op[cmd["whenif"]["oprt"]](
                    cls.sugar_var[cmd["whenif"]["var"]],
                    cmd["whenif"]["value"])
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
            os.system("rm -r {}".format(
                os.path.join(cls.output_dir, pattern.format(**cls.sugar_var))))
            os.system("cp -rl {} {}".format(
                os.path.join(cls.work_dir, pattern.format(**cls.sugar_var)),
                os.path.join(cls.output_dir,
                             output["dir"].format(**cls.sugar_var))))


def zero_check(cls):
    """
    空检查函数
    """
    cls.logger.debug("[Sugar Alert] 无自定义检查选项。")


def sugar_check_single_option(cls, option):
    """
    单选项检查
    """
    _required = option["required"] if "required" in option.keys() else False
    _picker = option["picker"] if "picker" in option.keys() else False
    if _required:
        if cls.option(option["name"]) and cls.option(option["name"]).is_set:
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


def create_agent_dict(config, agent_check_options=zero_check):
    """
    用于生成tool类的字典
    """
    return {
        "__init__": agent_init,
        "sugar_config": config,
        "check_option": check_option,
        "more_check_options": agent_check_options,
        "sugar_check_single_option": sugar_check_single_option,
        "sugar_check_options": sugar_check_options,
        "set_resource": set_resource,
        "end": agent_end
    }


def create_tool_dict(config, global_config=None, **sugar_function):
    """
    用于生成tool类的字典
    """
    return {
        "__init__": tool_init,
        "run": tool_run,
        "mount_var": mount_var,
        "mount_option": mount_option,
        "mount_env": mount_env,
        "mount_bindings": mount_bindings,
        "mount_functions": mount_functions,
        "sugar_config": config,
        "sugar_global_config": global_config or {},
        "run_cmd": run_cmd,
        "runtool": runtool,
        "local_link": local_link,
        "run_callback": run_callback,
        "sugar_function": sugar_function,
        "set_output": set_output
    }


def read_yaml(yaml_str):
    """
    读取yaml字符串
    """
    return yaml.load(yaml_str, yaml.Loader)


def create_tool_dict_by_yaml(content, global_config=None, **sugar_function):
    """
    读取并解码yaml格式的sugar_config生成tool类的字典
    """
    sugar_config = read_yaml(content)
    return create_tool_dict(config=sugar_config,
                            global_config=global_config,
                            **sugar_function)


def create_agent_dict_by_yaml(content, agent_check_options=zero_check):
    """
    读取并解码yaml格式的sugar_config生成agent类的字典
    """
    return create_agent_dict(read_yaml(content), agent_check_options)
