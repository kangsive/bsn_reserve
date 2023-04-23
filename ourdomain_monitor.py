from selenium import webdriver
from selenium.webdriver.common.by import By
from dateutil.relativedelta import *
import zmail
import time


def init_driver():
    global driver
    driver = webdriver.Chrome("./chrome_diver")

def one_attempt(link):
    driver.get(link)
    # Wait util the "Accept All Cookies" button display
    driver.implicitly_wait(5)
    # Another element is covering the element you are trying to click, cannot directly click on it
    try:
        element = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        driver.execute_script("arguments[0].click();", element)
    except:
        pass
    button = driver.find_element(By.CSS_SELECTOR, "#first-section > div > div > div.wrapper-menu.booknow > div > div.filtering-group.booknow-location > a:nth-child(1)")
    # Wait util the element
    driver.implicitly_wait(5)
    driver.execute_script("arguments[0].click();", button)
    # Get result
    try:
        driver.find_element(By.CSS_SELECTOR, "#first-section > div > div > div.wrapper-articles > div.empty-message > h3")
        print("Not found")
    except:
        print("Found")
    
def send_email(receiver: str, mail: dict):
    """Send email via qq SMTP server
    Reference: https://www.cnblogs.com/sean-test/p/17013716.html
    Args:
        receiver: the email address to reveive
        mail: {'subject':'标题','content_text':'邮件正文.'}
    """    
    server = zmail.server('1910173655@qq.com', 'kagckmlxabxrebdh')
    server.send_mail("1205498974@qq.com", {'subject':'标题','content_text':'邮件正文.'})

def monitor_availability():
    while True:
        dimen_link = "https://www.thisisourdomain.nl/amsterdam-diemen/apartments-studios"
        one_attempt(dimen_link)

        time.sleep(1)

        south_east_link = "https://www.thisisourdomain.nl/amsterdam-south-east/apartments-studios"
        one_attempt(south_east_link)

        time.sleep(1)

init_driver()
monitor_availability()




