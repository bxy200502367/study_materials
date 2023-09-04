# 二拆

## webroot

## to_file
### export_sample_split_info<br>***导出二拆的信息***
#### 文件名
- specimen_info_list.xls<br>**一个拆分任务所有样本的信息**
#### 生成文件列名(22列)
- specimen_id(sg_split_specimen)<br>*拆分样本id*
- library_id(sg_split_library)<br>*拆分文库id*
- lane_name(sg_split_library)<br>*lane名*
- library_number(sg_split_library)<br>*文库编号*
- library_type(sg_split_library)<br>*文库插入片段*
- library_s3_path(sg_split_library)<br>*合同数据量*
- library_work_path(sg_split_library)<br>*重命名*
- project_sn(sg_split_specimen)<br>*合同编号*
- product_type(sg_split_specimen)<br>*拆分类型*
- specimen_name(sg_split_specimen)<br>*样本名称*
- majorbio_name(sg_split_specimen)<br>*美吉编号*
- insert_size(sg_split_specimen)<br>*插入片段大小*
- barcode_tag(根据meta_type判断)<br>*barcode_tag*
- f_barcode(根据meta_type判断)<br>*f端barcode序列*
- r_barcode(根据meta_type判断)<br>*r端barcode序列*
- primer(sg_split_specimen)<br>*引物信息*
- link_primer(sg_split_specimen)<br>*link_primer序列*
- reverse_primer(sg_split_specimen)<br>*reverse_primer序列*
- analysis_type(sg_split_specimen)<br>*分析类型，是否是pure_sequence*
- meta_type(根据library_type判断)<br>*多样性类型*
  - official:官方多样性
  - no_official:非官方多样性
  - no_meta:非多样性
- split_method(sg_split_specimen)<br>*拆分类型，Single or Pair，默认为Pair*
- is_its_primer(sg_split_specimen)<br>*是否为ITS引物，no or yes， 默认为no*
### export_sample_split_params<br>***导出二拆meta的参数***
### 文件名
- meta.json<br>**主要的二拆参数**
  - trim_fqseq: 长度过滤
    - m
    - M
  - meta-fastp: fastp过滤
    - leading
    - slidingwindow
    - trailing
    - minlen
  - flash: flash拼接
    - M
    - m
    - x
  - split_by_barcode: 拆分样本
    - mismatch
  - split_type: 拆分类型
    - Auto or Single or Pair

## workflow
### sample_split: 二拆workflow
### 参数
- sample_split_info: 样本信息表，export_sample_split_info的结果
- meta_params: 二拆参数表，export_sample_split_params的结果
- split_id: 拆分id
- update: 更新表信息
### phase_configs: 步骤
- pretreatment_sample_info: 把样本信息表拆开
- parallel_meta: 并行拆分多样性样本