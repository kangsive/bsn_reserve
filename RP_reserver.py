from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import datetime
import time
import traceback


from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class RpReserve:
    def __init__(
        self, start_date=None, end_date=None, run_ddl=None, contact_info=None
    ) -> None:
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        self.run_ddl = datetime.datetime.strptime(run_ddl, "%Y-%m-%d %H:%M:%S")
        self.contact_info = contact_info
        self.success = False
        self.months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

    def start(self):
        self.driver = webdriver.Chrome("./chrome_diver")
        self.one_attempt()
        time.sleep(5)

    def one_attempt(self):
        self.driver.get("https://oap.ind.nl/oap/en/#/doc")
        select = Select(self.driver.find_element(By.ID, "desk"))
        select.select_by_visible_text("IND Amsterdam")
        # wait until calendar refresh, otherwise there will be StaleElementReferenceException when finding days's button
        time.sleep(1)

        self.calendar = self.driver.find_element(
            By.CSS_SELECTOR,
            "#js-content > div > div > div > oap-appointment > div > div > oap-appointment-reservation > div > form > div:nth-child(5) > available-date-picker > div > datepicker > datepicker-inner > div > daypicker > table",
        )

        while True:
            title = (
                self.calendar.find_element(By.TAG_NAME, "thead")
                .find_elements(By.TAG_NAME, "tr")[0]
                .find_elements(By.TAG_NAME, "th")
            )
            month_year = title[1].find_element(By.TAG_NAME, "button").text.split(" ")
            next_button = title[2].find_element(By.TAG_NAME, "button")

            if not self.in_schedule(month_year[1], self.months.index(month_year[0])+1):
                next_button.click()
                continue

            weeks = self.calendar.find_element(By.TAG_NAME, "tbody").find_elements(
                By.TAG_NAME, "tr"
            )

            print(month_year)

            button = self.check_slot(weeks, month_year)
            if not button:
                if self.in_schedule(
                month_year[1], self.months.index(month_year[0])+1, current_day=1
                ):  
                    next_button.click()
                else:
                    break
            else:
                self.success = True
                self.select_and_proceed(button)
                self.fill_in_info()
                break

    def check_slot(self, weeks, month_year):
        for week in weeks:
            days = week.find_elements(By.TAG_NAME, "td")
            for day in days:
                button = day.find_element(By.TAG_NAME, "button")
                day_txt = button.find_element(By.TAG_NAME, "span").text
                if not button.get_attribute("disabled"):
                    # current day might not belong to current month
                    if int(day_txt) > int(days[-1].find_element(By.TAG_NAME, "button").find_element(By.TAG_NAME, "span").text):
                        continue
                    if self.in_schedule(month_year[1], self.months.index(month_year[0])+1, current_day=day_txt):
                        # print(day_txt)
                        return button
        return None

    def select_and_proceed(self, button):
        button.click()
        time_slot = self.driver.find_element(By.ID, "timeSlot")
        select = Select(time_slot)
        # options = time_slots.find_elements(By.TAG_NAME, "option")
        print(max(1, len(select.options) // 2))
        select.select_by_index(max(1, len(select.options) // 2))
        self.driver.find_element(By.CSS_SELECTOR, "#js-content > div > div > div > oap-appointment > div > div > oap-appointment-reservation > div > form > div:nth-child(7) > button").click()

    def fill_in_info(self):
        time.sleep(1)
        self.driver.find_element(By.ID, "form-text-0").send_keys(self.contact_info["email_address"])
        self.driver.find_element(By.ID, "form-text-1").send_keys(self.contact_info["phone_number"])
        self.driver.find_element(By.ID, "form-text-2").send_keys(self.contact_info["v_number"])
        self.driver.find_element(By.ID, "form-text-4").send_keys(self.contact_info["first_name"])
        self.driver.find_element(By.ID, "form-text-5").send_keys(self.contact_info["last_name"])
        # TODO click button to confirm appointment
        # self.driver.find_element(By.CSS_SELECTOR, "#js-content > div > div > div > oap-appointment > div > div:nth-child(2) > oap-appointment-personalia > form > div:nth-child(5) > div > div > button")


    def in_schedule(self, current_year, current_month, current_day=None):
        # compare only month and year if no day given, this is for reaching specified month
        if current_day == None:
            if datetime.datetime(int(current_year), int(current_month), 1) < self.start_date:
                return False
            return True
        # compare extract day, this is for selecting time slot
        current_date = datetime.datetime(
            int(current_year), int(current_month), int(current_day)
        )
        if current_date >= self.start_date and current_date <= self.end_date:
            return True
        return False



if __name__ == "__main__":
    contact_info = {
        "first_name": "Chandler",
        "last_name": "Bing",
        "email_address": "123456789@qq.com",
        "phone_number": "792545",
        "v_number": "4681389",

    }
    bsn_booker = RpReserve(
        start_date="2023-02-01",
        end_date="2024-07-10",
        run_ddl="2022-12-30 23:59:59",
        contact_info=contact_info,
    )
    bsn_booker.start()
