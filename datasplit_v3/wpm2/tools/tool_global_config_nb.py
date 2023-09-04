# -*- coding:utf-8 -*-
"""
Author: yiwei.tang
mail: yiwei.tang@majorbio.com
Description: tool公共软件参数
"""
import yaml

TOOL_GLOBAL_CONFIG_YAML = r"""
var:
    mkdir: /usr/bin/mkdir
    mv: /usr/bin/mv
    ln: /usr/bin/ln
    gzip: /usr/bin/gzip
    cat: /usr/bin/cat
    python2: bioinfo/dna/env/bin/python2
    python3: bioinfo/dna/env/bin/python3
    perl: /usr/bin/perl
    lima: bioinfo/dna/smrtlink/install/smrtlink-release_11.0.0.146107/smrtcmds/bin/lima
    generate_pacbio_barcode_file: '{package_dir}/datasplit_v3/pacbio_split/generate_pacbio_barcode_file_datasplit_v3.py'
    generate_pacbio_sample_list: '{package_dir}/datasplit_v3/pacbio_split/generate_pacbio_sample_list_datasplit_v3.py'
    pacbio_rename: '{package_dir}/datasplit_v3/pacbio_split/pacbio_rename_datasplit_v3.py'
    bam_to_fastq: bioinfo/dna/smrtlink/install/smrtlink-release_11.0.0.146107/smrtcmds/bin/bam2fastq
    pacbio_length_filter: '{package_dir}/datasplit_v3/pacbio_split/trim_fqSeq.pl'
    pacbio_correct_seq: '{package_dir}/datasplit_v3/pacbio_split/split_byPrimer2.pl'
    sequence_rename: '{package_dir}/datasplit_v3/pacbio_split/sequence_rename_datasplit_v3.py'
    seqkit: /mnt/lustre/users/sanger-dev/app/bioinfo/dna/env/bin/seqkit
    generate_lima_summary: '{package_dir}/datasplit_v3/pacbio_split/lima_summary_datasplit_v3.py'
env:
    LD_LIBRARY_PATH: '{software_dir}/bioinfo/dna/env/lib'
    BCFTOOLS_PLUGINS: '{software_dir}/bioinfo/dna/bcftools-1.16/plugins'
"""

tool_global_config = yaml.load(TOOL_GLOBAL_CONFIG_YAML, yaml.Loader)
