# -*- codeing = utf-8 -*-
# 

# 3/11 10:31
# 
# @File: mytool.py
# @Desc:

def formatArea(area):
    return float(area.replace("平米",""))

def formatDegree(degree):
    if degree == '博士':
        return 1
    elif degree == '硕士':
        return 3
    elif degree == '本科':
        return 4
    elif degree == '大专':
        return 5
    elif degree == '高中':
        return 7
    elif degree == '初中及以下':
        return 9
    elif degree == '学历不限':
        return -1