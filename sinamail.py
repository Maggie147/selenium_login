#!/usr/bin/python
#coding=utf-8
import os
import re
import sys
import time
import json
# import chardet
import pprint
import email
import cookielib
import threading
import requests
from multiprocessing.dummy import Pool
sys.path.append('./')
from selenium_login import SinaEmailLogin
from qqmail_tools import *
reload(sys)
sys.setdefaultencoding('utf8')

def get_mail_dir_list(header):
    global sessrequ
    url = 'http://m0.mail.sina.com.cn/wa.php?a=list_folder&calltype=auto'
    # postdata = {'sactioncount':''}
    sessrequ = requests.session()
    response = sessrequ.get(url, headers=header)    # get qqmail main html
    if str(response.status_code)[0] != '2':
        print("request failed!!")
        return
    if response.text.find('data') == -1 and response.text.find('id')  ==-1:
        return None
    res_loads = json.loads(response.text)                           # to dic
    write_data_file(res_loads, fpath='./output/%s/sinamail_main_page.json'%user, ftype='json')

    ids = res_loads['data']
    id_list = [item['id'] for item in ids]
    return id_list if id_list else None


def get_one_box_mail(fid, header):
    global sessrequ
    list_url = "http://m0.mail.sina.com.cn/wa.php?a=list_mail"

    para = {'Origin': 'http://m0.mail.sina.com.cn',
            'Referer':'http://m0.mail.sina.com.cn/classic/index.php',
            'Host':'m0.mail.sina.com.cn'}
    header.update(para)
    page = 1
    one_box_mails = []
    while True:
        postdata =  {'fid':'%s' % fid, 'order':'htime', 'sorttype':'desc', 'type':0,'pageno':'%d' % page, 'tag':-1, 'webmail':1}
        response = sessrequ.post(list_url, headers=header, data = postdata)
        try:
            js_data = json.loads(response.text)
            if not js_data['data']['maillist']:
                break

            write_data_file(js_data, fpath='./output/%s/sinamail_box_%d.json'%(user, page), ftype='json')
        except Exception as e:
            print(e)
            continue

        for item in js_data['data']['maillist']:
            one_box_mails.append((item[0], item[3], item[4], fid))
        page += 1
    one_box_mails.reverse()
    news_ids = []

    # qvchong
    for item in one_box_mails:
        if item not in news_ids:
            news_ids.append(item)
    return news_ids


def get_mail_page(para):
    global g_headers
    global sessrequ
    try:
        mail_para = para[0]
        fid = mail_para[-1]
        mid = mail_para[0]
        num = para[1]
        url = 'http://m0.mail.sina.com.cn/classic/readmail.php?webmail=1&fid={}&mid={}&ts=17644'.format(fid, mid)
        # print("URL: %s\n"%url)
        para = {'Referer':'http://m0.mail.sina.com.cn/classic/index.php',
                'Host':'m0.mail.sina.com.cn'}
        header = g_headers
        header.update(para)

        response = sessrequ.get(url, headers=header, timeout=30, stream=True)
        if str(response.status_code)[0] != '2':
            print("request failed!!")
            return
        try:
            js_data = json.loads(response.text)
            if not js_data['result']:
                return
            write_data_file(js_data, fpath='./output/{}/eml/sinamail_emal_{}.json'.format(user, num), ftype='json')
        except Exception as e:
            print(e)
            return
    except Exception as e:
        print(e)


def main():
    global user
    global sessrequ
    global g_headers

    username = "tianxuesn@sina.com"
    password = "tianxue123"
    user  =  username.split('@')[0]
    siobj = SinaEmailLogin(username, password, dtype='chrome')    # chrome, firefox
    cookie   = siobj.cookie
    host_url = siobj.host_url
    print(host_url)

    para = {'referer': 'http://mail.sina.com.cn/'}
    g_headers = get_headers(cookie, para=None)
    write_data_file(g_headers, fpath='./output/%s/sinamail_login.json'%user , ftype='json')


    id_list = get_mail_dir_list(g_headers)
    if not id_list:
        print("id_list is None")
        return

    if "all" in id_list:
        fid = "all"
        one_box_mails = get_one_box_mail(fid, g_headers)

        num = len(one_box_mails)
        nums = range(1, num +1)
        print("all maillist len: ", num)

        pool = Pool(20)
        pool.map(get_mail_page, zip(one_box_mails, nums))
        pool.close()
        pool.join()



if __name__ == '__main__':
    main()