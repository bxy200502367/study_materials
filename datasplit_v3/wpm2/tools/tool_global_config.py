# -*- coding:utf-8 -*-
"""
Author: yiwei.tang
mail: yiwei.tang@majorbio.com
Description: tool公共软件参数
"""
import yaml

TOOL_GLOBAL_CONFIG_YAML = r"""
var:
    python2: bioinfo/datasplit/Miniconda3/envs/datasplit/bin/python
    python3: bioinfo/datasplit/Miniconda3/envs/datasplit/bin/python3
    python: /mnt/clustre/users/sanger-dev/app/program/Python-2.7.15/bin/python
    perl: /usr/bin/perl
    #bcl2fastq: bioinfo/datasplit/bcl2fastq
    #generate_library_sheet: '{package_dir}/datasplit_v3/library_split/datasplit_generate_library_sheet_v3'
    lima: bioinfo/datasplit/smrtlink/install/smrtlink-release_11.1.0.166339/smrtcmds/bin/lima
    generate_pacbio_barcode_file: '{package_dir}/datasplit_v3/pacbio_split/generate_pacbio_barcode_file_datasplit_v3.py'
    generate_pacbio_sample_list: '{package_dir}/datasplit_v3/pacbio_split/generate_pacbio_sample_list_datasplit_v3.py'
    pacbio_rename: '{package_dir}/datasplit_v3/pacbio_split/pacbio_rename_datasplit_v3.py'
    bam_to_fastq: bioinfo/datasplit/smrtlink/install/smrtlink-release_11.1.0.166339/smrtcmds/bin/bam2fastq
    mkdir: /usr/bin/mkdir
    mv: /usr/bin/mv
    rm: /usr/bin/rm
    ln: /usr/bin/ln
    gzip: /usr/bin/gzip
    cat: /usr/bin/cat
    pacbio_length_filter: '{package_dir}/datasplit_v3/pacbio_split/trim_fqSeq.pl'
    pacbio_correct_seq: '{package_dir}/datasplit_v3/pacbio_split/split_byPrimer2.pl'
    sequence_rename: '{package_dir}/datasplit_v3/pacbio_split/sequence_rename_datasplit_v3.py'
    #new_rc: /mnt/clustre/users/sanger-dev/app/bioinfo/datasplit/new.rc
    #cutadapt: 'bioinfo/datasplit/Miniconda3/envs/datasplit/bin/cutadapt'
    seqkit: /mnt/clustre/users/sanger-dev/app/bioinfo/datasplit/env/bin/seqkit
    generate_lima_summary: '{package_dir}/datasplit_v3/pacbio_split/lima_summary_datasplit_v3.py'
    bcl_convert: bioinfo/datasplit/env/bin/bcl-convert
    seqtk: /mnt/clustre/users/sanger-dev/app/bioinfo/datasplit/seqtk/seqtk
    blastn: bioinfo/datasplit/env/ncbi-blast-2.13.0+/bin/blastn
    rfam_database: /mnt/clustre/users/sanger-dev/app/database/align/ncbi/db/rfam_v14.6/rfam
    rfam_stat_script: '{package_dir}/datasplit/blast_rfam_stat.py'
    rfam_seed: /mnt/clustre/users/sanger-dev/app/database/align/ncbi/db/rfam_v14.6/Rfam.seed
env:
    LD_LIBRARY_PATH: '{software_dir}/bioinfo/datasplit/Miniconda3/envs/datasplit/lib/'
    #BCFTOOLS_PLUGINS: '{software_dir}/bioinfo/dna/bcftools-1.16/plugins'
"""

tool_global_config = yaml.load(TOOL_GLOBAL_CONFIG_YAML, yaml.Loader)
