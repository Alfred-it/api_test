#coding:utf-8
import xlrd
import xlwt
from xlwt import *
from xlutils.copy import copy

from src.utils.log_opt import error


class ExcelOperation:

    sheet_name = ""
    sheet_rows = 0
    # excel_file_path = "/Users/zhouyu/Auto-test/Auto-API/data/meeting_data.xlsx"

    fail=0
    success=0
    noexec=0


    def __init__(self, filepath, sheet_name):
        # self.tables = self.get_excel_tables(filepath)
        self.sheet_name = sheet_name
        self.excel_file_path = filepath
        self.sheet_r_data = self.get_data_by_sheet_name()
        self.sheet_w_data = copy(xlrd.open_workbook(self.excel_file_path, formatting_info=True))
        self.sheet_rows = self.get_rows()



    # 获取表格数据
    def get_data_by_sheet_name(self):
        try:
            excel_data = xlrd.open_workbook(self.excel_file_path)
            sheet_data = excel_data.sheet_by_name(self.sheet_name)

        except FileNotFoundError as e:
            error("excel文件打开失败，检查excel是否存在")
            error(e)
            raise e
        except xlrd.biffh.XLRDError as e:
            error("sheet打开失败，检查表单是否存在")
            error(e)
            raise e
        except Exception as e:
            error(e)
        else:
            return sheet_data



    # 获取表格的行数
    def get_rows(self):
        return self.sheet_r_data.nrows

    # 获取单元格数据
    def get_cell_value(self, row, llist):
        return self.sheet_r_data.cell_value(row, llist)

    # 回写结果到excel表格
    def write_to_excel(self, row,line,res):
        style = XFStyle()

        if res.state_code == 0:
            self.success+=1
            style = xlwt.easyxf('pattern: pattern solid, fore_colour light_green')
        elif res.state_code == 1:
            style = xlwt.easyxf('pattern: pattern solid, fore_colour rose')
            self.fail+=1
        elif res.state_code == -1:
            style = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow')
            self.noexec+=1
        elif res.state_code == 2:
            style = xlwt.easyxf('pattern: pattern solid, fore_colour pale_blue')
            self.noexec += 1
        elif res.state_code == 4:
            style = xlwt.easyxf('pattern: pattern solid, fore_colour light_green')
        elif res.state_code == 3:
            style = xlwt.easyxf('pattern: pattern solid, fore_colour pale_blue')
            self.success+=1



        borders = xlwt.Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1
        style.borders = borders

        write_data = self.sheet_w_data.get_sheet(self.sheet_name)
        write_data.write(row, line, res.msg, style)

    # 数据保存，调用完写数据的函数后，需要调用保存数据的函数，数据才能写入成功
    def data_save(self):
        self.sheet_w_data.save(self.excel_file_path)


# e = ExcelOperation()
# e.creat_sheet()




