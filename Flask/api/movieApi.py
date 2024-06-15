# -*- codeing = utf-8 -*-
# 

# 2/16 11:23
# 
# @File :movieApi.py
# #Desc :这个是电影接口的文件

import operator

from flask import Blueprint, request
from sqlalchemy import func
from sqlalchemy.sql import label

from algorithm import ItemCF, UserCF
from base.code import ResponseCode, ResponseMessage
from base.core import db
from base.response import ResMsg
from models.comments import Comment, comment_schema
from models.model import chart_data
from models.movie import getWords, Movie, movie_schema

# Blueprint的作用就是一个前缀，相当于前端访问下面的接口的时候地址前都会加上movie
# 如  http://localhost:5000/movie/getWordCut 这样
# 好处就是很容易区分这个接口是在哪个模块下的，逻辑很清晰
movieBp = Blueprint("movie", __name__)

# 分词接口，调用Jieba分词，给前端的词云图提供数据
@movieBp.route('/getWordCut', methods=["GET"])
def getWordCut():
    res = ResMsg()
    result = getWords()
    res.update(code=ResponseCode.SUCCESS, data=result)
    return res.data

# 搜索，这个搜索是给电影库用的，带了关键词这个参数
@movieBp.route('/get', methods=["GET"])
def get():
    res = ResMsg()
    keyword = request.args.get('keyword')
    if keyword is None:
        keyword = ""
    # print(keyword)
    result = db.session.query(Movie).filter(Movie.name.like('%' + keyword + '%')).order_by(Movie.douban_score.desc()).all()[:8]
    data = movie_schema.dump(result)
    res.update(code=ResponseCode.SUCCESS, data=data)
    return res.data

# 热门--根据评分
@movieBp.route('/getHot', methods=["GET"])
def getHot():
    res = ResMsg()
    # 热门只显示4个， 所以进行了切片，如果是数据很多的情况下，切片非常慢，最好直接用limit来访问数据库
    result = db.session.query(Movie).order_by(Movie.douban_score.desc()).all()[:4]
    # 使用Marshmallow来对结果封装json
    data = movie_schema.dump(result)
    res.update(code=ResponseCode.SUCCESS, data=data)
    return res.data

# 推荐 这个只是获取评分高的科幻电影，不是真实的推荐接口，目前前端应该没有调用这个接口
@movieBp.route('/getRec', methods=["GET"])
def getRec():
    res = ResMsg()
    result = db.session.query(Movie).filter(Movie.genres.like('%科幻%')).order_by(Movie.douban_score.desc()).all()[:4]
    data = movie_schema.dump(result)
    res.update(code=ResponseCode.SUCCESS, data=data)
    return res.data

@movieBp.route('/getChart1', methods=["GET"])
def getChart1():
    res = ResMsg()
    all = []
    dz = []
    kh = []
    aq = []
    xj = []
    ranges = [('1900', '1950'), ('1950', '1960'), ('1960', '1970'), ('1970', '1980'), ('1980', '1990'),
              ('1990', '2000'), ('2000', '2010'), ('2010', '2020'), ('2020', '2030')]
    for r in ranges:
        cnt = db.session.query(Movie).filter(Movie.year >= r[0], Movie.year < r[1]).count()
        dzcnt = db.session.query(Movie).filter(Movie.genres.like('%动作%'), Movie.year >= r[0], Movie.year < r[1]).count()
        khcnt = db.session.query(Movie).filter(Movie.genres.like('%科幻%'), Movie.year >= r[0], Movie.year < r[1]).count()
        aqcnt = db.session.query(Movie).filter(Movie.genres.like('%爱情%'), Movie.year >= r[0], Movie.year < r[1]).count()
        xjcnt = db.session.query(Movie).filter(Movie.genres.like('%喜剧%'), Movie.year >= r[0], Movie.year < r[1]).count()

        chart = dict(name=r[0] + '-' + r[1], value=cnt)
        all.append(chart)
        chart2 = dict(name=r[0] + '-' + r[1], value=dzcnt)
        dz.append(chart2)
        chart3 = dict(name=r[0] + '-' + r[1], value=khcnt)
        kh.append(chart3)
        chart4 = dict(name=r[0] + '-' + r[1], value=aqcnt)
        aq.append(chart4)
        chart5 = dict(name=r[0] + '-' + r[1], value=xjcnt)
        xj.append(chart5)
    # data = chart_data.dump(result)
    res.update(code=ResponseCode.SUCCESS, data=dict(all=all, kh=kh, dz=dz, aq=aq, xj=xj))
    return res.data

