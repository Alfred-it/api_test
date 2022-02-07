# -*- coding: utf-8 -*-
import os
import sys
import urllib.parse

from requests_toolbelt import MultipartEncoder

from src.public.signature_new import Get_signature_new_url, jvm
from src.utils.excel_opt import ExcelOperation
from src.utils.json_opt import JsonOperation
from src.utils.log_opt import log, error, info, warning, debug
from src.public.common import SheetColumnName as scn
from src.public.common import *

from src.public.send_msg import SendMsg
from src.public.signature_old import Get_signature_url
import json
import time
import logging.config

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO)


class Execute:
    # excel列名，下标和表格中的顺序一一对应
    name_list = ["name", "is_execute", "method", "header", "URL_head", "ip", "path", "extract_key", "depended_key",
                 "body", "status_code", "ex_answer", "sleep_time", "result"]
    row = 1

    # 缓存（dict）每张表一个缓存，用作接口的数据依赖
    # 相关依赖数据放在这里就行
    cache = {}

    # 每个接口执行后等待的时间，表格中可以自定义
    sleep_time_dafault = 0.1

    # 登录账号，获取有效sk，目前账号是pre环境下的，后续提到配置文件中
    url_login = ""
    data_login = ""

    # data_login={"account":"18118941109","deviceSn":"'CCE505B8-83AF-5A08-AF23-7D983ADAD468","deviceDisplayName":"18644839955","deviceType":"5","model":"MacBookPro11,4","cpu":"Intel(R) Core(TM) i7-4770HQ CPU @ 2.20GHz","cores":"","freq":"","deviceToken":"","softVersion":"","hardVersion":"","packageName":"",
    #             "password":"000000"}

    header = {"Content-Type": "application/json"}

    def __init__(self, data_file_path, sheet_name, jd_file_path, env_config, **kwargs):
        self.cache = {}
        # self.ddt=kwargs["ddt"]
        self.sheet_name = sheet_name
        self.send = SendMsg()
        self.e_opt = ExcelOperation(data_file_path, sheet_name)
        self.json_data = JsonOperation(jd_file_path)
        self.config = self.get_data_config(env_config)
        # self.token = self.json_data.get_data_by_key(env_config)["{token}"]
        self.env_config = env_config
        self.env = self.get_env(env_config)
        self.data_file_path = data_file_path
        self.status_code = 0
        self.signature = ""
        self.signType = self.get_sign_type()
        self.encryptionKey=""
        self.access_token=""
        if self.signType == 2:
            jvm.startJVM()
            # info(self.config.keys())
            self.client_type=""
            if '{signVersion}' in self.config.keys():
                self.signVersion = self.config["{signVersion}"]
            else:
                self.signVersion = "1.0"


        self.exception = self.get_exception_test_config()
        info(self.exception)

        self.body_key_list = []

    def get_exception_test_config(self):
        return True if "{exception}" in self.config.keys() and self.config["{exception}"] == True else False

    # 提取数据
    def get_extract_key(self):
        extract_key = self.row_data[scn["extract_key"]]

        if extract_key != "":
            res_data = ""
            try:
                res_data = json.loads(self.res.text)
            except Exception as e:
                error(e)

            extract_key_js = json.loads(extract_key)

            # info(extract_key_js)

            for key in extract_key_js:

                # 获取{"key":"val"}
                # 单层依赖数据支持依赖数据key自定义名称
                if extract_key_js[key] == "val":
                    temp_key = key + "_ex"
                    # debug(temp_key)

                    if key not in self.res.text:
                        # 目标key加了自定义名称，拿到原始的key
                        res_key = key[0:str(key).rfind("_")]
                    else:
                        # 目标key没有自定义名称
                        res_key = key

                    # 返回值为"[***,***,***]"
                    if isinstance(res_data, list):
                        if "desc" in key:
                            self.cache[temp_key] = res_data[len(res_data) - 1][res_key]
                        self.cache[temp_key] = res_data[0][res_key]
                    else:
                        try:
                            self.cache[temp_key] = res_data[res_key]
                        except Exception as e:
                            warning(e)
                            warning("接口返回值中没有发现key： " + res_key)


                # 获取{"key1":{"key2":"val"}}
                else:
                    # 获取到依赖数据层级列表
                    js_level_list = extract_key_js[key]
                    level_data_dict = {}
                    try:
                        # level_data_dict = res_data[key]
                        # level_data_dict = isinstance(res_data[key],list) == True?res_data[key][0]:res_data[key]
                        if isinstance(res_data[key], list) == True:
                            level_data_dict = res_data[key][0]
                        elif isinstance(res_data[key], dict):
                            level_data_dict = res_data[key]
                        else:
                            warning(type(res_data[key]))

                    except Exception as e:
                        warning(e)
                        warning(res_data)
                        warning("接口返回值中没有发现key： " + key)
                        # error(res_data)
                        # raise e

                    # 获取到依赖数据的最后一层的key
                    last_level_key = js_level_list[len(js_level_list) - 1]

                    for key in js_level_list:
                        if key != last_level_key:

                            # {"key":[A,B,C]}
                            # 当value的值是一个"[A，B，C]"列表时获取列表的第一个元素
                            # if isinstance(level_data_dict,list):
                            #     level_data_dict=level_data_dict[0]
                            if isinstance(level_data_dict[key], list):
                                if "_desc" in key:
                                    key = key[0:key.find("_desc")]
                                    level_data_dict = level_data_dict[key][len(level_data_dict[key]) - 1]
                                level_data_dict = level_data_dict[key][0]
                            else:
                                level_data_dict = level_data_dict[key]

                        else:
                            temp_key = last_level_key + "_ex"
                            if last_level_key not in self.res.text:
                                # 目标key加了自定义名称，拿到原始的key
                                res_key = last_level_key[0:str(last_level_key).rfind("_")]
                            else:
                                # 目标key没有自定义名称
                                res_key = last_level_key

                            if isinstance(level_data_dict, list):

                                try:

                                    if "_desc" in last_level_key:
                                        self.cache[temp_key] = level_data_dict[len(level_data_dict) - 1][last_level_key]
                                    # if ("_asc" in last_level_key) or  (index == -1):
                                    self.cache[temp_key] = level_data_dict[0][last_level_key]
                                except IndexError as e:
                                    error(e)
                                    error(self.res.text)
                                    error("返回值为空，检查测试数据")
                                    # raise e
                                except Exception as e:
                                    error(e)
                                    # raise e

                            else:
                                try:
                                    self.cache[temp_key] = level_data_dict[res_key]
                                except Exception as e:
                                    error(e)
                                    error("检查表中的key:  " + res_key)
                                    error("数据提取失败")
                                    # self.write_result_to_simple_report()

    def get_sk(self):
        jdata = json.dumps(self.data_login)

        # url = self.get_last_url("put", url=self.url_login, jdata=jdata, token=self.token)
        res = self.send.send_msg(method="put", url=self.url_login, header=self.header, data=jdata)
        # info(json.loads(res.text)["securityKey"])
        return json.loads(res.text)["securityKey"]

    # 部分Url重的qyery参数需要进行urlencode处理
    def get_urlencode_value(self, value):
        return urllib.parse.quote(value, safe='/', encoding=None, errors=None)

    def split_str_depended_key(self, dedepended_key):
        return dedepended_key.split(",")

    def get_depended_key(self):
        if self.get_exist_depended():
            self.depended_key_list = self.split_str_depended_key(self.depended_key)

    def get_exist_depended(self):
        self.depended_key = self.row_data[scn["depended_key"]]
        return True if self.row_data[scn["depended_key"]] != "" else False

    def get_sleep_time(self):
        if self.row_data[scn["sleep_time"]] != "":
            try:
                self.sleep_time = int(self.row_data[scn["sleep_time"]])
            except ValueError as e:
                error(e)
                error("读取值无法进行类型转换")
            except Exception as e:
                error(e)
        else:
            self.sleep_time = self.sleep_time_dafault

    def get_status_code(self):
        if self.row_data[scn["status_code"]] != "":
            self.status_code = int(self.row_data[scn["status_code"]])

    def get_env(self, env_config):
        # return "dev_result" if "dev" in env_config.lower() else "result"
        return "result"

    def get_row_data(self, line):
        return self.e_opt.get_cell_value(self.row, scn[line])

    def get_url_data(self):
        return self.row_data[scn["URL_head"]] + self.row_data[scn["ip"]] + self.row_data[scn["path"]]

    def get_last_url(self, method, url, jdata, token):
        try:
            obj = Get_signature_url(method=str.upper(method), req_url=url, req_data=jdata, token=token)
        except Exception as e:
            error(e)
            error("签名生成失败，检查URL信息是否填写正确")
            error(url)
        return obj.get_url()

    def get_last_new_signature_url(self, method, url, jdata, appSecret, appid, enterpriseid,version):



        obj = Get_signature_new_url(method=str.upper(method), req_url=url, req_data=jdata, appSecret=appSecret,
                                    appid=appid, enterpriseid=enterpriseid,sign_version=version,encryptionKey=self.encryptionKey,access_token=self.access_token,client_type=self.client_type)
        info("access_token")
        info(self.access_token)
        return obj.get_url()

    def get_url(self, jdata=""):
        #
        # body_key = str(self.row_data[scn["body"]])
        # jdata=json.dumps(self.json_data.get_data_by_key(body_key))

        original_url = self.get_url_data()

        # 参数优先级：配置文件 > 缓存 >  特殊字符
        for key in self.config:
            if key in original_url:
                value = str(self.config[key])
                # 判断当前参数是否需要进行urlencode处理,
                # 经过调试发现，python3好像会自动进行urlencode处理，不需要执行以下if语句也能执行成功
                # 但是还是加上吧，写都写了，万一哪天不行呢。。。。。。
                if "urlencode" in key:
                    value = value.replace("\'", '''\"''')
                    value = self.get_urlencode_value(value)

                original_url = original_url.replace(key, value)
            if self.get_exist_depended():
                # 替换path中的依赖数据
                for key in self.depended_key_list:
                    temp_key = key + "_ex"

                    if temp_key in self.cache:
                        path_key = "{" + key + "}"
                        original_url = original_url.replace(path_key, str(self.cache[temp_key]))

        # if '{securityKey}' in original_url:
        #     original_url = original_url.replace('{securityKey}',self.sk)
        original_url = self.replace_special_key_in_request_path(original_url)

        configDict = dict(self.json_data.get_data_by_key(self.env_config))

        if self.signType == 0:
            return original_url
        elif self.signType == 1:
            try:
                self.token = configDict["{token}"]
            except Exception:
                error("使用旧签名需要'token'参数")
            return self.get_last_url(self.method, url=original_url, jdata=jdata, token=self.token)
        elif self.signType == 2:
            try:
                self.appSecret = configDict["{appSecret}"]
                self.appid = configDict["{appId}"]
                self.enterpriseid = configDict["{enterpriseId}"]

                if self.signVersion == "2.0":
                    self.client_type = configDict["{clientType}"]

                if ("pre-sdkapi.xylink.com" not in original_url) and self.encryptionKey=="":
                    self.encryptionKey = self.config["{appId}"]

            except Exception:
                error("使用新签名配置文件中需要如下参数，'appSecret'，'appId'，'enterpriseId'")


            paramaters = self.get_last_new_signature_url(self.method, url=original_url, jdata=jdata,
                                                         appSecret=self.appSecret, appid=self.appid,
                                                         enterpriseid=self.enterpriseid,version=self.signVersion)
            # info(self.header)
            # info(type(self.header))
            # info(type(paramaters))
            self.header.update(paramaters)
            # info(self.header)
            # info(paramaters)
            return original_url

    def get_sign_type(self):

        configDict = dict(self.json_data.get_data_by_key(self.env_config))

        # info(configDict.keys())

        # 不走签名
        if (("{token}" not in configDict.keys()) or (configDict["{token}"] == "")) and (
                "{signature}" not in configDict.keys()):
            return 0
        if configDict["{signature}"] == "no":
            return 0

        # 走旧签名
        if ("{signature}" not in configDict.keys()) or configDict["{signature}"] != "new":
            try:
                self.token = configDict["{token}"]
            except Exception:
                error("使用旧签名需要'token'参数")
            return 1

        # 走新签名
        return 2

    def get_header(self):

        h = self.json_data.get_data_by_key(self.row_data[scn["header"]])

        for key in h:
            tempval = h[key][str(h[key]).find("{"):str(h[key]).rfind("}") + 1]

            if "{" in h[key] and h[key] in self.config:
                h[key] = str(h[key]).replace(tempval, self.config[tempval])
                # info(h[key])
                h[key] = self.config[tempval]
                # h[key]=self.config[h[key]]

            # temp_key = str(h[key]).lstrip("{").rstrip("}") + "_ex"
            temp_key = tempval.lstrip("{").rstrip("}") + "_ex"

            if temp_key in self.cache:
                h[key] = str(h[key]).replace(tempval, self.cache[temp_key])

        # if "Authorization" in h and "Bearer" not in h["Authorization"]:
        #     h["Authorization"] = "Bearer " + h["Authorization"]
        return self.json_data.get_data_by_key(self.row_data[scn["header"]])

    def get_body_ddt(self):
        body_key = str(self.row_data[scn["body"]])
        body = json.dumps(self.json_data.get_data_by_key(body_key))
        for key in self.config:
            if body_key in key:
                body = body.replace(key, str(self.config[key]))

    def get_body(self):
        body = ""
        body_key = str(self.row_data[scn["body"]])
        self.body_str = body

        # 对请求体中的数据进行参数化替换，参数变量来源：1.配置文件  2.缓存   3.特殊字符
        # 当参数名发生重合时，参数优先级：特殊字符  <  缓存  <  配置文件
        if body_key != "":

            # body = self.json_data.get_data_by_key(body_key)
            # json中读取原始请求体,用于后面参数化数据替换操作
            body = json.dumps(self.json_data.get_data_by_key(body_key))
            # 将请求体转化成dict，方便后续替换前的判断操作
            # body_dict = json.loads(body)
            # 获取body中的所有value
            # body_values = body_dict.values()

            # 替换配置文件中的参数化变量
            for key in self.config:
                if key in body:
                    body = body.replace(key, str(self.config[key]))

            # 替换缓存中的配置文件
            # for item in body_values:
            #     val = str(item).lstrip("{").rstrip("}")+"_ex"
            #     if val in self.cache:
            #         body = body.replace(item,str(self.cache[val]))

            for item in self.cache:
                val = str(item).lstrip("{").rstrip("}")[:-3]
                if val in body:
                    val = "{" + val + '}'
                    body = body.replace(str(val), str(self.cache[item]))

            # 对请求体中的特殊字段进行替换
            body = self.replace_special_key_in_request_body(body)

            if "_urlencoded" in body_key:
                body = json.loads(body)
                self.header["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
                return body

            if "_formdata" in body_key:
                body = json.loads(body)
                body = MultipartEncoder(body)
                self.header["Content-Type"] = body.content_type
                return body

            if "_file" in body_key:

                file_body = json.loads(body)
                file_key = file_body["file_key"]
                file_name = file_body["file_name"]
                file_path = os.path.dirname(os.path.realpath(__file__))
                file_path = file_path[:file_path.find("src") + 4] + file_name
                file_data = file_body["data"]
                info(file_data)
                try:
                    body = {
                        "^upload_file": {
                            file_key: (
                                os.path.basename(file_path), open(file_path, "rb"), "application/vnd.ms-excel")
                        },
                        "data": file_data
                    }
                except Exception as e:
                    error(e)
                return body

        return body

    # 特殊默认字段的处理，可扩展
    def replace_special_key_in_request_body(self, body):
        if "{startTime}" in body:
            body = body.replace("{startTime}", str(int(time.time() + 120) * 1000))
        if "{endTime}" in body:
            body = body.replace("{endTime}", str((int(time.time()) + 1200) * 1000))
        return body

    # 特殊默认字段的处理，可扩展
    def replace_special_key_in_request_path(self, path):

        if "{startTime}" in path:
            path = path.replace("{startTime}", str(int(time.time() + 120) * 1000))
        if "{endTime}" in path:
            path = path.replace("{endTime}", str((int(time.time()) + 1200) * 1000))
        if '{securityKey}' in path:
            path = path.replace('{securityKey}', self.sk)

        return path

    def get_is_exec(self):

        try:
            is_execute_data = int(self.row_data[scn["is_execute"]])
        except ValueError as e:
            error(e)
            print(e)
            error("读取值无法进行类型转换")
            return 0
        except Exception as e:
            error(e)
            error("数据填写有误")
            print(e)
            return 0
        else:
            return is_execute_data

    def get_run_result(self):

        res_msg = ""
        if (self.res.status_code in {200, 204,
                                     201} and self.status_code == 0) or self.res.status_code == self.status_code:
            if self.is_execute == 2:
                res_msg = DEPENDED_API
            if self.is_execute == 1:
                res_msg = SUCCESS
            if self.is_execute == 3:
                res_msg = EXCEPTION_TEST
            if self.answer != " ":
                if self.answer not in self.res.text:
                    res_msg = FAIL
        else:
            res_msg = FAIL

        return res_msg

    def re_write_result(self, row, exc=1):
        if exc == -1:
            res_msg = NO_EXEC
        else:
            res_msg = self.get_run_result()
        self.e_opt.write_to_excel(row, line=scn[self.env], res=res_msg)
        self.e_opt.data_save()

    def sleep(self):
        self.get_sleep_time()
        time.sleep(self.sleep_time)

    def get_data_config(self, config_name):
        return self.json_data.get_data_by_key(config_name)

    # 期望值参数化
    def get_ex_answer(self):
        answer = str(self.row_data[scn["ex_answer"]])
        if "{" in answer:
            for key in self.config:
                if key in answer:
                    answer = answer.replace(key, self.config[key])
        return answer

    # 生成简易报告，汇总每个模块的运行情况
    def write_result_to_simple_report(self):

        Count.sheet_nums_count += 1

        Count.success_count_all += self.e_opt.success
        Count.fail_count_all += self.e_opt.fail
        Count.no_exec_count_all += self.e_opt.noexec

        Count.temp_success_count += self.e_opt.success
        Count.temp_fail_count += self.e_opt.fail
        Count.temp_noexec_count += self.e_opt.noexec

        if Count.sheet_nums_count >= Count.sheet_nums:
            m = {"sheetname": self.sheet_name, "success": Count.temp_success_count, "fail": Count.temp_fail_count,
                 "noexec": Count.temp_noexec_count}
            Count.module_count.append(m)
            # 参数初始化
            Count.temp_success_count = 0
            Count.temp_fail_count = 0
            Count.temp_noexec_count = 0
            Count.sheet_nums_count = 0

    def assert_result(self, body):
        try:
            info(self.res.status_code)
            info("requestBody: " + str(body))
            if self.status_code == 0:
                assert (self.res.status_code in [200, 204]), "status_code excepotion"
            else:
                assert (self.res.status_code == self.status_code), "status_code excepotion"

            if len(self.answer) > 0:
                assert (self.answer in self.res.text), self.answer + " not in " + self.res.text

            if self.res.text != "":
                info("responseBody: " + self.res.text)

            info(self.row_data[scn["name"]] + ":   " + "运行成功")
            self.get_extract_key()
        except Exception as e:
            print(e)
            error(e)

            try:
                error(str(self.res.status_code))
                error(body)
                error(self.answer + " not in " + self.res.text)
            except Exception as e:
                error(e)

            error(self.row_data[scn["name"]] + ":   " + "运行失败")

    def exception_case_body_recursion(self, body, leaf, body_key_list):

        leaf += 1
        for item in body.keys():

            # 记录key和所在的层级
            templist = []

            templist.append(item)
            templist.append(leaf)

            body_key_list.append(templist)

            if isinstance(body[item], dict):
                self.exception_case_body_recursion(body[item], leaf, body_key_list)
            elif isinstance(body[item], list):
                for l in body[item]:
                    if isinstance(l, dict):
                        self.exception_case_body_recursion(l, leaf, body_key_list)

    def get_body_key_list(self, body):
        body_key_list = []
        self.exception_case_body_recursion(body, 0, body_key_list)
        return body_key_list

    def get_match_brackets(self, count, word, match_word):
        i = 1
        index = word.find(match_word)
        while i < count:
            index = word.find(match_word, index + 1)
            i += 1
        # info(match_word + "出现          :" + count)
        return index

    def exception_case_test(self, body):
        if body == '':
            return

        if isinstance(body, str):
            body = json.loads(body)

        if isinstance(body, list):
            if isinstance(body[0], str):
                body_copy = body.copy()
                body_copy[0] = ""
                body_copy = str(body_copy).replace("\'", "\"")
                self.exception_assert_result(str(body_copy))

                body_copy = body.copy()
                body_copy[0] = ""
                body_copy = str(body_copy).replace("\'\'", "null")
                self.exception_assert_result(str(body_copy))

                body_copy = body.copy()
                body_copy.clear()
                self.exception_assert_result(str(body_copy))

                return
            body = body[0]

        key_list = self.get_body_key_list(body)
        info(key_list)

        # 添加 end 辅助节点
        key_list.append(["%^end", -1])

        info(key_list)
        str_body = json.dumps(body)

        start_ini = 0
        # 遍历key，找到当前可被替换的字符范围地址
        for i in range(0, len(key_list)):
            for j in range(i + 1, len(key_list)):
                # 当找到一个节点的层级小于等于当前节点时停止，找到可变范围字符串的结束关键字
                if key_list[j][1] <= key_list[i][1]:

                    start_word_index = str_body[start_ini:].find(key_list[i][0]) + len(key_list[i][0]) + 2 + start_ini
                    start_ini = start_word_index
                    end_word_index = str_body[start_word_index:].find(key_list[j][0]) + start_word_index - 1

                    if key_list[j][1] != -1:
                        replace_word = str_body[start_word_index:end_word_index].strip()

                    else:
                        replace_word = str_body[start_word_index:].strip()

                    s = []
                    id = 0
                    for r in reversed(replace_word):
                        item = []
                        item.append(r)
                        item.append(id)
                        if r in {"}", "]"}:
                            s.append(item)

                        elif r == "{":
                            if len(s) != 0 and s[-1][0] == "}":
                                s.pop()
                            else:
                                s.append(item)
                        elif r == "[":
                            if len(s) != 0 and s[-1][0] == "]":
                                s.pop()
                            else:
                                s.append(item)
                        id -= 1

                    if len(s) > 0:
                        replace_word = replace_word[:s.pop()[1] - 1]

                    pre = str_body[:start_word_index]
                    post = str_body[start_word_index + len(replace_word) + 1:]

                    rpost = post
                    if replace_word[-1] == ",":
                        rpost = "," + post

                    exception_body = pre + "null" + rpost
                    self.exception_assert_result(exception_body.replace("\'", "\""))

                    exception_body = pre + "\"\"" + rpost
                    self.exception_assert_result(exception_body.replace("\'", "\""))

                    pre = pre[:len(pre) - len(key_list[i][0]) - 3]
                    if post.strip()[0] in {"]", "}"} and pre.strip()[-1] == ",":
                        pre = pre.rstrip().rstrip(",")

                    exception_body = pre + post
                    self.exception_assert_result(exception_body.replace("\'", "\""))

                break

    def exception_assert_result(self, body):

        info("-" * 60)
        url = self.get_url(str(body))

        res = ""
        try:
            # info(body)
            res = self.send.send_msg(method=self.method, url=url, header=self.header, data=body)
        except Exception as e:
            error(e)
            error("Failed to connect server")
        try:
            assert (res.status_code in [200, 400]), "status_code excepotion"
            info(res.status_code)
            info(url)
            info("requestbody：" + str(body))
            info(res.text)
        except Exception as ee:
            error("异常场景出错")
            error(res.status_code)
            error(url)
            error(body)
            error(res.text)
            self.fw.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
            self.fw.write(str(res.status_code) + "\n")
            self.fw.write(str(url) + "\n")
            self.fw.write(str(body) + "\n")
            self.fw.write(str(res.text) + "\n")

    def execute(self):

        for line in range(1, self.e_opt.sheet_rows):

            # info(self.cache)

            # 获取表格的行数据
            self.row_data = list(map(self.get_row_data, self.name_list))
            self.method = str(self.row_data[scn["method"]]).strip()

            # 是否执行当前接口
            self.is_execute = self.get_is_exec()

            # if is_execute is False:
            if self.is_execute not in [1, 2, 3]:
                self.re_write_result(line, exc=-1)
                self.row += 1
                continue

            # 请求头
            self.header = self.get_header()

            # 获取depentded_key
            self.get_depended_key()

            body = self.get_body()
            # info(type(body))

            if "signSecret_ex" in self.cache.keys() and "access_token_ex" in self.cache.keys():
                self.encryptionKey = self.cache["signSecret_ex"]
                self.access_token = self.cache["access_token_ex"]

            # 拼接url
            url = self.get_url(body)
            info(url)
            # info("requestBody: " + self.body_str)
            try:
                self.res = self.send.send_msg(method=self.method, url=url, header=self.header, data=body)
                info(self.res.headers)
            except Exception as e:
                error(e)
                error("Failed to connect server")

            # 获取期望结果
            # self.answer = str(self.row_data[scn["ex_answer"]])
            self.answer = self.get_ex_answer().strip()

            # info("缓存数据：" + str(self.cache))
            self.get_status_code()

            self.assert_result(body)

            # self.get_extract_key()

            # 回写结果到excel
            self.re_write_result(line)

            self.status_code = 0

            # 表格行数加1
            self.row += 1

            if self.exception == True and body != "":
                self.fw = open("../report/log.txt", "a+")
                self.exception_case_test(body)
                self.fw.close()

            info("header: " + str(self.header))
            info("cache: " + str(self.cache))

            # 打印运行结果
            # self.print_result()
            info("-" * 60)

            # 睡眠
            self.sleep()

        if self.signType == 2:
            jvm.stopJVM()
