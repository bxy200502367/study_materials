# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/07/02
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

from biocluster.agent import Agent
from biocluster.tool import Tool
from mbio.tools.datasplit_v3.sugar.tool import create_tool_dict_by_yaml, create_agent_dict_by_yaml
from mbio.tools.datasplit_v3.sugar.basic import read_local_file, read_yaml
import unittest

DatasplitCutLeftAgent = type(
    "DatasplitCutLeftAgent", (Agent, ),
    create_agent_dict_by_yaml(read_local_file(__file__, "datasplit_cut_left.yml")))
DatasplitCutLeftTool = type(
    "DatasplitCutLeftTool", (Tool, ),
    create_tool_dict_by_yaml(read_local_file(__file__, "datasplit_cut_left.yml"),
                             global_config=read_yaml(
                                 read_local_file(
                                     __file__, "../tool_global_config.yml"))))

class TestFunction(unittest.TestCase):
    """
    This is test for the tool. Just run this script to do test.
    """
    def test(self):
        from mbio.workflows.single import SingleWorkflow
        from biocluster.wsheet import Sheet
        import datetime
        test_dir='/mnt/clustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/datasplit_v3/sample_qc/tool'
        data = {
            "id": "CutLeft" + datetime.datetime.now().strftime('%H-%M-%S'),
            "type": "tool",
            "name": "datasplit_v3.sample_qc.datasplit_cut_left",
            "devmod": True,
            "instant": False,
            "options": dict(
                fastq="/mnt/dlustre/users/sanger/wpm2/workspace/20230627/LibrarySplit_CF5-20230621NovaX_20230627_160040/output/library_result/6/H0621novaX6_L1EHF1201639/L1EHF1201639--FH_2_2.R1.raw.fastq.gz",
                cut_left=3,
                length_contain=75,
                sample_id="L1EHF1201639--FH_2_2",
            )
           }
        wsheet = Sheet(data=data)
        wf = SingleWorkflow(wsheet)
        wf.run()


if __name__ == '__main__':
    unittest.main()
