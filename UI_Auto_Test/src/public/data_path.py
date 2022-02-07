# 相关数据路径
import functools
import gc
import os

import xlwt

from src.public.executes import Execute, Count
from src.utils.excel_opt import ExcelOperation
from src.utils.log_opt import info





class PathInfo:
    root_dir = os.path.dirname(os.path.abspath('..'))
    data_path = root_dir + '/data/'  # 根据项目所在路径，找到用例所在的相对项目的路径
    # json_path_list=[]
    data_name_list=[]
    sheet_name_list=[]



    def __init__(self):
        self.excel_path = self.data_path
        self.json_path = self.data_path
        self.sheet_name = "sheet_name"
        self.config_name="config_name"




def info_print(sheet_name, msg):
    info("*"*60)
    info("               "+sheet_name+":  " + msg + "        ")
    info("*"*60)

def execute(sheet_name,datafile):

    Count.ui_cases_count+=1
    Count.sheet_nums+=1
    path_info.sheet_name_list.append(str(sheet_name))
    path_info.data_name_list.append(str(datafile))



def runa(sheet_name,config_name):

    # e_list=[]
    # 这里有个问题，当Execute中的cache不在构造函数中初始化{}时，后面一个实例对象的cache引用的是同一快内存地址，为啥呢，原因不明
    #  ？？？？？？？？？？？？？？？
    info_print(sheet_name, "开始运行")
    e=Execute(path_info.excel_path, sheet_name,config_name)
    e.execute()
    # e_list.append(e)
    info_print(sheet_name, "运行结束")




# 语法糖，用于处理文件之间的路径关系
def excelpath(excelpath):
    def decorator(func):
        def wrapper(*args, **kw):
            global path_info
            path_info= PathInfo()

            excel_path=excelpath.strip("/")
            path_list=excel_path.split("/")
            path_info.data_path = path_info.data_path+path_list[0]
            # path_info.json_path = path_info.json_path+path_list[0]+"/"
            path_info.excel_path = path_info.excel_path+excel_path

            func(*args, **kw)


            list(map(runa,path_info.sheet_name_list,path_info.data_name_list))

            # 初始化参数列表
            path_info.sheet_name_list.clear()
            # path_info.json_path_list.clear()
            path_info.data_name_list.clear()

            Count.sheet_nums=0


        return wrapper

    return decorator
