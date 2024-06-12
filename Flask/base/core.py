# -*- codeing = utf-8 -*-
# 

# 2/15 18:48
# 
# @File :core.py

import datetime
import decimal
import uuid

from flask.json import JSONEncoder as BaseJSONEncoder
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 配置这个是可以让SQLAlchemy 在解析JSON的时候自动对时间字段等进行处理
class JSONEncoder(BaseJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            # 格式化日期
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            # 格式化时间
            return o.strftime("%Y-%m-%d")
        if isinstance(o, decimal.Decimal):
            # 格式化高精度数字
            return str(o)
        if isinstance(o, uuid.UUID):
            # 格式化uuid
            return str(o)
        if isinstance(o, bytes):
            # 格式化字节数据
            return o.decode("utf-8")
        return super(JSONEncoder, self).default(o)