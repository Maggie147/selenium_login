#!/usr/bin/python
#coding=utf-8
import os
import re
import sys
import time
import json
# import chardet
import cookielib
import email
import threading
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import requests
reload(sys)
sys.setdefaultencoding('utf8')


class QQEmailLogin(object):
    def __init__(self, email, passwd, dtype='chrome', debug=0):
        url = 'http://mail.qq.com/'
        self.email = email
        self.passwd = passwd
        self.debug = debug

        mydrvier = self.get_driver(dtype)
        results  = self.qq_login(url, mydrvier)
        self.cookie   = results[0]
        self.host_url = results[1]


    def get_driver(self, dtype):            # type: chrome, geckdriver, phantoms
        try:
            print("Step1: get webdriver")
            dtype = dtype.lower()
            if 'chrome' in dtype:
                driver = webdriver.Chrome(executable_path = './driver/chromedriver')
            elif 'firefox' in dtype:
                driver = webdriver.Firefox(executable_path = './driver/geckodriver')
            elif 'phantom' in dtype:
                driver = webdriver.PhantomJS(executable_path='./driver/phantomjs')
            else:
                print("No Exist web driver: {}".format(dtype))
                sys.exit(1)

            driver.implicitly_wait(5)               #  隐性等待
            driver.set_page_load_timeout(40)        #  设置超时
            return driver
        except Exception as e:
            print(e)
            sys.exit(1)

    def qq_login(self, url, driver):
        head_url = None
        oCookie_list = None

        print("Step2: get url")
        try:
            driver.get(url)
        except TimeoutException:
            print('time out after 10 seconds when loading page')
            driver.execute_script('window.stop()')
        time.sleep(2)        # 强制等待

        print("Step3: Analyse html")
        try:
            driver.switch_to.frame("login_frame")
            driver.find_element_by_id('switcher_plogin').click()
        except BaseException as e:
            print(e)
            return (None, None)

        try:
            driver.find_element_by_id('u').send_keys(self.email)             # input username
            time.sleep(5)
            driver.find_element_by_id('p').send_keys(self.passwd)            # input password
        except BaseException as e:
            print(e)
            return (None, None)
        print("Acount value: ", driver.find_element_by_id("u").get_attribute("value"))
        print("Passwd value: ", driver.find_element_by_id("p").get_attribute("value"))

        print("Step4: Send  Login Request")
        driver.find_element_by_id('login_button').click()

        print("login...")
        time.sleep(1)
        ts = 0
        while True:
            time.sleep(1)
            # print(ts)
            # print(driver.current_url)
            if 'frame_html?sid=' in driver.current_url:
                oCookie_list =  driver.get_cookies()
                head_url = driver.current_url
                break
            ts += 1
            if ts > 40:
                print('connect timeout')
                driver.close()
                break
        driver.close()
        if not head_url or not oCookie_list:
            return (None, None)

        if self.debug:
            print(oCookie_list)
            print("type(oCookie_list)", type(oCookie_list))

        # return {item['name']:item['value'] for item in oCookie_list}, head_url
        return   "; ".join([item["name"] + "=" + item["value"] for item in oCookie_list]), head_url



def get_qqmail_list(header, sid, page):
    list_req = "http://mail.qq.com/cgi-bin/mail_list?sid=%s&folderid=1&folderkey=1&page=%s&s=inbox&topmails=0&\
    showinboxtop=1&ver=933714.0&cachemod=maillist&cacheage=7200&r=&selectall=0"%(sid, page)

    my_session = requests.Session()
    response = my_session.get(list_req, headers = header, verify=False)
    # print response.text
    return response.text


def get_qqmail_html(header, sid, page):
    email_req = "https://mail.qq.com/cgi-bin/readmail?folderid=1&folderkey=1&t=readmail&\
    mailid=%s&mode=pre&maxage=3600&base=12.82&ver=12968&sid=%s"%(sid, page)

    my_session = requests.Session()
    response = my_session.get(list_req, headers = header, verify=False)
    # print response.text
    return response.text


def main():
    username = "925321080@qq.com"
    password = "dong890721!"
    qqobj = QQEmailLogin(username, password, dtype='chrome')
    print(qqobj.cookie)
    print(qqobj.host_url)



if __name__ == '__main__':
    main()
