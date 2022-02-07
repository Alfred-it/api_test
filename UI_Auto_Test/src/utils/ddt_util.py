

import yaml

from src.utils.log_opt import error


class DDT:
    ddt_file=""
    data_record={""}


def ddt(func):
    def wrapper(*args,**kwargs):
        if (".yml" in DDT.ddt_file)or (".yaml" in DDT.ddt_file):
            data = read_yaml(DDT.ddt_file)
            for record in data:
                DDT.data_record=data[record]
                func(*args,**kwargs)
        else:
            func(*args, **kwargs)
    return wrapper


def read_yaml(data_file):
    data = ""
    with open(data_file, 'r') as f:
        try:
            data = yaml.safe_load(f.read())
            print(data)
        except Exception as e:
            error("数据文件打开失败！")
            error(e)
        return data




