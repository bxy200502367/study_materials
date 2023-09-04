# !usr/bin/python
# -*- coding: utf-8 -*-
"""
Last-edit: 2023/5/18
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""
import csv
from collections import namedtuple
import os
from biocluster.iofile import File
from biocluster.core.exceptions import FileError


def find_duplicates(lst):
        return [x for x in lst if lst.count(x) > 1] 

class AllSampleInfoFile(File):
    """
    空检查,用于指定infile类型的文件夹
    """

    def check(self):
        if super(AllSampleInfoFile, self).check():
            self.is_file()
            self.check_sample_barcode()
            return True

    def is_file(self):
        """
        检查传入的参数是否是文件夹并且判断是否存在
        """
        if not os.path.isfile(self.path) or not os.path.exists(self.path):
            raise FileError("不存在{}路径！".format(self.path))
        
    def check_sample_barcode(self):
        """
        modified by yuan.xu 20230610
        在不同的lane里面也有可能有相同的library_number名字，使用library_id作为区分标识
        但是一个library里面可以有相同的样本名，因为引物不同
        """
        sample_barcode_dict = {}
        with open(self.path, "r") as f:
            f_csv = csv.reader(f, delimiter="\t")
            headers = next(f_csv)
            sample_info_nt = namedtuple('sample_info_nt', headers)
            for row in f_csv:
                each_row = sample_info_nt(*row)
                if each_row.library_id not in sample_barcode_dict.keys():
                    sample_barcode_dict[each_row.library_id] = [(each_row.specimen_name, each_row.barcode_tag, each_row.f_barcode, each_row.r_barcode)]
                else:
                    sample_barcode_dict[each_row.library_id].append((each_row.specimen_name, each_row.barcode_tag, each_row.f_barcode, each_row.r_barcode))    
            for lib, sample_info in sample_barcode_dict.items():
                #specimen_name_list = []
                specimen_barcode_list = []
                specimen_barcode_seq_list = []
                for specimen_name, barcode_tag, f_barcode, r_barcode in sample_info:
                    #specimen_name_list.append(specimen_name)
                    specimen_barcode_list.append(barcode_tag)
                    specimen_barcode_seq_list.append(f_barcode + "_" + r_barcode)
                #duplicate_name_set = set(find_duplicates(specimen_name_list))
                duplicate_barcode_set = set(find_duplicates(specimen_barcode_list))
                duplicate_barcode_seq_set = set(find_duplicates(specimen_barcode_seq_list))
                #if duplicate_name_set:
                    #raise FileError("在 文库 {} 中样品名 {} 重复了".format(lib, ";".join(list(duplicate_name_set))))
                #else:
                    #pass
                if duplicate_barcode_set:
                    raise FileError("在 文库 {} 中barcode名 {} 重复了".format(lib, ";".join(list(duplicate_barcode_set))))
                else:
                    pass
                if duplicate_barcode_seq_set:
                    raise FileError("在 文库 {} 中barcode序列 {} 重复了".format(lib, ";".join(list(duplicate_barcode_seq_set))))
                else:
                    pass
            
if __name__ == "__main__":
    a = AllSampleInfoFile()
    a.set_path("/mnt/dlustre/users/sanger/wpm2/workspace/20230526/LibrarySplit_CF5-20230524Nova2_20230526_090239/all_specimen_info.xls")
    print a.check()
    print a.prop["path"]