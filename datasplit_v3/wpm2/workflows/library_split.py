# -*- coding:utf-8 -*-
"""
Last-edit: 2023/05/14
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.workflow import Workflow
from mbio.tools.datasplit_v3.sugar.workflow import create_workflow_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

def exist_self_library(self):
    count = -1
    with open(self.option("self_library_info"), "r") as f:
        for count, line in enumerate(f):
            count += 1
    if count > 1:
        return True
    else:
        return False
    
LibrarySplitWorkflow = type(
    "LibrarySplitWorkflow", (Workflow, ),
    create_workflow_dict_by_yaml(read_local_file(__file__, "library_split.yml"),
                                 exist_self_library = exist_self_library))
