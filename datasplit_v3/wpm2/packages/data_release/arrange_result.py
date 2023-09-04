# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/08/02
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

"""
结果文件整理
"""

import argparse
import os
import shutil

def make_dir(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        pass
    else:
        os.makedirs(dir_path)
        
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

def arrange_result(result_dir: str, arrange_dir: str) -> None:
    dir_list = os.listdir(result_dir)
    for dir in dir_list:
        new_dir = os.path.join(arrange_dir, dir)
        make_dir(new_dir)
        product_type = os.listdir(os.path.join(result_dir, dir))[0]
        make_dir(os.path.join(arrange_dir, dir, product_type))
        if product_type in ["meta", "mirna"]:
            if len(os.listdir(os.path.join(result_dir, dir, product_type))) == 0:
                continue
            else:
                old_result_dir = os.path.join(result_dir, dir, product_type, product_type)
                new_result_dir = os.path.join(arrange_dir, dir, product_type, product_type)
                if os.path.exists(new_result_dir) and os.path.isdir(new_result_dir):
                    shutil.rmtree(new_result_dir)
                else:
                    make_dir(new_result_dir)
                    os_link_recursion(old_result_dir, new_result_dir)
        else: # 如果是非合并的去除raw
            if len(os.listdir(os.path.join(result_dir, dir, product_type))) == 0:
                continue
            if os.path.exists(os.path.join(result_dir, dir, product_type, product_type + "_True")):
                old_result_dir = os.path.join(result_dir, dir, product_type, product_type + "_True")
                new_result_dir = os.path.join(arrange_dir, dir, product_type, product_type)
                if os.path.exists(new_result_dir) and os.path.isdir(new_result_dir):
                    shutil.rmtree(new_result_dir)
                else:
                    make_dir(new_result_dir)
                    os_link_recursion(old_result_dir, new_result_dir)
            elif os.path.exists(os.path.join(result_dir, dir, product_type, product_type + "_False")):
                old_result_dir = os.path.join(result_dir, dir, product_type, product_type + "_False")
                new_result_dir = os.path.join(arrange_dir, dir, product_type, product_type)
                if os.path.exists(new_result_dir) and os.path.isdir(new_result_dir):
                    shutil.rmtree(new_result_dir)
                else:
                    make_dir(new_result_dir)
                    os_link_recursion(old_result_dir, new_result_dir)
                for file in os.listdir(new_result_dir):
                    if file.endswith("R1.raw.fastq.gz"):
                        r1_raw_fastq = os.path.join(new_result_dir, file)
                        os.remove(r1_raw_fastq)
                    if file.endswith("R2.raw.fastq.gz"):
                        r2_raw_fastq = os.path.join(new_result_dir, file)
                        os.remove(r2_raw_fastq)
            else:
                raise Exception("非多样性结果文件夹有误")
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="拆分完的结果改名")
    parser.add_argument("-i", "--result_dir", help="要整理的结果文件夹", required=True)
    parser.add_argument("-o", "--arrange_dir", help="整理完的结果文件夹", required=True)
    args = vars(parser.parse_args())
    arrange_result(args["result_dir"], args["arrange_dir"])
