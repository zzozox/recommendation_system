# -*- codeing = utf-8 -*-
# 

# 3/10 16:12
# 
# @File: fileApi.py
# @Desc:
import os

from flask import Flask, send_from_directory
from aip import AipOcr

APP_ID = '23995255'
API_KEY = 'nbKNqoVPa3eOFwQ3A6EBRTGp'
SECRET_KEY = 'tuuVDpiYXh5v53IUMktD0QFFLUAQGj8V'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

idCardSide = "back"

# 读取图片
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def idocr(filename):
    print("当前路径 -> %s" % os.getcwd())
    image = get_file_content(filename)
    result = client.idcard(image, idCardSide)
    print("姓名:", result['words_result']['姓名']['words'])
    print("性别:", result['words_result']['性别']['words'])
    print("民族:", result['words_result']['民族']['words'])
    print("出生:", result['words_result']['出生']['words'])
    print("公民身份号码:", result['words_result']['公民身份号码']['words'])
    print("住址:", result['words_result']['住址']['words'])
    return  result['words_result']['公民身份号码']['words'], result['words_result']['姓名']['words']

