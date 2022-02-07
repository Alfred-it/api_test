import time

from appium import webdriver

config={
    "platformName":"Android",
    "deviceName":"172.33.122.158:5555",
}

driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub",config)


size = driver.get_window_size()
print(size)

driver.find_element_by_id("com.xylink.launcher:id/text").click();
time.sleep(3)

el = driver.find_element_by_id("com.xylink.gill:id/call_nemo_input")
el.send_keys("9005534686")

p=driver.find_element_by_id("com.xylink.gill:id/whole_view")
# p.click()
driver.press_keycode(23)
time.sleep(3)

driver.find_element_by_id("com.xylink.gill:id/hang_up").click()

