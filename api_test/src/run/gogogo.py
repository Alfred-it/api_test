import datetime
import shutil
import unittest

from src.base import HTMLTestRunner_back
from src.public.sendmail import sendmail

case_path = "../cases"

if __name__ == '__main__':


    discover = unittest.defaultTestLoader.discover(case_path, pattern="case_j*", top_level_dir=None)

    fp = open('../report/html_report.html', 'wb')


    runner = HTMLTestRunner_back.HTMLTestRunner(stream=fp, title="API自动化测试报告")
    runner.run(discover)

    f = open("../report/html_report.html", "rb")
    msg = f.read()
    f.close()

    time = datetime.datetime.now().strftime('%m%d%H')
    result_html = "../report/html_report-" + datetime.datetime.now().strftime('%m%d%H') + ".html"
    shutil.copyfile("../report/html_report.html", result_html)
    sendmail(msg, [result_html])
