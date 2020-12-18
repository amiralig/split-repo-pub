import time

# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# sent_from = 'tekbridgeconsulting@gmail.com'
# to = ['amiralig@gmail.com']
# subject = 'Balance sheet report'
#
# def reportUnpaid():
#     try:
#         server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#         server.ehlo()
#         server.sendmail(sent_from, to, 'Find attached the balance sheet report')
#     except Exception as e:
#         print 'Something went wrong...'+e.message

TODAY_XPATH = "//div[contains(@class,'react-datepicker__day--today') and not(contains(@class, 'react-datepicker__day--outside-month'))]"


def report():
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory": "/Users/amirali/Public/reports"}
    chromeOptions.add_experimental_option("prefs", prefs)

    #driver = webdriver.Chrome(options=options2)
    driver = webdriver.Chrome('/Users/amirali/Documents/Life-VCC/chromedriver3', chrome_options=chromeOptions)

    driver.get("https://lifeinharmony.janeapp.com/admin")
    delay = 20  # seconds


    driver.get("https://lifeinharmony.janeapp.com/admin")
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id("auth_key").clear()
    driver.find_element_by_id("auth_key").send_keys("info@lifeinharmony.ca")
    driver.find_element_by_id("auth_key").click()
    driver.find_element_by_id("auth_key").click()
    # ERROR: Caught exception [ERROR: Unsupported command [doubleClick | id=auth_key | ]]
    driver.find_element_by_id("auth_key").click()
    driver.find_element_by_id("log_in").click()
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, 'Reports')))

    on_boarding = check_exists_by_xpath(driver, "//ul[@id='onboarding_link']/li[@class='active']")
    if on_boarding:
        driver.find_element_by_xpath("//ul[@id='onboarding_link']/li[@class='active']").click()

    myElem.click()
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, 'Sales')))

    myElem.click()
    #driver.find_element_by_xpath(
    #    "(.//*[normalize-space(text()) and normalize-space(.)='Last Month'])[1]/following::p[1]").click()


    dateElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'react-datepicker-ignore-onclickoutside')]")));

    dateElem.click()


    # driver.implicitly_wait(10)
    #driver.find_element_by_xpath(
    #        "(.//*[normalize-space(text()) and normalize-space(.)='sa'])[1]/following::div["+sDate+"]").click()
    # driver.implicitly_wait(10)
    #driver.find_element_by_xpath(
    #    "(.//*[normalize-space(text()) and normalize-space(.)='sa'])[1]/following::div["+eDate+"]").click()

    #nput_range = driver.find_element_by_name("date_range")
    #input_range.clear()
    #input_range.send_keys("2019-05-01 to 2019-05-25")

    # Check first if Feb 1 is on the list. If not go back enough time to reach it
    time_exists = check_exists_by_xpath(driver, "//div[@aria-label='month-2019-02']/div[@aria-label='day-2']")
    while not time_exists:
        driver.find_element_by_xpath("//button[contains(@class,'react-datepicker__navigation--previous')]").click()
        time_exists = check_exists_by_xpath(driver, "//div[@aria-label='month-2019-02']/div[@class='react-datepicker__week']/div[@aria-label='day-2']")
    if time_exists:
        driver.find_element_by_xpath("//div[@aria-label='month-2019-02']/div[@class='react-datepicker__week']/div[@aria-label='day-2']").click()

    today_exists = check_exists_by_xpath(driver, "//button[@class='react-datepicker__day--today']")
    while not today_exists:
        driver.find_element_by_xpath("//button[contains(@class,'react-datepicker__navigation--next')]").click()
        today_exists = check_exists_by_xpath(driver, "%s" % TODAY_XPATH)
    if today_exists:
        driver.find_element_by_xpath(TODAY_XPATH).click()
    #today_exists
    time.sleep(120)

    #filter_exists = check_exists_by_xpath(driver, "//div[@class='flex']/div/div[contains(@role,'button')]")
    #if (filter_exists):

    #driver.find_element_by_xpath("/html/body/div[7]/div/div/div[2]/div/div/div/div[3]/div/span/div/div/div/ul[2]/li/div").click()
    driver.find_element_by_xpath("//div[contains(@class,'filter-bar-button') and contains(@class,'dropdown-toggle')]").click()
    # new export to excel button
    driver.find_element_by_xpath("//*[contains(text(), 'Export to Excel')]").click()

    #driver.find_element_by_link_text("Export to Excel").click()
    # ERROR: Caught exception [ERROR: Unsupported command [selectWindow | win_ser_1 | ]]
    #time.sleep(10)

    newWindow=driver.window_handles[-1]
    #unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')

    #for winHandle in driver.window_handles:
    #    driver.switch_to.window(winHandle)
    #downloadTab = driver.window_handles[1]
    #downloadTab = str(downloadTab)
    driver.switch_to.window(newWindow)
    #driver.switch_to.window()
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//i[contains(@class, 'icon-download')]")))
    #myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'xlsx')]")))
    time.sleep(5)
    myElem.click()
    #os.system("scp -i /Users/amirali/Downloads/mac-odoo.pem /Users/amirali/Documents/Life-VCC/payroll/lifeVCC ubuntu@ec2-35-162-121-232.us-west-2.compute.amazonaws.com:~")
    time.sleep(15)
    driver.close()
    #copyfile(src, dst)



#     def is_element_present(self, how, what):
#         try:
#             self.driver.find_element(by=how, value=what)
#         except NoSuchElementException as e:
#             return False
#         return True
#
#     def is_alert_present(self):
#         try:
#             self.driver.switch_to_alert()
#         except NoAlertPresentException as e:
#             return False
#         return True
#
#     def close_alert_and_get_its_text(self):
#         try:
#             alert = self.driver.switch_to_alert()
#             alert_text = alert.text
#             if self.accept_next_alert:
#                 alert.accept()
#             else:
#                 alert.dismiss()
#             return alert_text
#         finally:
#             self.accept_next_alert = True
#
#     def tearDown(self):
#         self.driver.quit()
#         self.assertEqual([], self.verificationErrors)
#
#
#     if __name__ == "__main__":
#         unittest.main()
#
#     # reportUnpaid()
# o = UntitledTestCase()

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

#sDate = sys.argv[1]
#eDate = sys.argv[2]
report()
