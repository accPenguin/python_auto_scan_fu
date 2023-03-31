import requests
import os
import codecs
import sys
import time
import json
import re

class WebRequests:

    def __init__(self):
        self.dirPath = ''
        self.getCaptchaUrl = 'https://rds.alipay.com/captcha.htm'

        self.getResultUrl = 'https://mobilegw.alipay.com/mgw.htm'

        self.operationType = {
            'sendVerifyCode': 'alipay.tradecsa.biz.blessingprod.wufu2021.sendVerifyCode',
            'outPrize': 'alipay.tradecsa.biz.blessingprod.wufu2021.outPrize'
        }

        self.s = requests.Session()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 10; zh-CN; MI 9 Build/QKQ1.190828.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 Quark/4.3.3.145 Mobile Safari/537.36 Edg/89.0.4389.6',
            'DNT': '1'
        }

    def loads_jsonp(self, _jsonp):
        try:
            return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
        except:
            raise ValueError('Invalid Input')

    def getCaptcha(self, mobile, source):
        digits = 32
        hex = codecs.encode(os.urandom(digits), 'hex').decode()
        data = {
            'appid': "blessingprod_wufu_otp",
            'bizNo': hex,
            'mobile': mobile,
            'refer': "",
            'scene': "DO_NOTHING",
            'type': "silence",
            'useragent': "Mozilla/5.0 (Linux; U; Android 10; zh-CN; MI 8 UD Build/QKQ1.190828.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 Quark/4.3.3.145 Mobile Safari/537.36 Edg/89.0.4389.6"
        }
        self.s.options(self.getCaptchaUrl)
        try:
            r = self.s.post(self.getCaptchaUrl, json=data,
                            headers=self.headers)
            # print(r.text)

            rdsToken = json.loads(r.content)['data']['extra']['token']
            requestData = [{"mobile": mobile, "source": source,
                            "rdsBizNo": hex, "rdsToken": rdsToken}]
            getResultData = {
                '_fli_online': True,
                'operationType': self.operationType['sendVerifyCode'],
                'requestData': str(requestData),
                '_': int(round(time.time() * 1000)),
                'callback': 'jsonp' + str(int(round(time.time() * 1000)))
            }

            re = self.s.get(self.getResultUrl,
                            params=getResultData, headers=self.headers)
            # 'jsonp16121({"resultStatus":1000,"result":{"code":"5101","resultView":"人气太旺了，请稍后再试","success":true}})'
            # print(re.text)
            re_json = self.loads_jsonp(re.text)
            if re_json['result']['success'] == True:
                return {"code": 1000, "info": f'成功获取验证码，请注意查收'}
            else:
                resultView = re_json['result']['resultView']
                return {"code": 1001, "info": f'获取验证码失败，原因为{resultView}'}
        except Exception as e:
            return {"code": 1001, "info": f'获取验证码失败，原因为 {e}'}

    def getResult(self, mobile, source, ackCode):
        requestData = [
            {"mobile": mobile, "source": source, "ackCode": str(ackCode)}]
        getResultData = {
            '_fli_online': True,
            'operationType': self.operationType['outPrize'],
            'requestData': str(requestData),
            '_': int(round(time.time() * 1000)),
            'callback': 'jsonp' + str(int(round(time.time() * 1000)))
        }

        try:

            re = self.s.get(self.getResultUrl,
                            params=getResultData, headers=self.headers)
            # jsonp16121({"resultStatus":1000,"result":{"code":"50144","hasPrized":false,"hasUserId":false,"resultView":"已经领取过奖品","success":false}})
            # print(re.text)
            re_json = self.loads_jsonp(re.text)
            if re_json['result']['success'] == True:
                return {"code": 1000, "info": f'成功领取'}
            else:
                resultView = re_json['result']['resultView']
                return {"code": 1001, "info": f'领取失败，原因为 {resultView}'}
        except Exception as e:
            return {"code": 1001, "info": f'领取失败，原因为 {e}'}

    def getSiteNum(self):
        path = os.path.join(self.dirPath, "site.json")
        with open(path, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
            return len(json_data['channelList'])

    def getSiteInfo(self, num):
        path = os.path.join(self.dirPath, "site.json")
        with open(path, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
            length = len(json_data['channelList'])
            if num > length:
                print(f"站点的长度为{length}，{num}已经超出这个长度")
                return None
            return json_data['channelList'][num-1]

    def getAllSiteInfo(self):
        path = os.path.join(self.dirPath, "site.json")
        with open(path, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
            return json_data['channelList']

    def getSiteName(self, siteInfo):
        return siteInfo['sourceList'][0]['name']

    def getSiteSource(self, siteInfo):
        return siteInfo['sourceList'][0]['source']

    def addSuccessSite(self, siteInfo):
        path = os.path.join(self.dirPath, "success.json")
        add = self.isSuccessSite(siteInfo)
        if add == False:
            with open(path, 'r+', encoding='utf8')as fp:
                json_data = json.load(fp)
            with open(path, 'w', encoding='utf8')as fp:
                json_data['channelList'].append(siteInfo)
                fp.write(json.dumps(json_data, indent=4))

    def isSuccessSite(self, siteInfo):
        path = os.path.join(self.dirPath, "success.json")
        with open(path, 'r+', encoding='utf8')as fp:
            json_data = json.load(fp)
            if siteInfo in list(json_data['channelList']):
                return True
            else:
                return False

def main(path):
    webRequests = WebRequests()
    webRequests.dirPath = path
    print(f"总共有{webRequests.getSiteNum()}个站点可以领取福卡")
    for i in range(1, webRequests.getSiteNum()+1):
        siteInfo = webRequests.getSiteInfo(i)
        siteName = webRequests.getSiteName(siteInfo)
        print(f"{i}：{siteName}")

    startSite = int(input("您要从第几个站点开始向后领取？"))
    mobile = input("请输入您的手机号:")

    for i in range(startSite, webRequests.getSiteNum()+1):
        siteInfo = webRequests.getSiteInfo(i)
        siteName = webRequests.getSiteName(siteInfo)
        siteSource = webRequests.getSiteSource(siteInfo)
        if webRequests.isSuccessSite(siteInfo):
            print(f"{i}：{siteName} 已经成功领取，跳过")
            continue
        print(f"{i}：{siteName} 正在领取中")
        result = webRequests.getCaptcha(mobile, siteSource)
        print(result['info'])
        if result['code'] == 1001:
            if str(result['info']).find("验证码发送过频繁") != -1:
                print("验证码需等待60s后才能获取，正在等待..")
                time.sleep(60)
                result = webRequests.getCaptcha(mobile, siteSource)
            if str(result['info']).find("人气太旺啦，稍候再试试") != -1:
                print("您的手机号在近期已经获得了多次支付宝验证码，已被支付宝限制，24小时内无法再获得验证码，程序终止。")
                break
            elif str(result['info']).find("人气太旺啦，稍候再试试") == -1 and str(result['info']).find("验证码发送过频繁") == -1:
                continue
        ackCode = input("请输入验证码：")
        result = webRequests.getResult(mobile, siteSource, ackCode)
        print(result['info'])

        if result['code'] == 1000 or result['info'].find("已经领取过奖品") != -1:
            webRequests.addSuccessSite(siteInfo)

        print("验证码需等待60s后才能获取，正在等待..")
        time.sleep(60)

    input("程序已结束，您可以关闭此程序了")

if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    main(path)
