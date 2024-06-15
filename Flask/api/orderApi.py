# -*- codeing = utf-8 -*-
# Author: MiniBigData

# 3/17 11:12
# 
# @File: alipay.py
# @Desc: 订单接口
import json
import time
import uuid

from flask import Blueprint, request
from base.core import db
from base.code import ResponseCode
from base.response import ResMsg
from models.order import Order

orderBp = Blueprint("order", __name__)

@orderBp.route('/add', methods=["POST"])
def addOrder():
    res = ResMsg()
    uid = request.json['uid']
    order_total = request.json['amount']
    type = request.json['type']
    order_numbering = str(uuid.uuid4())  #基于随机数的方法生产一个UUID作为本次支付的订单号，支付宝的订单号必须唯一
    # order_total = 10.0
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    order = Order(id=order_numbering, user_id=uid, amount=order_total, type=type, status=0, create_time=current_time)
    db.session.add(order)
    db.session.commit()
    res.update(code=ResponseCode.SUCCESS, data=order_numbering)
    return res.data

@orderBp.after_request
def close_session(response):
    db.session.close()
    return response