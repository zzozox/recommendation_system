# -*- codeing = utf-8 -*-
# 

# 2/16 11:23
# 
# @File :userApi.py
# #Desc :这个是用户接口的文件
import json

from flask import Blueprint, request, flash, session, jsonify

from base.code import ResponseCode, ResponseMessage
from base.response import ResMsg
from base.core import db
from models.model import valid_login, valid_register, User, user_schema

userBp = Blueprint("user", __name__)

# 前端用来获取用户信息的接口
@userBp.route( '/userinfo', methods=["POST"])
def userinfo():
    res = ResMsg()
    username = request.json['username']
    user = User.query.filter(User.username == username).first()
    print(user)
    # data = dict(zip(user.keys(), user))
    data = user_schema.dump(user)
    res.update(code=ResponseCode.SUCCESS, data=data)
    return res.data

@userBp.route( '/get/<id>', methods=["GET"])
def get(id):
    res = ResMsg()
    user = User.query.filter(User.id == id).first()
    print(user)
    data = user_schema.dump(user)
    res.update(code=ResponseCode.SUCCESS, data=data)
    return res.data

# 登录接口，验证用户名和密码
@userBp.route( '/login', methods=["POST"])
def login():
    res = ResMsg()
    username = request.json['username']
    password = request.json['password']
    if valid_login(username, password):
        # flash(username + "登录成功")
        session['username'] = username
        userId = db.session.query(User.id).filter(User.username==username).first()
        # print(userId)
        res.update(code=ResponseCode.SUCCESS,msg=ResponseMessage.SUCCESS,data=userId[0])
    else:
        res.update(code=ResponseCode.ACCOUNT_OR_PASS_WORD_ERR,msg=ResponseMessage.ACCOUNT_OR_PASS_WORD_ERR)
    return res.data

# 注销接口，清除session中的用户名
@userBp.route( '/logout')
def logout():
    res = ResMsg()
    session.pop('username', None)
    return res.data

# 用户注册接口，前端提供表单给这个接口后完成注册，会验证用户名是否存在
@userBp.route('/register', methods=["POST"])
def register():
    res = ResMsg()
    username = request.json['username']
    password = request.json['password']
    realname = request.json['realname']
    if valid_register(username):
        user = User(username=username, password=password, realname=realname)
        db.session.add(user)
        db.session.commit()
        res.update(code=ResponseCode.SUCCESS)
    else:
        res.update(code=ResponseCode.USERNAME_ALREADY_EXIST, msg=ResponseMessage.USERNAME_ALREADY_EXIST)
    return res.data

@userBp.route('/idconfirm', methods=["POST"])
def idconfirm():
    res = ResMsg()
    id = request.json['id']
    idno = request.json['idno']
    realname = request.json['realname']
    db.session.query(User).filter(User.id == id).update({"idno": idno, "realname": realname})
    db.session.commit()
    res.update(code=ResponseCode.SUCCESS)
    return res.data

@userBp.route('/update', methods=["POST"])
def update():
    res = ResMsg()
    id = request.json['id']
    # realname = request.json['realname']
    phone = request.json['phone']
    email = request.json['email']
    avatar = request.json['avatar']
    intro = request.json['intro']
    addr = request.json['addr']
    age = request.json['age']
    print(id)
    db.session.query(User).filter(User.id == id).update({"phone":phone, \
                                                         "email":email,"avatar":avatar,"intro":intro,\
                                                         "addr":addr,"age":age})
    db.session.commit()
    res.update(code=ResponseCode.SUCCESS)
    return res.data

@userBp.route('/modifypass', methods=["POST"])
def modifypass():
    res = ResMsg()
    id = request.json['id']
    password = request.json['password']
    db.session.query(User).filter(User.id == id).update({"password": password})
    db.session.commit()
    res.update(code=ResponseCode.SUCCESS)
    return res.data

# 这个函数非常关键，由于数据库的连接数是有限的，所以在操作完之后，一定要关闭db连接
# 这个方法可以在请求完之后自动关闭连接，这样就不需要每个接口里手动写关闭连接接口
@userBp.after_request
def close_session(response):
    db.session.close()
    return response
