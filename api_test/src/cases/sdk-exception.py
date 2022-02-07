# -*- coding:utf-8 -*-
import time
import unittest

from src.base import HTMLTestRunner_back
from src.public.data_path import *



class TestMethodPre(unittest.TestCase):

      @excelpath("/sdkException/sdk.xls")

      def test_sdk(self):

          execute("additional", "sdk2.json", "config_pre")


      @excelpath("/dcs/dcs_jingjunwei.xls")
      def test_test(self):

          execute("dcs", "dcs_jingjunwei.json", "config_prd_jingjunwei")



      @excelpath("/dating/dating_prd.xls")
      def test_dating(self):

          execute("dating", "dating_prd.json", "config_prd_dating")


if __name__ == '__main__':
    fp = open('../report/html_report.html', 'wb')

    suite = unittest.TestSuite()

    # suite.addTest(TestMethodPre('test_dating'))
    suite.addTest(TestMethodPre('test_sdk'))

    runner = HTMLTestRunner_back.HTMLTestRunner(stream=fp, title="API Report")
    runner.run(suite)











