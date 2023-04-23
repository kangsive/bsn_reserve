from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from dateutil.relativedelta import *
import time
import datetime
import traceback

opt = ChromeOptions()            # 创建Chrome参数对象
opt.headless =  False
driver = webdriver.Chrome("./chrome_diver", options=opt)
driver.get("https://studentexperience.nl/en/studios/?countryId=166")
driver.find_element(By.CSS_SELECTOR, "body > div.cc-window.cc-floating.cc-type-opt-in.cc-theme-edgeless.cc-bottom.cc-left.cc-color-override--433619286 > div > a.cc-btn.cc-allow").click()
driver.find_element(By.CSS_SELECTOR, "#header > div > div > div.right-section > div.top-header > div.portal-button-wrapper.mobile.is-hidden-desktop > a.login-btn").click()
driver.find_element(By.CSS_SELECTOR, "#header > div > div > div.right-section > div.top-header > div.portal-button-wrapper.mobile.is-hidden-desktop > nav > ul > li:nth-child(1) > a").click()
driver.find_element(By.CSS_SELECTOR, "#email").send_keys("1205498974@qq.com")
driver.find_element(By.CSS_SELECTOR, "#password").send_keys("Pdk@160411")
driver.find_element(By.CSS_SELECTOR, "body > div.site-container > div.page-wrapper > section > div > div:nth-child(2) > div > div > div.column.is-half.login-wrap > div > form > button"
).click()
driver.find_element(By.CSS_SELECTOR, "body > div.site-container > div.page-wrapper > div > div.modal-card > section > a").click()


time.sleep(600)