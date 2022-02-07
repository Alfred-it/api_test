import time


from src.utils.log_opt import error, info


class Element:

    def __init__(self,webdriver,picture_path="null"):

        self.driver = webdriver
        self.path = picture_path

    def get_element(self,by,val):

        el="null"
        try:
            if by == "id":
                el=self.driver.find_element_by_id(val)

            elif by == "xpath":
                el = self.driver.find_element_by_xpath(val)
        except Exception as e:
            el = "null"
            error("检查元素是否填写正确")
            error(e)

        # t=self.path+(str(time.time())+'.png')

        # if self.path != "null":
        #     self.driver.get_screenshot_as_file(self.path+(str(time.time())+'.png'))
        #     info(self.path+(str(time.time())+'.png'))

        return el



