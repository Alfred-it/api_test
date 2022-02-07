# -*- coding: utf-8 -*-
import requests
import ssl

from src.utils.log_opt import debug, info

ssl._create_default_https_context = ssl._create_unverified_context


class SendMsg:

    def send_msg(self, method=None, url=None, header=None, data=None):

        if isinstance(data, str):
            data = data.encode("utf-8")

        method = method.lower()

        if method == "put":
            return requests.put(url=url, data=data, verify=False, headers=header)
        elif method == "get":
            return requests.get(url=url, data=data, verify=False, headers=header)
        elif method == "post":
            if isinstance(data, dict) and "^upload_file" in data:
                info(data["data"])
                info(url)
                info(header)
                info(data["^upload_file"])
                return requests.post(url=url, data=data["data"], files=data["^upload_file"], verify=False,
                                     headers=header)
            return requests.post(url=url, data=data, verify=False, headers=header)
        elif method == "delete":
            return requests.delete(url=url, data=data, verify=False, headers=header)
