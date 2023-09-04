# !usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'yuan.xu'
# first modify: 20230110
# last modify: 20230110

from biocluster.agent import Agent
from biocluster.tool import Tool
from biocluster.core.exceptions import OptionError
from sugartool import create_tool_dict, create_agent_dict
import os

"""params
options: 
var:
    perl_path: perl解释器
    perl_script: /datasplit_v3/trim_fqSeq.pl脚本
功能：
    三代全长多样性长度过滤
"""

def move_result(self):
    new_fastq = "{output_dir}/{library_number}.trim.merge.split.allLen.fq".format(**self.sugar_var)
    if os.path.exists(new_fastq):
        os.remove(new_fastq)
    fastq = "{work_dir}/{library_number}.trim.merge.split.allLen.fq".format(**self.sugar_var)
    os.link(fastq, new_fastq)

sugar_config = {
    "name": "datasplit_trim_length_v3",
    "cpu": lambda x: 2,
    "mem": lambda x: "2G",
    "queue": "chaifen",
    "options": [{
        "name": "fastq",
        "type": "string",
        "required": True
    }, {
        "name": "start_pos",
        "type": "string",
        "default": "1"
    }, {
        "name": "valid_len",
        "type": "string",
        "required": True
    }, {
        "name": "min_len",
        "type": "string",
        "default": "0"
    }, {
        "name": "trim_end_len",
        "type": "string",
        "default": "0"
    }, {
        "name": "library_number",
        "type": "string",
        "required": True
    }],
    "var": {
        "perl_path": "program/perl-5.24.0/bin/perl",
        "perl_script": "{package_dir}/datasplit/trim_fqSeq.pl",
    },
    "env": lambda var: {
        "LD_LIBRARY_PATH": "{software_dir}/bioinfo/dna/env/lib".format(**var)
    },
    "cmds": [{
        "name": "datasplit_trim_length",
        "formatter": [
            "{perl_path} {perl_script} -i {fastq} -o {work_dir}/{library_number}.trim.merge.split.allLen.fq -s {start_pos} -l {valid_len} -m {min_len} "
            "-e {trim_end_len}"
        ],
        "callback": move_result
    }]
}

DatasplitTrimLengthV3Agent = type("DatasplitTrimLengthV3Agent", (Agent, ), create_agent_dict(sugar_config))

DatasplitTrimLengthV3Tool = type("DatasplitTrimLengthV3Tool", (Tool, ), create_tool_dict(sugar_config))
