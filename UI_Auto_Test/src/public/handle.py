import time

from src.utils.log_opt import info


class Handle:

    def __init__(self,webdriver,picture_path="null"):
        self.driver=webdriver
        self.path = picture_path


    def elment_operation(self,obj,opt,data):
        if opt == "click":
            obj.click()

        elif opt == "send_keys":
            obj.send_keys(str(data))

        elif opt == "press":

            if str(data).lower().strip()=="ok":
                self.driver.press_keycode(23)
            elif str(data).lower().strip()=="home":
                self.driver.press_keycode(3)

        if self.path != "null":
            self.driver.get_screenshot_as_file(self.path+(str(time.time())+'.png'))
            info(self.path+(str(time.time())+'.png'))