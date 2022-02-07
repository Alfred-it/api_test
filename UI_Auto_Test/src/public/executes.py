import time

from selenium import webdriver

from src.public.element import Element
from src.public.handle import Handle
from src.utils.ddt_util import ddt, DDT
from src.utils.excel_opt import ExcelOperation
from src.public.common import SheetColumnName as scn, SUCCESS, FAIL, NO_EXEC, Count, BrowserType
from src.utils.files_opt import FileOperation
from src.utils.json_opt import JsonOperation
from src.utils.log_opt import info, error,warning
from src.utils.time_wait_opt import maxtry
import logging.config
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO)

from src.public.index import INDEX, name_dict
from src.config import *
from src.cache import *


class Execute:

    name_list = ["name","browser", "by", "element", "operation", "data","check_by","check_element", "res"]
    row=1

    indexValid=False
    screenShot=False
    cacheValid=False

    picture_path="null"
    ddt_data={}



    def __init__(self, data_file_path, sheet_name,ddt_file):
        info("server is connecting ... ...")

        self.sheet_name = sheet_name
        self.e_opt = ExcelOperation(data_file_path, sheet_name)
        self.json_opt=JsonOperation(configPath)
        # self.config = self.json_opt.get_data_by_key("config")
        self.ddt_file=ddt_file
        self.get_config()
        self.print_config_info()
        DDT.ddt_file=ddt_file

        self.browser=self.json_opt.get_data_by_key("config")
        self.bt=BrowserType.val
        info(self.bt)

    def get_config(self):

        try:
            self.indexValid = self.json_opt.get_data_by_key("indexValid")
        except Exception:
            self.indexValid=False
            info("indexValid value  failed  found from config")

        try:
            self.screenShot = self.json_opt.get_data_by_key("screenShot")
        except Exception:
            self.screenShot=False
            info("screenShot value  failed  found from config")

        try:
            self.cacheValid = self.json_opt.get_data_by_key("cacheValid")
        except Exception:
            self.cacheValid=False
            info("cacheValid value  failed  found from config")




    def print_config_info(self):
        if self.screenShot:
            self.picture_path=self.json_opt.get_data_by_key("picturePath")
        else:
            info("screenShot value is default: False")

        if self.indexValid:
            info("indexValid value is open: True")
        else:
            info("indexValid value is default: False")

        if self.cacheValid:
            self.fileOpt=FileOperation()
            self.cache = self.fileOpt.read(cachePath + self.sheet_name + ".cah")
            info("cacheValid value is open: True")
        else:
            info("cacheValid value is default: False")



    def get_row_data(self, line):
        return self.e_opt.get_cell_value(self.row, scn[line])

    # 生成简易报告，汇总每个模块的运行情况
    def write_result_to_simple_report(self):

        Count.sheet_nums_count += 1

        Count.success_count_all += self.e_opt.success
        Count.fail_count_all += self.e_opt.fail
        Count.no_exec_count_all += self.e_opt.noexec

        # info(Count.sheet_nums)
        # info(Count.sheet_nums_count)

        info(Count.success_count_all)
        info(Count.fail_count_all)

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



    @maxtry(6)
    def run_each(self):

        try:
            m = self.e.get_element(self.row_data[scn["by"]], self.row_data[scn["element"]])
            if DDT.data_record:
                info(DDT.data_record)
                self.data=DDT.data_record[str(self.row_data[scn["data"]]).lstrip("{").rstrip("}")]
                # self.h.elment_operation(obj=m, opt=self.row_data[scn["operation"]], data=DDT.data_record[str(self.row_data[scn["data"]]).lstrip("{").rstrip("}")])
            else:
                self.data = self.row_data[scn["data"]]
            self.h.elment_operation(obj=m, opt=self.row_data[scn["operation"]], data=self.data)
        except Exception as err:
            warning(self.row_data[scn["element"]]+ " is not found")
            warning(err)
            self.get_from_index()
            return False
        return True

    def get_run_result(self,res):

        # info(self.res.status_code)
        # info(self.status_code)
        res_msg = FAIL
        if res==True:
            res_msg = SUCCESS
            info(self.row_data[scn["name"]] + " is successful")
        else:
            error(self.row_data[scn["name"]] + " is failed")


        return res_msg

    def re_write_result(self, row,res, exc=1):
        if exc == -1:
            res_msg = NO_EXEC
        else:
            res_msg = self.get_run_result(res)
        self.e_opt.write_to_excel(row,line=scn["res"], res=res_msg)
        self.e_opt.data_save()

    def check_element(self):

        elcheck = self.e.get_element(self.row_data[scn["check_by"]], self.row_data[scn["check_element"]])
        return False if elcheck == "null" else True

    def is_check(self,res):
        if (self.row_data[scn["check_by"]]) != "":
            el_check = self.check_element()
            if el_check == True and res == True:
                res = True
            else:
                res = False
        return res

    def get_from_cache(self):
        if self.row_data[scn["element"]] in self.cache.keys():

            # 元素计数器加1
            self.cache[self.row_data[scn["element"]]]["num"]+=1
            replace_by=self.cache[self.row_data[scn["element"]]]['replace_by']
            replace_el=self.cache[self.row_data[scn["element"]]]['replace_element']
            self.row_data[scn['by']] = replace_by
            self.row_data[scn["element"]] = replace_el

            return True
        return False

    def get_from_index(self):
        if self.indexValid:
            if self.cacheValid:
                isFoundFromCache=self.get_from_cache()
                if isFoundFromCache:
                    return True

            if self.row_data[scn["element"]] in INDEX.index.keys():

                repalce_by=INDEX.index[self.row_data[scn["element"]]][name_dict['replace_by']]
                repalce_el=INDEX.index[self.row_data[scn["element"]]][name_dict['replace_element']]

                # 如果开启缓存机制，将索引中找到的数据拷贝到缓存
                if self.cacheValid:
                    cacheElDict={
                        "element":self.row_data[scn["element"]],
                        "by":self.row_data[scn['by']],
                        "replace_element":repalce_el,
                        "replace_by":repalce_by,
                        "num":1
                    }
                    self.cache[self.row_data[scn["element"]]]=cacheElDict
                    self.cache["change"]=True

                # 缓存更新后在进行元素的替换
                self.row_data[scn['by']] = repalce_by
                self.row_data[scn["element"]] = repalce_el

                return True
            else:
                return False


    def update_cache(self):

        # 缓存中的数据发生变更时更新本地缓存文件
        if self.cache["change"]:
            for key in self.cache.keys():
                # 删除缓存中引用为0的元素
                if key != "change":
                    if self.cache[key]["num"]==0:
                        del(self.cache[key])
            self.fileOpt.write(self.cache,cachePath+self.sheet_name+".cah")

    @ddt
    def execute(self):
        # for b in self.browser:

        self.row =1

        for line in range(1, self.e_opt.sheet_rows):
            self.row_data = list(map(self.get_row_data, self.name_list))

            if self.row == 1:
                # browser = self.row_data[scn["browser"]]
                index = self.row_data[scn["data"]]
                if str(self.bt).lower()=="chrome":
                    self.webdriver=webdriver.Chrome()
                elif str(self.bt).lower()=="edge":
                    self.webdriver=webdriver.Edge()

                self.webdriver.get(index)

                self.e = Element(self.webdriver, self.picture_path)
                self.h = Handle(self.webdriver,self.picture_path)

                self.row+=1

                continue

            res = self.run_each()
            checkres=self.is_check(res)

            self.re_write_result(line,checkres)

            self.row += 1

        if self.row == self.e_opt.sheet_rows:

            if self.cacheValid:
                self.update_cache()
            self.write_result_to_simple_report()




