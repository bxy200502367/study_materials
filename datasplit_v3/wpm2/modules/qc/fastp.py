# -*- coding:utf-8 -*-
# @First-edit Time 2022/11/29
# @Last-edit Time 2022/12/5
# @Author xiaoya.ye
# @mail xiaoya.ye@majorbio.com


from sugartool import create_tool_dict, create_agent_dict
from biocluster.agent import Agent
from biocluster.tool import Tool
from biocluster.core.exceptions import OptionError
import os

"""params
options:
    sample_name
    fastq:通过files类下载s3路径下的该fastq
    parameter：说明下载的为read1或read2源文件
    index：fastq编号
"""

"""vars
    fastp:对样品进行质控
"""

"""output:
    {sample_name}:W3.R1.raw.fastq.gz.clean.2.fastq.gz
"""

def set_output(self):
#将结果文件复制到output文件夹下面
    self.logger.info("{sample_name}:正在设置结果目录".format(**self.sugar_var))
    try:
        all_files = os .listdir("{work_dir}".format(**self.sugar_var))
        for files in all_files:
            judge = False #如果为True则说明为需要的文件
            if files.endswith("clean.2.fastq.gz"):
                new_name = "{sample_name}.clean.2.fastq.gz".format(**self.sugar_var)
                judge = True
            elif files.endswith("clean.1.fastq.gz"):
                new_name = "{sample_name}.clean.1.fastq.gz".format(**self.sugar_var)
                judge = True
            elif files.endswith(".json"):
                new_name = "{sample_name}.json".format(**self.sugar_var)
                judge = True
            else:
                pass
            if judge == True:
                f_ = "{output_dir}/{files}".format(files=files,**self.sugar_var)
                if os.path.exists(f_):
                    os.remove("{work_dir}/{files}".format(files=files,**self.sugar_var))
                    os.rename("{output_dir}/{files}".format(files=files,**self.sugar_var),"{output_dir}/{new_name}".format(new_name=new_name,**self.sugar_var))
                else:
                    os.system("mv {work_dir}/{files} {output_dir}/{new_name}".format(new_name=new_name,**self.sugar_var))
            else:
                pass
        self.logger.info("设置fastp分析结果目录成功")

    except Exception as e:
        self.logger.info("设置fastp分析结果目录失败{}".format(e))
        self.set_error("设置fastp分析结果目录失败{}".format(e))

    

sugar_config = {
    "name": "fastp",
    "cpu": lambda x: 4,
    "mem": lambda x: "10G",
    "options": [
        {
            "name": "fq1",
            "type": "infile",
            "format": "datasplit_v3.fastq",
            "required": True
        },{
            "name": "fq2",
            "type": "infile",
            "format": "datasplit_v3.fastq",
            "required": True
        },{
            "name": "sample_name",
            "type": "string",
            "required": True
        },{
            "name": "qualified_quality_phred",# -q,一个碱基合格的质量值,默认表示phred质量> = Q是合格的。
            "type": "string"
        },{
            "name": "length_required",# -l,长度过滤参数，比此值短的读取将被丢弃
            "type": "string"
        },{
            "name": "cut_by_quality5",# -5,根据前面(5 ')的质量，允许每个读切割，默认是禁用的
            "type": "string"
        },{
            "name": "cut_by_quality3",# -3,根据后面(3 ')的质量，允许每个读切割，默认是禁用的
            "type": "string"
        },{
            "name": "cut_mean_quality",# -M,在滑动窗口的基础上的平均质量低于切割质量将被切割，默认是Q20
            "type": "string"
        },{
            "name": "n_base_limit",# -n,如果reads的碱基数大于该值，那么这个reads就被丢弃了
            "type": "string"
        },{
            "name": "compression",# -z,gzip输出的压缩级别(1 ~ 9). 1是最快的，9是最小的
            "type": "string"
        },{
            "name": "thread", # -w,线程数
            "type": "string"
        },{
            "name": "cut_window_size",# -W
            "type": "string"
        },{
            "name": "adapter_sequence",# --adapter_sequence,the adapter for read1
            "type": "string" 
        },{
            "name": "adapter_sequence_r2",# --adapter_sequence,the adapter for read2
            "type": "string"
        }
    ],
    "var": {
        "fastp":"/mnt/lustre/users/sanger-dev/app/bioinfo/dna/env/bin/fastp"
    },
    "env": lambda var: {
        "LD_LIBRARY_PATH": "{software_dir}/bioinfo/dna/env/lib".format(**var)
    },
    "cmds": [
    {
        "name": "runfastp",
        "formatter": ["{fastp} -i {fq1} -I {fq2} -o {output_dir}/{sample_name}.clean.1.fastq.gz -O {output_dir}/{sample_name}.clean.2.fastq.gz -q {qualified_quality_phred} -l {length_required} -M {cut_mean_quality} -n {n_base_limit} -j {output_dir}/{sample_name}.json -z {compression} -w {thread} -5 {cut_by_quality5} -3 {cut_by_quality3} -W {cut_window_size} --adapter_sequence {adapter_sequence} --adapter_sequence_r2 {adapter_sequence_r2}"],
        "shell": True
    },{
        "callback":set_output
    }]
}

FastpAgent = type("FastpAgent", (Agent,), create_agent_dict(sugar_config))
FastpTool = type("FastpTool", (Tool,), create_tool_dict(sugar_config))