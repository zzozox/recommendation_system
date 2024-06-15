# -*- codeing = utf-8 -*-
# 

# 2/15 16:27
# 
# @File :testApi.py
from datetime import datetime
from decimal import Decimal

from flask import Blueprint

from base.code import ResponseCode
from base.response import ResMsg

bp = Blueprint('test', __name__)

# 这几个接口都是测试方法，可以不看
@bp.route( '/test', methods=["GET"])
def test_type():
    """
    测试响应封装
    :return:
    """
    res = ResMsg()
    now = datetime.now()
    date = datetime.now().date()
    num = Decimal(11.11)
    test_dict = dict(now=now, date=date, num=num)
    # 此处只需要填入响应状态码,即可获取到对应的响应消息
    res.update(code=ResponseCode.SUCCESS, data=test_dict)
    # 此处不再需要用jsonify，如果需要定制返回头或者http响应如下所示
    # return res.data,200,{"token":"111"}
    return res.data

@bp.route( '/test2', methods=["GET"])
def test_packed_response():
    """
    测试响应封装
    :return:
    """
    res = ResMsg()
    test_dict = dict(name="zhang", age=18)
    # 此处只需要填入响应状态码,即可获取到对应的响应消息
    res.update(code=ResponseCode.SUCCESS, data=test_dict)
    # 此处不再需要用jsonify，如果需要定制返回头或者http响应如下所示
    # return res.data,200,{"token":"111"}
    return res.data

@bp.route( '/db_test1', methods=["GET"])
def db_test1():
    res = ResMsg()
    test_dict = dict(name="zhang", age=18)
    # 此处只需要填入响应状态码,即可获取到对应的响应消息
    res.update(code=ResponseCode.SUCCESS, data=test_dict)
    # 此处不再需要用jsonify，如果需要定制返回头或者http响应如下所示
    # return res.data,200,{"token":"111"}
    return res.data
