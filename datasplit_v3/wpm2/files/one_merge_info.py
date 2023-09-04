# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/05/25
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""



from biocluster.iofile import File
from biocluster.core.exceptions import FileError
from itertools import islice
import csv
from collections import namedtuple

class OneMergeInfoFile(File):
    """
    name: one_merge_info
    Description: |
        多列，以制表符分隔
    Props:
        merge_info_dict: 样品s3字典，样本名为键，raw_path1和raw_path2元组为值
        tuple_number: 元组数量
        r1_paths_str: 空格分隔的r1列表字符串
        r2_paths_str: 空格分隔的r2列表字符串
        sample_name: 样本的id，也是最后的名字
    """
    def check(self):
        if super(OneMergeInfoFile, self).check():
            self.get_info()
            return True
        return False

    def get_info(self):
        super(OneMergeInfoFile, self).get_info()
        merge_info_dict = self.check_merge_info()
        self.set_property("merge_info_dict", merge_info_dict)
        self.set_property("tuple_number", len(*merge_info_dict.values()))
        r1_path_list = []
        r2_path_list = []
        for key, value in merge_info_dict.items():
            if len(value) == 1:
                for r1_path, in value:
                    r1_path_list.append(r1_path)
            elif len(value) == 2:
                for r1_path, r2_path in value:
                    r1_path_list.append(r1_path)
                    r2_path_list.append(r2_path)
            else:
                raise FileError("样本{}的合并参数有问题".format(key))
        sample_name = key
        r1_paths_str = " ".join(r1_path_list)
        r2_paths_str = " ".join(r2_path_list)
        self.set_property("sample_name", sample_name)
        self.set_property("r1_paths_str", r1_paths_str)
        self.set_property("r2_paths_str", r2_paths_str)

    def check_merge_info(self):
        """
        检查函数,支持有r1和r2;也支持只有r1
        """
        merge_info_dict = {}
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            merge_info = namedtuple('merge_info', headers)
            for row in f_csv:
                each_row = merge_info(*row)
                if len(each_row.raw_path.split(";")) == 2:
                    raw_path_1 = each_row.raw_path.split(";")[0]
                    raw_path_2 = each_row.raw_path.split(";")[1]
                    merge_info_dict.setdefault(each_row.sample_name, []).append((raw_path_1, raw_path_2))
                elif len(each_row.raw_path.split(";")) == 1:
                    raw_path_1 = each_row.raw_path
                    merge_info_dict.setdefault(each_row.sample_name, []).append((raw_path_1, ))
                else:
                    raise FileError("样本{}的合并参数有问题".format(each_row.sample_name))
        return merge_info_dict

if __name__ == "__main__":
    a = OneMergeInfoFile()
    a.set_path("/mnt/lustre/users/sanger-dev/sg-users/yuan.xu/majorbio_development/data_release/test/merge_info_dir/GD72_3.sample_info.xls")
    print a.check()
    print a.prop["path"]
    print a.prop["merge_info_dict"]
    print a.prop["tuple_number"]
    print a.prop["sample_name"]
    print a.prop["r1_paths_str"]
    print a.prop["r2_paths_str"]