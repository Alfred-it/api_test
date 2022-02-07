import json

from src.utils.log_opt import info, error


class JsonOperation:
    file_name = " "
    data = " "

    def __init__(self, file_path):

        try:
            self.data = self.get_json_data(file_path)
        except Exception as e:
            error(e)
            error("json文件打开失败")
            print(e)


    # 获读取json文件
    def get_json_data(self, file_path=None):
        with open(file_path, 'r', encoding='UTF-8') as fp:
            try:
                edata = json.load(fp)
            except Exception as e:
                info("json文件解析出错，检查json文件格式")
                print("json文件解析出错，检查json文件格式")
                raise e
        return edata




    # 获取目标数据
    def get_data_by_key(self, key):
        if "_list" not in key:
            try:
                r = self.data[key]
            except Exception as e:
                error(e)
                error("检查json文件中的的"+key)
                raise e
        else:
            try:
                r = self.data[key]["list"]
            except Exception as e:
                error(e)
                error("检查json文件中的的"+key)
                raise e
        return r

