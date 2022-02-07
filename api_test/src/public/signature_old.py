# -*- coding: UTF-8 -*-
import sys

sys.path.append('../')

import requests
from urllib.parse import urlparse
import re
import hashlib
import base64
import urllib
import hmac
import json


class Get_signature_url(object):
    def __init__(self, method, req_url, req_data, token):
        if req_data == None:
            req_data = ""
        self.method = method
        self.req_url = req_url
        self.req_data = req_data
        self.token = token

    def parse_url(self):
        pass
        # 数据脱敏
        # ******
        # ******
        # ******
        # 数据脱敏



    def hash_body(self):
        pass
        # 数据脱敏
        # ******
        # ******
        # ******
        # 数据脱敏


    def get_list(self):
       pass

    def get_signature(self):
        llist = self.get_list()
        Hmac_sha256 = hmac.new(bytes(self.token, 'utf-8'), bytes(llist, 'utf-8'), digestmod=hashlib.sha256).digest()
        signature = urllib.parse.quote_plus(base64.b64encode(bytes(Hmac_sha256)))
        return signature

    def get_url(self):
        signature = self.get_signature()
        last_url = self.url + '&signature=' + signature
        return last_url
