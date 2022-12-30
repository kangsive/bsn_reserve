from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
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
        
        self.driver = webdriver.Chrome("./chrome_diver")

        while True:
            try:
                # TODO - make it in request way
                self.one_attempt()
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


    def one_attempt(self):

        self.driver.get("https://formulieren.amsterdam.nl/TriplEforms/Directregelen/formulier/nl-NL/evAmsterdam/afspraakmakenRegistration.aspx")

        # choose location and click next
        select = Select(self.driver.find_element("id", 'ctl00_CntMain_amc_ContantHolder_ssm_ctl00_LoketkeuzeBurgerzaken'))
        select.select_by_value("LOKETOS18aa955efda0ce6da145a6622c80543548e06d91ebb0290e61281da59")
        self.driver.find_element("id", "ctl00_CntMain_amc_ContantHolder_ssm_ctl00_fAfspraakKeuzeRegistrationEfAutoGen2").click()

        # get current month, year
        current_month, current_year, table_tr_list, title_list = self.get_current_month()

        # jump to specified month
        while not self.in_schedule(current_year, self.months.index(current_month)+1):
            title_list[2].find_element(By.TAG_NAME, "a").click()
            current_month, current_year, table_tr_list, title_list = self.get_current_month()

        # check available slot
        found = self.check_slot(table_tr_list, current_year)
        if not found:
            print("not found")

        # 如果当月没有可选日期，跳转到下一个月继续查看
        while not found and self.in_schedule(current_year, self.months.index(current_month)+1, current_day=1):
            print("still not found")
            title_list[2].find_element(By.TAG_NAME, "a").click()
            current_month, current_year, table_tr_list, title_list = self.get_current_month()
            found = self.check_slot(table_tr_list, current_year)


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
                    if self.in_schedule(current_year, self.months.index(date_str[1])+1, date_str[0]):
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

    def in_schedule(self, current_year, current_month, current_day=None):
        # compare only month and year if no day given, this is for reaching specified month
        if current_day == None:
            if datetime.datetime(int(current_year), int(current_month), 1) < self.start_date:
                return False
            return True
        # compare extract day, this is for selecting time slot
        current_date = datetime.datetime(int(current_year), int(current_month), int(current_day))
        if current_date >= self.start_date and current_date <= self.end_date:
            return True
        return False




if __name__ == "__main__":
    contact_info = {
        "last_name": "Bing",
        "email_address": "123456789@qq.com",
    }
    bsn_booker = BsnReserve(start_date="2023-07-01", end_date="2023-07-10", run_ddl="2022-12-30 23:59:59", contact_info=contact_info)
    bsn_booker.start()