# 面积图接口
@movieBp.route('/getAreaChart', methods=["GET"])
def getAreaChart():
    res = ResMsg()
    kh = []
    ranges = [('1900', '1970'), ('1970', '1990'), ('1990', '2000'), ('2000', '2010'), ('2010', '2020')]
    for r in ranges:
        khcnt = db.session.query(Movie).filter(Movie.year >= r[0], Movie.year < r[1]).count()
        chart3 = dict(name=r[0] + '-' + r[1], value=khcnt)
        kh.append(chart3)
    # data = chart_data.dump(result)
    res.update(code=ResponseCode.SUCCESS, data=dict(kh=kh))
    return res.data

#
@movieBp.route('/getChart2', methods=["GET"])
def getChart2():
    res = ResMsg()
    datas = []
    for i in range(2001, 2021):
        cnt = db.session.query(Movie).filter(Movie.year == i).count()
        chart = dict(name=i, value=cnt)
        datas.append(chart)
    res.update(code=ResponseCode.SUCCESS, data=datas)
    return res.data


@movieBp.route('/getChart3', methods=["GET"])
def getChart3():
    res = ResMsg()
    result = db.session.query(Movie.year.label('name'), func.count('*').label('value')).group_by(Movie.year).order_by(
        Movie.year.asc()).all()
    datas = chart_data.dump(result)
    res.update(code=ResponseCode.SUCCESS, data=datas)
    return res.data

# 查询各类型电影的数量，给出排名
@movieBp.route('/getTypeRank', methods=["GET"])
def getTypeRank():
    res = ResMsg()
    types = ['惊悚', '古装', '武侠', '冒险', '喜剧', '恐怖', '犯罪', '历史', '歌舞', '纪录片', '动画', '科幻', '西部', '战争', '家庭', '传记', '悬疑',
             '儿童', '灾难', '奇幻', '剧情', '同性', '动作', '运动', '音乐', '情色', '爱情']
    datas = []
    for t in types:
        cnt = db.session.query(Movie).filter(Movie.genres.like('%' + t + '%')).count()
        chart = dict(name=t, value=cnt)
        datas.append(chart)
    datas = sorted(datas, key=operator.itemgetter('value'), reverse=True)

    res.update(code=ResponseCode.SUCCESS, data=dict(datas=datas))
    return res.data

# 查询各个国家电影的数量，给世界地图使用
@movieBp.route('/getNationRank', methods=["GET"])
def getNationRank():
    res = ResMsg()
    nations = ['摩纳哥', '西班牙', '印度', '比利时', '塞浦路斯', '英国', '冒险', '韩国', '希腊', '奥地利', '意大利', '动画', '德国', '泰国', '喜剧', '澳大利亚',
               '中国台湾', '巴西', '中国香港', '墨西哥', '加拿大', '匈牙利', '中国大陆', '瑞典', '新西兰', '卡塔尔', '捷克', '瑞士', '南非', '法国', '伊朗',
               '黎巴嫩', '阿联酋', '日本', '悬疑', '约旦', '爱尔兰', '波兰', '丹麦', '美国', '阿根廷', '荷兰']
    datas = []
    for t in nations:
        cnt = db.session.query(Movie).filter(Movie.regions.like('%' + t + '%')).count()
        chart = dict(name=t, value=cnt)
        datas.append(chart)
    datas = sorted(datas, key=operator.itemgetter('value'), reverse=True)

    res.update(code=ResponseCode.SUCCESS, data=dict(datas=datas))
    return res.data

