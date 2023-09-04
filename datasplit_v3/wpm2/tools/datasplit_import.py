# -*- coding: utf-8 -*-
# __author__: zengjing
# last_modify: 20190314

import os
from biocluster.tool import Tool
from biocluster.agent import Agent
from biocluster.core.exceptions import OptionError
#from biocluster.api.file.lib.transfer import TransferManager
from biocluster.api.file.lib.transfer import MultiFileTransfer

class DatasplitImportAgent(Agent):
    """
    线下数据导入对象存储
    功能：对数据进检查，将线下文件上传到对象存储，生成新的拆分任务
    """
    def __init__(self, parent=None):
        super(DatasplitImportAgent, self).__init__(parent)
        options = [
            {"name": "target_path", "type": "string", "required": True},  # 对象存储路径
            {"name": "main_id", "type": "string", "required": True},  # sg_import的_id
            {"name": "update_info", "type": "string", "required": True},  # 更新信息
        ]
        self.add_option(options)
        self.queue = "chaifen"  # 投递到指定的队列chaifen

    def check_options(self):
        if not self.option("target_path"):
            raise OptionError("请设置对象存储路径")
        if not self.option("main_id"):
            raise OptionError("请设置main_id")
        if not self.option("update_info"):
            raise OptionError("请设置update_info")

    def set_resource(self):
        self._cpu = 1
        self._memory = "10G"

    def end(self):
        self.add_upload_dir(self.output_dir)
        super(DatasplitImportAgent, self).end()


class DatasplitImportTool(Tool):
    def __init__(self, config):
        super(DatasplitImportTool, self).__init__(config)
        self.upload_api = self.api.api("datasplit.datasplit_import")

    def check_import_info(self):
        """
        检查导入的信息，拆分板、lane、文库、样本、path是否都存在
        """
        import_id = self.option("main_id")
        s3_path = self.option("target_path")
        self.s3_info = self.upload_api.check_import_info(import_id, s3_path)
        self.logger.info("信息检查成功")

    def upload_file(self):
        """
        将path上传到对象存储
        """
        self.logger.info("开始上传文件到对象存储")
        #transfer = TransferManager()
        transfer = MultiFileTransfer()
        with open("upload.list", "wb") as w:
            for upload_file in self.s3_info.keys():
                target_file = self.s3_info[upload_file]
                targe_file_path = os.path.dirname(target_file) + "/"
                transfer.add_upload(upload_file, targe_file_path)
                self.run_md5sum(upload_file, target_file)
                w.write(upload_file + "\t" + target_file + "\n")
        #transfer.wait()
        transfer.perform()
        self.logger.info("文件上传到对象存储完成")

    def run_md5sum(self, path, s3_path):
        """
        生成md5校验码
        """
        if s3_path != "-":
            md5 = os.popen("md5sum {}".format(path)).readlines()[0].split(" ")[0]
            if self.md5_dict.has_key(os.path.dirname(s3_path)):
                self.md5_dict[s3_path] = md5
            else:
                self.md5_dict[s3_path] = {}
                self.md5_dict[s3_path] = md5

    def make_datasplit_task(self):
        """
        上传成功后，生成拆分任务
        """
        import_id = self.option("main_id")
        self.upload_api.make_datasplit_task(import_id, self.md5_dict)
        self.logger.info("生成新的拆分任务成功")

    def run(self):
        super(DatasplitImportTool, self).run()
        self.md5_dict = {}
        self.check_import_info()
        self.upload_file()
        self.make_datasplit_task()
        self.end()
