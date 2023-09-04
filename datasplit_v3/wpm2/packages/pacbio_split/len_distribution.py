# -*- coding:utf-8 -*-
"""
LastEditTime: 2023/08/11
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import argparse

def len_distribution(infile: str, outfile: str) -> None:
    """
    长度分布文件生成
    """
    readDistribution = {}
    for i in range(200,3001,200):
        readDistribution[i] = 0
    with open(infile, "r") as f, open(outfile, "w") as w:
        for line in f:
            line_list = line.rstrip().split(' ')
            read_num = int(line_list[0])
            read_len = int(line_list[1])
            if read_len <=200:
                readDistribution[200] += int(read_num)
            elif read_len <=400:
                readDistribution[400] += int(read_num)
            elif read_len <=600:
                readDistribution[600] += int(read_num)
            elif read_len <=800:
                readDistribution[800] += int(read_num)
            elif read_len <=1000:
                readDistribution[1000] += int(read_num)
            elif read_len <=1200:
                readDistribution[1200] += int(read_num)
            elif read_len <=1400:
                readDistribution[1400] += int(read_num)
            elif read_len <=1600:
                readDistribution[1600] += int(read_num)
            elif read_len <=1800:
                readDistribution[1800] += int(read_num)
            elif read_len <=2000:
                readDistribution[2000] += int(read_num)
            elif read_len <=2200:
                readDistribution[2200] += int(read_num)
            elif read_len <=2400:
                readDistribution[2400] += int(read_num)
            elif read_len <=2600:
                readDistribution[2600] += int(read_num)
            elif read_len <=2800:
                readDistribution[2800] += int(read_num)
            else:
                readDistribution[3000] += int(read_num)
        for key in sorted(readDistribution.keys()):
            w.write("{}\t{}\n".format(key,readDistribution[key]))
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="长度分布文件生成")
    parser.add_argument("-i", "--infile", help="输入文件", required=True)
    parser.add_argument("-o", "--outfile", help="输出文件", required=True)
    args = parser.parse_args()
    len_distribution(args.infile, args.outfile)
