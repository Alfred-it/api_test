
# -*- coding:utf-8 -*-
import time
import unittest

import ddt as ddt

from src.base import HTMLTestRunner
from src.public.data_path import execute, excelpath

from src import *


class TestMethodPre(unittest.TestCase):

    p="/Users/zhouyu/Desktop/webUI/web_ui_test/web_auto_test/UI_Auto_Test/data/data.yml";

    @excelpath("/me60/AndroidSDKcall.xls")
    def test_call(self):
        execute("call", "")

    @excelpath("/me60/call.xls")
    def test_call2(self):
        execute("call", self.p)





if __name__ == '__main__':
    # unittest.main()

    fp = open('../report/html_report.html', 'wb')
    suite = unittest.TestSuite()

    # suite.addTest(TestMethodPre('test_call'))
    suite.addTest(TestMethodPre('test_call2'))



    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title="UI Auto Report")
    runner.run(suite)











