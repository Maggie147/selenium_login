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

def sina_email_login(Email, Passwd):
    url = "http://mail.sina.com.cn/"

    head_url = None
    oCookie_list = None

    # driver = webdriver.PhantomJS(executable_path='./driver/phantomjs')
    # driver = webdriver.Chrome(executable_path = './driver/chromedriver')
    driver = webdriver.Firefox(executable_path = './driver/geckodriver')

    driver.implicitly_wait(5)
    driver.set_page_load_timeout(40)

    try:
        driver.get(url)
    except TimeoutException:
        print 'time out after 10 seconds when loading page'
        driver.execute_script('window.stop()')

    print '1'
    time.sleep(2)

    try:
        driver.find_element_by_id('freename').send_keys(Email)          #send username
        time.sleep(2)
        driver.find_element_by_id('freepassword').send_keys(Passwd)     #send password
    except BaseException as e:
        print e
        return -1

    print '2'
    print "value is " + driver.find_element_by_id("freename").get_attribute("value")
    print "value is " + driver.find_element_by_id("freepassword").get_attribute("value")
    time.sleep(4)

    print '3'
    driver.find_element_by_class_name('loginBtn').click()

    ts = 0
    time.sleep(1)
    while True:
        time.sleep(1)
        print driver.current_url                            # jump to url
        print ts
        if '/classic/index.php' in driver.current_url:
            oCookie_list =  driver.get_cookies()            # get cookie
            head_url = driver.current_url
            break
        ts += 1
        if ts > 40:
            print 'connect timeout'
            driver.close()
            return -1
    driver.close()
    if not head_url or not oCookie_list:
        return -1

    print oCookie_list
    print "type(oCookie_list)", type(oCookie_list)
    return "; ".join([item["name"] + "=" + item["value"] for item in oCookie_list])


def qq_email_login(Email, Passwd):
    url = "http://mail.qq.com/"

    head_url = None
    oCookie_list = None

    # driver = webdriver.PhantomJS(executable_path='./driver/phantomjs')
    driver = webdriver.Chrome(executable_path = './driver/chromedriver')
    # driver = webdriver.Firefox(executable_path = './driver/geckodriver')

    driver.implicitly_wait(5)
    driver.set_page_load_timeout(40)

    try:
        driver.get(url)
    except TimeoutException:
        print 'time out after 10 seconds when loading page'
        driver.execute_script('window.stop()')

    print '1'
    time.sleep(2)

    try:
        driver.switch_to.frame("login_frame")
        driver.find_element_by_id('switcher_plogin').click()
    except BaseException as e:
        print e
        return -1

    print '2'

    try:
        driver.find_element_by_id('u').send_keys(Email) #send username
        time.sleep(5)
        driver.find_element_by_id('p').send_keys(Passwd) #send username
    except BaseException as e:
        print e
        return -1

    print '3'
    print "value is " + driver.find_element_by_id("u").get_attribute("value")
    print "value is " + driver.find_element_by_id("p").get_attribute("value")

    print '4'
    driver.find_element_by_id('login_button').click()

    time.sleep(1)
    ts = 0
    while True:
        time.sleep(1)
        print ts
        print driver.current_url
        if 'frame_html?sid=' in driver.current_url:
            oCookie_list =  driver.get_cookies()
            head_url = driver.current_url
            break
        ts += 1
        if ts > 40:
            print 'connect timeout'
            driver.close()
            break
    driver.close()
    if not head_url or not oCookie_list:
        return None

    # print oCookie_list
    # print "type(oCookie_list)", type(oCookie_list)

    return   "; ".join([item["name"] + "=" + item["value"] for item in oCookie_list]), head_url
    # return {item['name']:item['value'] for item in oCookie_list}, head_url


def get_headers(cookie=None):
    header = {}
    if cookie:
        header['Cookie'] = cookie
    header['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"
    return header

def get_sid(buf, head_str='?sid=', tail_str='&'):
    sid = ''
    try:
        begin = buf.find(head_str)
        if begin:
            end = buf[begin+len(head_str):].find(tail_str)
            if end:
                sid = buf[begin+len(head_str): begin+len(head_str)+end]
            else:
                sid = buf[begin: ]
        else:
            print "no find head_str"
    except Exception as e:
        print e
    return sid


def write_date_2file(path, fname, data,):
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        with open(path+fname, "wb") as fp:
            fp.write(data)
    except Exception as e:
        print e
        return False
    return True

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
    s = qq_email_login(username, password)
    # sina_email_login("yangzhilivip@sina.com", "yzl123")

    cookie = s[0]
    host_url = s[1]
    sid = get_sid(host_url)
    header = get_headers(cookie)
    # print '-'*40
    # print header

    page1 = get_qqmail_list(header, sid, '0')
    # print page1
    write_date_2file('./', 'page1.html', page1.decode().encode('gbk'))

if __name__ == '__main__':
    main()
