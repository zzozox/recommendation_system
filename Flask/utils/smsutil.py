# -*- codeing = utf-8 -*-


# 4/4 10:47
# 
# @File: smsutil.py
# @Desc:
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

class Sms():

    # 短信签名秘钥，通过工信部网站ICP备案后才可以申请
    # 短信服务是收费服务，秘钥请勿泄漏到网上。
    def __init__(self):
        self.accessKeyId = 'LTAI5tSeYfPtcmWnE7YZ1YDa'
        self.accessSecret = 'MkZg7NiOiRrwo3dX6faPRh7nVRgnL5'
        self.RegionId = 'cn-hangzhou'
        self.client = AcsClient(self.accessKeyId, self.accessSecret, self.RegionId)
        self.CommonRequest = CommonRequest()
        self.CommonRequest.set_accept_format('json')
        self.CommonRequest.set_domain('dysmsapi.aliyuncs.com')
        self.CommonRequest.set_method('POST')
        self.CommonRequest.set_protocol_type('https')  # https | http
        self.CommonRequest.set_version('2017-05-25')

    # 发送短信
    def sendCode(self, phone, code):
        self.CommonRequest.set_action_name('SendSms')
        self.CommonRequest.add_query_param('PhoneNumbers', phone)
        self.CommonRequest.add_query_param('SignName', '大数据旅游网')
        self.CommonRequest.add_query_param('TemplateCode', 'SMS_238136898')
        self.CommonRequest.add_query_param('TemplateParam', "{\"code\":\"%s\"}" % code)
        response = self.client.do_action(self.CommonRequest)
        print(str(response, encoding='utf-8'))
        return response