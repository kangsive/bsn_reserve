from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from dateutil.relativedelta import *
import time
import datetime
import traceback


class BsnReserve:

    def __init__(self, start_date=None, end_date=None, run_ddl=None, contact_info=None) -> None:
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        self.run_ddl = datetime.datetime.strptime(run_ddl, "%Y-%m-%d %H:%M:%S")
        self.contact_info = contact_info
        self.success = False
        self.months = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']

    def start(self):
        opt = ChromeOptions()            # 创建Chrome参数对象
        opt.headless = False  
        self.driver = webdriver.Chrome("./chrome_diver", options=opt)

        while True:
            try:
                # TODO - make it in request way
                self.one_attempt("LOKETCN8df7800ec7268250a76820491e1ad3f21ea147f762facaacca7c012d8")
                time.sleep(0.5)
                self.one_attempt("LOKETNWde616374b05458c8d839af202ed735f0ccc9c57853fa2242d2dd84fdb")
                time.sleep(0.5)
                self.one_attempt("LOKETNO1480287a0e75244c4501bf4fa1337300c2bfd72db8034b9db2ffeef3c")
                time.sleep(0.5)
                self.one_attempt("LOKETOS18aa955efda0ce6da145a6622c80543548e06d91ebb0290e61281da59")
                time.sleep(0.5)
                self.one_attempt("LOKETWE628a2e4841355090a9a87d09bcbbe748bc521f07952cc4122994d6351")
                time.sleep(0.5)
                self.one_attempt("LOKETZD0a818af82bbde245721278f5962d6cc1fd15a0dc5f6b8ca705ef9031e")
                time.sleep(0.5)
                self.one_attempt("LOKETZO9da42f0936a7c1b31d19e83c8cd81dade9bdf816e3a83ee95de6e497a")
                time.sleep(0.5)
                self.one_attempt("LOKETWSa5cb3e28a8d15cd1139155773858f5fc8d3a6b53d9588d3b282bbc265")
            except:
                traceback.print_exc()

            if self.success:
                break
            if datetime.datetime.now() > self.run_ddl:
                break

            print("one attempt")
            time.sleep(5)

        print("end")
        time.sleep(10)


    def one_attempt(self, location):

        self.driver.get("https://formulieren.amsterdam.nl/TriplEforms/Directregelen/formulier/nl-NL/evAmsterdam/afspraakmakenRegistration.aspx")

        # choose location and click next
        select = Select(self.driver.find_element("id", 'ctl00_CntMain_amc_ContantHolder_ssm_ctl00_LoketkeuzeBurgerzaken'))
        select.select_by_value(location)
        self.driver.find_element("id", "ctl00_CntMain_amc_ContantHolder_ssm_ctl00_fAfspraakKeuzeRegistrationEfAutoGen2").click()

        # jump to specified month
        current_month, current_year, table_tr_list, title_list = self.jump_to_start_month()

        found = False
        # check available slot, 如果当月没有可选日期，跳转到下一个月继续查看
        while not found:
            current_month = self.months.index(current_month)+1
            if datetime.datetime(int(current_year), int(current_month), 1) > self.end_date:
                break
            else:
                found = self.check_slot(table_tr_list, current_year)
                if not found:
                    print("Not found in month: {}".format(current_month))
                    title_list[2].find_element(By.TAG_NAME, "a").click()
                    current_month, current_year, table_tr_list, title_list = self.get_current_month()

    def get_current_month(self):
        """
        Returns:
            current month
            current year
            table_tr_list: elements of every line in caledar table
            title_list: elements with tag '<', '<DATE>', '>'
        """
        canlendar_tbody = self.driver.find_element(By.CSS_SELECTOR, "#ctl00_CntMain_amc_ContantHolder_ssm_ctl00_Afspraak_Calendar > tbody")
        table_tr_list = canlendar_tbody.find_elements(By.TAG_NAME, "tr")
        title_list = table_tr_list[0].find_element(By.TAG_NAME, "tbody").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "td")
        date = title_list[1].text.split(" ")
        return date[0], date[1], table_tr_list, title_list

    def jump_to_start_month(self):
        reach = False
        while not reach:
            current_month, current_year, table_tr_list, title_list = self.get_current_month()
            current_month_int = self.months.index(current_month)+1
            # print(current_month)
            if datetime.datetime(int(current_year), int(current_month_int), 1) + relativedelta(months = +1) < self.start_date:
                title_list[2].find_element(By.TAG_NAME, "a").click()
            elif datetime.datetime(int(current_year), int(current_month_int), 1) > self.start_date:
                title_list[0].find_element(By.TAG_NAME, "a").click()
            else:
                reach = True
        return current_month, current_year, table_tr_list, title_list
        

    def check_slot(self, table_tr_list, current_year):
        # 查看当前月可选日期, 如果存在则选中继续
        # TODO 查到可选日期发送邮件通知
        found = False
        for tr in table_tr_list:
            line = tr.find_elements(By.TAG_NAME, "td")
            for day in line:
                state = day.get_attribute("class")
                # if this day is enable, process reservation
                if state=="enabled":
                    button = day.find_element(By.TAG_NAME,"a")
                    date_str = button.get_attribute("title").split(" ")
                    # check if in schedule
                    current_date = datetime.datetime(int(current_year), self.months.index(date_str[1])+1, int(date_str[0]))
                    if current_date <= self.end_date and current_date >= self.start_date:
                        found = True
                        # print(date_str)
                        button.click()

                        # choose time slot and click next
                        time_slots = self.driver.find_element(By.CSS_SELECTOR, "#ctl00_CntMain_amc_ContantHolder_ssm_ctl00_Tijd")
                        select = Select(time_slots)
                        options = time_slots.find_elements(By.TAG_NAME, "option")
                        select.select_by_index(max(1, len(options)//2))
                        self.driver.find_element(By.CSS_SELECTOR, "#ctl00_CntMain_amc_ContantHolder_ssm_ctl00_fAfspraakKeuzeRegistrationEfAutoGen4").click()

                        # fill in contact_info and next
                        self.fill_in_info()
                        print("Success!")
                        # TODO click next and finish reservation
                        # self.driver.find_element(By.CSS_SELECTOR, "#ctl00_CntMain_amc_ContantHolder_ssm_ctl00_fAfspraakKeuzeRegistrationEfAutoGen6").click()

                        self.success = True
                            
                        break
            if self.success == True:
                break
        return found

    def fill_in_info(self):
        # fill in last_name
        self.driver.find_element(By.CSS_SELECTOR, "#ctl00_CntMain_amc_ContantHolder_ssm_ctl00_Achternaam").send_keys(self.contact_info["last_name"])
        # fill in email address
        self.driver.find_element(By.CSS_SELECTOR, "#ctl00_CntMain_amc_ContantHolder_ssm_ctl00_Emailadres").send_keys(self.contact_info["email_address"])




if __name__ == "__main__":
    contact_info = {
        "last_name": "Zhu",
        "email_address": "zhudongdong1997@163.com",
    }
    bsn_booker = BsnReserve(start_date="2023-02-04", end_date="2023-02-28", run_ddl="2023-02-15 23:59:59", contact_info=contact_info)
    bsn_booker.start()