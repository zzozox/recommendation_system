# -*- codeing = utf-8 -*-
# 

# 3/17 11:12
# 
# @File: alipay.py
# @Desc:
import json
import time
import uuid

from alipay import AliPay
from flask import Blueprint, redirect, request

from base.code import ResponseCode
from base.constant import app_private_key_string, alipay_public_key_string, alipay_nofity_url
from base.core import db
from base.response import ResMsg
from models.model import User
from models.order import Order

payBp = Blueprint("alipay", __name__)

@payBp.route('/pay', methods=["POST"])
def testpay():
    res = ResMsg()
    order_total = request.json['addBal']
    order_numbering = request.json['orderId']
    subject = request.json['subject']
    # print(uid)
    # print(order_total)

    alipay = AliPay(
        appid="2016092500594263",  # 第3步中的APPID
        app_notify_url=alipay_nofity_url,  # 默认回调url
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",
        debug=False
    )

    # 电脑网站支付
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_numbering,  # 你自己生成的订单编号, 字符串格式
        total_amount=order_total,  # 订单总金额, 字符串格式
        subject=subject,  # 订单主题,可随便写
        return_url="",  # 支付完成后要跳转的页面, 完整的url地址,包括域名
        notify_url=alipay_nofity_url  # 可选, 不填则使用默认notify url
    )
    url = "https://openapi.alipaydev.com/gateway.do?" + order_string
    res.update(code=ResponseCode.SUCCESS, data=url)
    return res.data

@payBp.route('/notify', methods=["POST"])
def notify():
    res = ResMsg()
    data = request.form.to_dict()
    signature = data.pop("sign")
    print(json.dumps(data))
    # res = json.dumps(data)
    # print(data.pop('trade_status'))
    # 处理支付宝调用成功
    if data.pop('trade_status') == "TRADE_SUCCESS":
        oid = data.pop('out_trade_no')
        print(oid)
        order = db.session.query(Order).filter(Order.id == oid).first()
        print(order.user_id)
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        db.session.query(Order).filter(Order.id == oid).update({"status": 1, "update_time": current_time})
        user = db.session.query(User).filter(User.id == order.user_id).first()
        db.session.query(User).filter(User.id == order.user_id).update({"bal": user.bal + order.amount})
        db.session.commit()
    res.update(code=ResponseCode.SUCCESS)
    return res.data