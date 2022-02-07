import json
import os

from src.utils.log_opt import info


class FileOperation:

    def read(self,cachePath):

        if os.path.exists(cachePath) == False:
            cacheDict = {
                "change": False
            }
            info("cache file is created")
            info(cachePath)
            return cacheDict

        with open(cachePath,"r") as fr:
            cacheData = fr.read()
            cacheDict=json.loads(cacheData)
            cacheDict["change"]=False

            # 元素计数器清零
            for key in cacheDict.keys():
                if key != "change":
                    cacheDict[key]["num"]=0

        return cacheDict

    def write(self,cacheData,cachePath):
        with open(cachePath,"w") as fw:
            fw.write(json.dumps(cacheData))






#
# f=FileOperation()
# f.read()
# f.write()


