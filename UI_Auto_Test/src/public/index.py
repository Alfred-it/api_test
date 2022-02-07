import os

from src.utils.excel_opt import ExcelOperation
from src.utils.json_opt import JsonOperation
from src.config import *
from src.utils.log_opt import info

name_dict = {"element": 0, "by": 1, "replace_element": 2, "replace_by": 3}

class Index:
    index={}
    row=1
    indexValid=False
    name_list = ["element", "by","replace_element","replace_by"]

    def __init__(self):
        self.json_opt=JsonOperation(configPath)
        self.index_path=self.json_opt.get_data_by_key("indexPath")
        self.table_index=ExcelOperation(self.index_path,"index")
        self.get_config()
        if self.indexValid:
            self.execute()
        else:
            info("INDEX is default invalid")

    def get_config(self):
        try:
            self.indexValid=self.json_opt.get_data_by_key("indexValid")
        except Exception:
            info("indexValid failed foud from config")

    def get_row_data(self, line):
        return self.table_index.get_cell_value(self.row, name_dict[line])

    def execute(self):
        for line in range(1, self.table_index.sheet_rows):
            self.row_data = list(map(self.get_row_data, self.name_list))
            self.index[self.row_data[name_dict["element"]]]=self.row_data
        self.row+=1


INDEX = Index()
# print(INDEX.index)




