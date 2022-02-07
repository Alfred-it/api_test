
# -*- coding:utf-8 -*-
import multiprocessing
import time
import unittest
from logging import Manager
from multiprocessing import Process
from multiprocessing import Pool

import ddt as ddt

from src.base import HTMLTestRunner
from src.public.common import BrowserType
from src.public.data_path import execute, excelpath

from src import *
from src.utils import json_opt
from src.utils.json_opt import JsonOperation
from src.utils.log_opt import info


class TestMethodPre(unittest.TestCase):

    p="/Users/zhouyu/Desktop/webUI/web_ui_test/web_auto_test/UI_Auto_Test/data/data.yml";

    @excelpath("/me60/AndroidSDKcall.xls")
    def test_call(self):
        execute("call", "")

    @excelpath("/me60/call.xls")
    def test_call2(self):
        execute("call", self.p)



def t():
    BrowserType.val=BrowserType.q.get()
    # 转换为localtime
    time_local = time.localtime(time.time())
    # 转换为新的时间格式
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    fp = open('../report/'+BrowserType.val+'_'+str(dt)+'.html', 'wb')
    suite = unittest.TestSuite()

    # suite.addTest(TestMethodPre('test_call'))
    suite.addTest(TestMethodPre('test_call2'))



    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title="UI Auto Report")
    runner.run(suite)


if __name__ == '__main__':
    # unittest.main()


    json_opt=JsonOperation("../config/config.json")
    bt=json_opt.get_data_by_key("config")
    for b in bt:
        BrowserType.q.put(b)

    pool = Pool(5)
    for b in bt:
        pool.apply_async(func=t)

    pool.close()
    pool.join()











