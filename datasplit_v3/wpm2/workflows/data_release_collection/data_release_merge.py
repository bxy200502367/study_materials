# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/22
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""


from biocluster.workflow import Workflow
from mbio.tools.datasplit_v3.sugar.workflow import create_workflow_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file

DataReleaseMergeWorkflow = type(
    "DataReleaseMergeWorkflow", (Workflow, ),
    create_workflow_dict_by_yaml(read_local_file(__file__, "data_release_merge.yml")))
