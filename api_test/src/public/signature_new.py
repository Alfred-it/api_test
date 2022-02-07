import json

import jpype

from src.public.send_msg import SendMsg
from src.utils.log_opt import error, info, debug


class JVMUtils:
    def __init__(self):
        # 对应jar包已脱敏删除
        self.jarPath = "/Users/zhouyu/Desktop/project/api_test/lib/signature-1.0-SNAPSHOT.jar"
        self.jarPath2 = "/Users/zhouyu/Desktop/project/api_test/lib/xy-signature2.0-1.0-SNAPSHOT.jar"
        self.dependency = "/Users/zhouyu/Desktop/project/api_test/lib"

    def startJVM(self):
        # jpype.startJVM()
        jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=" + self.jarPath2,
                       "-Djava.ext.dirs=%s" % self.dependency)

    def stopJVM(self):
        jpype.shutdownJVM()


jvm = JVMUtils()


class Get_signature_new_url(object):
    def __init__(self, method, req_url, req_data, appSecret, appid, enterpriseid,sign_version="1.0",encryptionKey="",access_token="",client_type=""):
        self.method = method
        self.req_url = req_url
        self.req_data = req_data
        self.appid = appid
        self.appSeccret = appSecret
        self.enterpriseid = enterpriseid
        self.sendmsg = SendMsg()
        self.sign_version = sign_version
        self.encryptionKey = encryptionKey
        self.access_token = access_token
        self.client_type=client_type

        info(access_token)

    def get_encryptionKey(self):
        url = "**********"
        header = {
            "Content-Type": "application/json",
            "x-xy-clientid": self.appid
        }
        body = {
            "k1": self.appid,
            "k2": self.appSeccret,
            "k3": self.enterpriseid
        }
        jbody = json.dumps(body)

        res = ""
        try:
            res = self.sendmsg.send_msg("post", url=url, data=jbody, header=header)
        except Exception as e:
            error(e)
            error("failed to get access_token or signSecret")

        if res.status_code != 200:
            error("fail to get access_token or signSecret.......")
            error(url)
            error(header)
            error(body)
            error(res.status_code)
            error(res.text)

        resdata = json.loads(res.text)



        signSecret = resdata["data"]["***"]
        self.access_token = resdata["data"]["***"]

        return signSecret

    def get_url(self):

        # jarPath ="/Users/zhouyu/Desktop/project/api_test/lib/signature-1.0-SNAPSHOT.jar"
        # dependency = "/Users/zhouyu/Desktop/project/api_test/lib"
        #
        # startJVM(get_default_jvm_path(), "-ea", "-Djava.class.path="+jarPath,"-Djava.ext.dirs=%s" % dependency)

        # method = "POST"
        global resDict
        method = str.upper(self.method)

        uri = self.req_url
        # requestBody = {"meetingName": "my first cloudRoom"}
        requestBody = self.req_data

        encryptionKey = self.encryptionKey

        SignUtil1 = jpype.JClass("***")
        s1 = SignUtil1(self.appid)

        SignUtil2 = jpype.JClass("***")
        s2 = SignUtil2(self.appid)

        if self.encryptionKey == "":
            encryptionKey= self.get_encryptionKey()
            if self.sign_version == "1.0":
                res = s1.getLastUrl(method, uri, str(requestBody), self.access_token, "SHA256")
            else:
                res = s2.getLastUrl(method, uri, str(requestBody), encryptionKey+"&","SHA256")
        else:
            res = s2.getLastUrl(method, uri, str(requestBody), encryptionKey+"&", "SHA256")
        try:
            resDict = json.loads(str(res))
        except Exception as e:
            error(e)

        if self.access_token != "":
            resDict["***"] = "Bearer" + " " + self.access_token

        if self.client_type != "":
            resDict["***"] = self.client_type

        resDict["***"] = self.sign_version
        # resDict["x-xy-sign"] = "123"

        # info(type(resDict))

        return resDict
# g = Get_signature_url()
# g.get_url()
