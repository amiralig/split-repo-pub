import sys
import os

import socket
from _ssl import SSLEOFError
import traceback

import schedule

import imaplib
import credentials
import logging

from email import parser
from email.utils import parseaddr
from selenium import webdriver
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

logpath=sys.argv[1]
if not os.path.exists(logpath):
    log = open(logpath, "w")
    log.close()

logging.basicConfig(filename=logpath,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)



def sender(fromEmail, invoiceDate):
    try:
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": "/Users/amirali/Public/reports"}
        chromeOptions.add_experimental_option("prefs", prefs)
        #chromeOptions.headless = True
        #options.add_argument("no-sandbox")
        driver = webdriver.Chrome('/Users/amirali/Documents/Life-VCC/chromedriver3', chrome_options=chromeOptions)


        driver.get("https://lifeinharmony.janeapp.com/admin")
        delay = 15  # seconds

        driver.get("https://lifeinharmony.janeapp.com/admin")
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("auth_key").clear()
        driver.find_element_by_id("auth_key").send_keys("info@lifeinharmony.ca")
        driver.find_element_by_id("auth_key").click()
        driver.find_element_by_id("auth_key").click()
        # ERROR: Caught exception [ERROR: Unsupported command [doubleClick | id=auth_key | ]]
        driver.find_element_by_id("auth_key").click()
        driver.find_element_by_id("log_in").click()

        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, 'Clients')))

        myElem.click()

        on_boarding = check_exists_by_xpath(driver, "//ul[@id='onboarding_link']/li[@class='active']")
        if on_boarding:
            driver.find_element_by_xpath("//ul[@id='onboarding_link']/li[@class='active']").click()
        time.sleep(5)

        client_search = check_exists_by_xpath(driver,
                                            "//input[@placeholder='Client Search...']")

        if str(fromEmail) is None or str(invoiceDate) is None:
            logging.info('Name or date is empty')
            driver.close()
            return 1

        if client_search:
            logging.info('client search found')
            myElem = driver.find_element_by_xpath("//input[@placeholder='Client Search...']")
            logging.info('name  is '+str(fromEmail))
            myElem.send_keys(fromEmail)
            time.sleep(5)
        else:
            print 'client search did not find: '+fromEmail
            driver.close()
            return 1

        #check_exists_by_xpath()

        myElem = driver.find_element_by_xpath("//li[contains(@class, 'list-group-item')]/a")
        if myElem:
            name = myElem.get_attribute("href")
            logging.info('Name found: '+name)
            myElem.click();
            time.sleep(5)

            if str(name).find('#') != -1:
                billing = driver.find_element_by_xpath("//a[contains(@href, '"+str(name).split('#')[1]+"/billing')]")
                billing.click()
                time.sleep(5)



                #driver.get(name)
                allDates = driver.find_elements_by_xpath("//tbody[contains(@class, 'purchases')]/tr/td/div[contains(@class,'no-wrap')]")

                allRows = driver.find_elements_by_xpath("//tbody[contains(@class, 'purchases')]/tr/td[contains(@class,'controls')]")
                i = 0
                for each in allRows:
                    if allDates[i] is not None and allDates[i].text is not None:
                        date = datetime.strptime(allDates[i].text, '%b %d, %Y')
                        if date == invoiceDate:
                            logging.info('An invoice is found for name: '+ name +', the given date: '+allDates[i].text)
                            toggle = each.find_element_by_xpath(".//button[contains(@class,'dropdown-toggle')]")
                            if toggle:
                                toggle.click()
                                time.sleep(5)
                                email = each.find_element_by_xpath(".//a[contains(@class, 'email-receipt')]")
                                if email:
                                    logging.info('Will send email for '+name)
                                    email.click()
                                    time.sleep(5)
                                    driver.close()
                                    return 0
                                else:
                                    logging.warn('email option not found')
                            else:
                                logging.info('Toggle not found within the purchase row')
                    i = i + 1
            else:
                logging.warn('No patient billing link is found for the given link')
        else:
            logging.warn('The client name was not found')
        driver.close()
        return 1
    except WebDriverException:
        #Cross platform
        logging.warn('Will try to kill geckodriver')
        os.system("killall -9 geckodriver")
        return 1
    except Exception as e:
        logging.error('Standard error occurred: '+traceback.format_exc())
        return 1


def email_checker():
    #pop_conn = poplib.POP3_SSL('pop.gmail.com')

    # Get messages from server:
    #messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]

    #pop_conn.set_debuglevel(1)
    # get pop3 server welcome message.
    #pop3_server_welcome_msg = pop_conn.getwelcome().decode('utf-8')
    # print out the pop3 server welcome message.
    #print(pop_conn.getwelcome().decode('utf-8'))

    # user account authentication
    #pop_conn.user('tech@lifeinharmony.ca')
    #pop_conn.pass_('GozoeBlue67')

    # stat() function return email count and occupied disk size



    try:
        imap_ssl_host = 'imap.gmail.com'
        imap_ssl_port = 993
        #socket.setdefaulttimeout(10)
        server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
        server.login(username, password)
        server.select('INBOX')
        logging.info('Will check emails for anything new')
        status, data = server.uid('SEARCH',None, '(UNSEEN)')
        for num in data[0].split():
            status, data = server.uid('FETCH', num, '(BODY[HEADER.FIELDS (SUBJECT DATE FROM)])')
            email_msg = data[0][1]
            sendto = ''
            if str(email_msg).find('\n') != -1:
                many = str(email_msg).split('\n')
                for each in many:
                    if each.startswith('From:'):
                        indexOfLess = each.find('<')
                        indexOfMore = each.find('>')
                        if (indexOfLess != -1 and indexOfMore != -1):
                            sendto = each[indexOfLess+1:indexOfMore].strip()
                        else:
                            sendto = each.replace("From:",'').strip()
                        logging.info("will send invoice to:"+sendto)
                    elif each.startswith('Subject:'):
                        indexDate=each.find('Date:')
                        indexComma=each.find(',')
                        if indexDate != -1 and indexComma != -1:
                            invoicedate=each[indexDate:indexComma]
                            invoicedate=invoicedate.replace('Date:','').strip()
                            logging.info("invoicedate is: "+invoicedate)
                            if invoicedate != '':
                                actualdate=datetime.strptime(invoicedate, '%m/%d/%y')
                                indexemail=each.find('Email:')
                                if indexemail != -1:
                                    sendto = each[indexemail:len(each)-1]
                                    sendto = sendto.replace('Email:', '').strip()
                                    logging.info('Subject Email is: '+sendto)
                                if (sendto is not None and len(sendto) != 0):
                                    result = sender(sendto, actualdate)
                                if result != 0:
                                    logging.warn('No will mark as unread')
                                    server.uid('STORE', num, '-FLAGS', '(\Seen)')

                            #print email_msg

    except SSLEOFError:
        logging.error('SSL error ocurred!')
    except Exception as e:
        logging.error('Standard error occurred: '+traceback.format_exc())


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


schedule.every(5).minutes.do(email_checker)

while True:
    schedule.run_pending()
    time.sleep(2)
