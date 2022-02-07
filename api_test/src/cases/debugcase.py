
# -*- coding:utf-8 -*-
import functools
import time
import unittest

from src.base import HTMLTestRunner_back, HTMLTestRunner
from src.public.data_path import *




class TestMethodPre(unittest.TestCase):

    @excelpath("/AAAdebug/debug.xlsx")
    def test_debug(self):
        execute("Q4", "Q4.json", "config_prd")



if __name__ == '__main__':
    fp = open('../report/html_report.html', 'wb')

    suite = unittest.TestSuite()
    suite.addTest(TestMethodPre('test_debug'))





    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title="API Report")
    runner.run(suite)










