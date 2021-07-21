from selenium import webdriver
from time import sleep

driver = webdriver.Chrome()
driver.get("https://connect.garmin.com/signin/")
sleep(4)
driver.find_element_by_class_name("login_email valid").sendKeys("aune150@gmail.com")
driver.find_element_by_xpath("//*[@id='password']")

