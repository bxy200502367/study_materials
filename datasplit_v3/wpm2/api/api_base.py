# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
Last-edit: 2022/05/15
Author: yuan.xu
mail: yuan.xu@majorbio.com
"""

import json
import time
import gevent
from bson.objectid import ObjectId
from biocluster.api.database.base import Base


class ApiBase(Base):
    """
    基础database api
    """

    def __init__(self, bind_object):
        """
        api基类，可以用于将列表导表入库，以及完成momgo表的查找，更新等
        """
        super(ApiBase, self).__init__(bind_object)
        self._project_type = "datasplit"
        self._api_factory = {
            "find_one": self.find_one,
            "find_many": self.find_many,
            "insert_one": self.insert_data,
            "insert_many": self.insert_data,
            "update": self.update_db_record
        }

    def find_one(self, collection, query_dic):
        """
        用于mongo查询一条记录，查询字段是一个字典,支持一个字段的查询，也支持多个字段的查询
        example: {"batch_id": ObjectID("5a782577a4e1af477e1ac081"), "type": "pt"}
        :param collection:
        :param query_dic:
        :return:
        """
        collection = self.db[collection]
        result = collection.find_one(query_dic)
        # if not result:
        #     print ("没有找到{}表中的{}结果，请检查".format(collection, query_dic.keys()))
        return result

    def find_many(self, collection, query_dic):
        """
        用于mongo查询多条记录，查询字段是一个字典,支持一个字段的查询，也支持多个字段的查询
        example: {"batch_id": ObjectID("5a782577a4e1af477e1ac081"), "type": "pt"}
        :param collection:
        :param query_dic:
        :return:
        """
        collection = self.db[collection]
        return collection.find(query_dic)

    def insert_data(self, collection, data_list=None, data=None):
        """
        插入多条记录，data_list样例格式[{"1":"2"},{"2":"3"},{"3": "4"}]
        这里只是抽象出，进行大规模的mongo插表,这里兼容了插入一条记录与多条记录
        :param collection:
        :param data_list (多记录):
        :param data (单记录):
        :return:
        """
        start = time.time()
        table_id = None
        con = self.db[collection]
        record_num = 0
        if data:
            record_num = 1
            try:
                table_id = con.insert_one(data_list[0]).inserted_id
            except Exception:
                raise Exception("往{}插入一条记录失败".format(collection))
            else:
                self.bind_object.logger.info("往{}插入一条记录成功".format(collection))
        elif data_list:
            record_num = len(data_list)
            try:
                if record_num > 5000000:
                    for i in range(0, record_num, 4000000):
                        temp = data_list[i:i + 4000000]
                        con.insert_many(temp)
                elif record_num >= 2:
                    con.insert_many(data_list)
                else:
                    table_id = con.insert_one(data_list[0]).inserted_id
            except Exception:
                if record_num >= 2:
                    raise Exception("往{}插入多条记录失败".format(collection))
                raise Exception("往{}插入一条记录失败".format(collection))
            else:
                if record_num >= 2:
                    self.bind_object.logger.info(
                        "往{}插入多条记录成功".format(collection))
                else:
                    self.bind_object.logger.info(
                        "往{}插入一条记录成功".format(collection))
        else:
            raise Exception("插入数据为空，不能进行后面的插表操作")
        end = time.time()
        self.bind_object.logger.info("文件导入mongo中花费的时间:{}".format(end - start))
        return table_id

    def gevet_insert_data(self, collection, data, step=100000):
        """
        实现并发导表，当一个文件比较大的时候，将文件存入data列表中，然后按照step步长进行分割导表
        :param collection:
        :param data:
        :param step:
        :return:
        """
        start = time.time()
        gevent_data = []
        data_length = len(data)
        for i in range(0, data_length, step):
            temp = data[i:i + step]
            gevent_data.append(
                gevent.spawn(self.insert_data, collection, temp, "true"))
        self.bind_object.logger.info("gevent data length: {}".format(
            len(gevent_data)))
        gevent.joinall(gevent_data)
        end = time.time()
        self.bind_object.logger.info("gevent 导表花费时间：{}".format(end - start))

    def update_db_record(self, collection, update_dict, query_dict, **options):
        """
        用于更新表格的字段，暂时只是简单的更新一个表的对应字段，后面有需求再进行完善
        :param collection: 集合的名称
        :param query_dict: 查询的字段，可以有多个字段进行联合查询, 是一个字典
        :param update_dict: 表格中要更新进去的字段
        :param upsert: 表中没有查找到对应条件的记录，确认是否要更新 默认为True
        :param multi: 表中按照对应条件查找到多条记录，是否要全部更新 默认为True
        :return:
        """
        upsert = options["upsert"] if "upsert" in options.keys() else True
        multi = options["multi"] if "multi" in options.keys() else True
        try:
            self.db[collection].update(
                query_dict, {'$set': self.deflatten_dict(update_dict)},
                upsert=upsert,
                multi=multi)
        except Exception:
            raise Exception("更新表格{}失败!".format(collection))
        else:
            self.bind_object.logger.info("更新表格{}成功！".format(collection))

    def data_split(self, list_data, step=400000):
        """
        当一条记录中的，某个字段的值大于16M的时候，我们要进行切割后重组后导表
        :param list_data:
        :param step: 按照400000切割
        :return:
        """
        new_data = []
        if len(list_data) < step:
            new_data.append(list_data)
        else:
            for i in range(0, len(list_data), step):
                temp = list_data[i:i + step]
                new_data.append(temp)
        return new_data

    def check_objectid(self, id_):
        """
        用于检查并转成成ObjectID
        :param id_:
        :return:
        """
        if not isinstance(id_, ObjectId):
            if isinstance(id_, str):
                id_ = ObjectId(id_)
            else:
                raise ValueError("id必须为ObjectId对象或其对应的字符串!")
        return id_

    def deflatten_dict(self, sdict):
        """把单层key-value类型变为嵌套dict

        Args:
            sdict (dict): 单层kv dict
        """
        out_dict = {}
        for key, value in sdict.items():
            if isinstance(value, str):
                try:
                    temp = json.loads(value)
                except ValueError as _:
                    out_dict[key] = value
                else:
                    out_dict[key] = temp
            else:
                out_dict[key] = value
        return out_dict

    def api_factory(self, collection, api_type, **options):
        """api 工厂函数

        Args:
            collection (str): 表名
            api_type (str): 车间
            options (any): 输入参数
        """
        self.bind_object.logger.info("调用工厂{}导表{}！".format(
            api_type, collection))
        self._api_factory[api_type](collection, **options)
