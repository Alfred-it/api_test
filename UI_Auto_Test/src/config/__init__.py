import os

root_dir = os.path.realpath(__file__)
configPath = root_dir[0:root_dir.rfind("__init__")]+"config.json"
