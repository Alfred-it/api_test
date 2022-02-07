from enum import Enum

# 列的名称
# l = {"name": 1}

SheetColumnName = {
    "name": 0, "is_execute": 1, "method": 2, "header": 3, "URL_head": 4,
    "ip": 5, "path": 6, "extract_key": 7, "depended_key": 8, "body": 9, "status_code": 10, "ex_answer": 11,
    "sleep_time": 12, "result": 13
}


# 信息返回体
class ResponseData:
    state_code = -1
    msg = "None"

    def __init__(self, state_code, msg):
        self.state_code = state_code
        self.msg = msg

    def get_code(self):
        return self.state_code

    def get_msg(self):
        return self.msg

    def set_msg(self, msg):
        self.msg = msg

    def set_code(self, state_code):
        self.state_code = state_code


# 常用返回体定义
SUCCESS = ResponseData(0, "pass")
FAIL = ResponseData(1, "fail")
NO_EXEC = ResponseData(-1, " ")

SUCCESS_COUNT = ResponseData(0, "msg")
FAIL_COUNT = ResponseData(1, "msg")
NO_EXEC_COUNT = ResponseData(-1, "msg")

ALL_SUCCESS_COUNT = ResponseData(2, "msg")
ALL_FAIL_COUNT = ResponseData(2, "msg")
ALL_NO_EXEC_COUNT = ResponseData(2, "msg")

EXCEPTION_TEST = ResponseData(3, "exception test")

DEPENDED_API = ResponseData(4, "denpended api")


class Count:
    fail_count = 0
    success_count = 0
    no_exec_count = 0

    simple_report_rows = 2
    sheet_nums = 0
    sheet_nums_count = 0

    temp_success_count = 0
    temp_fail_count = 0
    temp_noexec_count = 0

    fail_count_all = 0
    success_count_all = 0
    no_exec_count_all = 0

    table_all = 0

    module_count = []