# 这个代码暂时不用，注释掉
# @movieBp.before_request
# def init_session():
#     db.session = db.session.session_factory()

# 给出各个类型的评分，给散点图提供数据 （评分分析）
@movieBp.route('/getTypeRate', methods=["GET"])
def getTypeRate():
    res = ResMsg()
    types = ['剧情','爱情', '喜剧',  '冒险', '犯罪']
    datas = []
    for t in types:
        data = []
        movies = db.session.query(Movie).filter(Movie.genres.like('%' + t + '%')).all()
        for m in movies:
            rateData = []
            rateData.append(int(m.year))
            rateData.append(m.douban_score)
            data.append(rateData)
        datas.append(data)
    res.update(code=ResponseCode.SUCCESS, data=dict(datas=datas, labels=types))
    return res.data

# 是时间轴图提供数据，查询各个国家在2000-2021电影的出品情况
@movieBp.route('/getTimeLine', methods=["GET"])
def getTimeLine():
    res = ResMsg()
    types = ['美国', '英国', '日本', '中国香港', '中国大陆', '法国', '德国', '韩国', '意大利', '加拿大','中国台湾','澳大利亚','西班牙','印度','瑞士','新西兰']
    datas = []
    for y in range(2000, 2021):
        yearData = []
        for t in types:
            cnt = db.session.query(Movie).filter(Movie.year==y, Movie.regions.like('%' + t + '%')).count()
            yearData.append(cnt)
        datas.append(yearData)

    res.update(code=ResponseCode.SUCCESS, data=dict(datas=datas))
    return res.data

# Flask 推荐算法接口（基于itemCF）
# 只推荐A领域的东西给目标用户，因为目标用户的主要兴趣点在A领域，
# 这样他有限的推荐列表中就会包含该领域一定数量不热门的物品，所以推荐长尾能力较强，但多样性不足
# 举例： 电影、购物、音乐网站等
@movieBp.route('/getRecomendation', methods=["GET"])
def getRecomendation():
    userId = request.args.get('userId')
    userId = int(userId)
    res = ResMsg()
    rates = []
    dd = []
    datas = ItemCF.recommend(userId)
    for id, rate in datas:
        print(id)
        movie = db.session.query(Movie).filter(Movie.id == id).first()
        dd.append(movie)
        rates.append(rate)
    data = movie_schema.dump(dd)
    res.update(code=ResponseCode.SUCCESS, data=dict(datas=data, rates=rates))
    return res.data

# Flask 推荐算法接口（基于userCF）
# 系统会找到与目标用户兴趣相似的其他用户然后将其他用户关注的东西推荐给目标用户，所以是某个群体内的热门物品；
# 同时也反应出如果某些物品没有被该群体关注，则不会推荐给该群体，即推荐长尾能力的不足
# 举例： 微博热搜、热点新闻等
@movieBp.route('/getRecomendation2', methods=["GET"])
def getRecomendation2():
    userId = request.args.get('userId')
    userId = int(userId)
    res = ResMsg()
    datas = UserCF.recommend(userId)
    dd = []
    rates = []
    for id, rate in datas:
        # print(id)
        movie = db.session.query(Movie).filter(Movie.id==id).first()
        dd.append(movie)
        rates.append(rate)
    data = movie_schema.dump(dd)
    res.update(code=ResponseCode.SUCCESS, data=dict(datas=data, rates=rates))
    return res.data

# 查询影评数据的接口
@movieBp.route('/getComments', methods=["POST"])
def getComments():
    res = ResMsg()
    douban_id = request.json['douban_id']
    comments = db.session.query(Comment).filter(Comment.douban_id == douban_id).all()
    data = comment_schema.dump(comments)

    res.update(code=ResponseCode.SUCCESS, data=data)
    return res.data

# 这个函数非常关键，由于数据库的连接数是有限的，所以在操作完之后，一定要关闭db连接
# 这个方法可以在请求完之后自动关闭连接，这样就不需要每个接口里手动写关闭连接接口
@movieBp.after_request
def close_session(response):
    db.session.close()
    return response
