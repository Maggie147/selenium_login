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
from selenium_login import QQEmailLogin
from qqmail_tools import *
reload(sys)
sys.setdefaultencoding('utf8')


# 每一类邮件主页请求并分析, 返回每一类邮件中所有邮件的url_list
def analy_page_list(url, header, args):
    global user
    response = sessrequ.get(url, headers=header)      # 请求 每一类邮件main html
    if str(response.status_code)[0] != '2':
        print("request failed!!")
        return None
    write_data_file(response.text, fpath='./output/{}/maillist_page{}.html'.format(user, args['folderid']), ftype='html')

    # 解析每类邮件主页 显示的邮件页数，无法获取页数或者页数为0，该类中没有邮件
    cnt = mail_page_cnt(response.text)
    if not cnt:
        return None

    mail_list = []
    # for i in range(0, cnt+1):
    for i in range(1):
        url_list = get_one_page_url(response.text, args)
        if not url_list:
            continue
        mail_list.extend(url_list)
    return mail_list



def main():
    global user
    global sessrequ

    username = "740954235@qq.com"
    password = "Tessie1126"
    user  =  username.split('@')[0]
    qqobj = QQEmailLogin(username, password, dtype='chrome')
    cookie   = qqobj.cookie
    host_url = qqobj.host_url
    print(host_url)

    # step1: get sid, folderid, folderkey, header
    sid = get_sid(host_url)
    if not sid:
        print("get sid failed!!!")
        return
    para = {'referer': 'https://mail.qq.com/cgi-bin/frame_html?sid=%s'%sid}
    headers = get_headers(cookie, para)
    write_data_file(headers, fpath='./output/%s/qqmail_login.json'%user , ftype='json')


    # step2: By cookie, requests qq mail main_page
    sessrequ = requests.session()
    response = sessrequ.get(host_url, headers=headers)    # get qqmail main html
    if str(response.status_code)[0] != '2':
        print("request failed!!")
        return
    write_data_file(response.text, fpath='./output/%s/qqmail_main_page.html'%user, ftype='html')


    # step3: 解析出邮件主页导航栏中每一类别邮件的URL
    dirs = get_mail_dirs(response.text)
    pprint.pprint(dirs)


    # step4: 分别获取每类邮件列表中的邮件URL
    all_mail_list = []
    for url in dirs:
        args = get_url_args(url, sid)
        mail_list = analy_page_list(url, headers, args)
        if not mail_list:
            continue

        # qvchong
        for item in mail_list:
            if item not in all_mail_list:
                all_mail_list.append(item)
            else:
                pass
    print("all maillist len: ", len(all_mail_list))


    # step5: 请求每个邮件
    mailpage = sessrequ.get(all_mail_list[0], headers=headers)
    if str(mailpage.status_code)[0] != '2':
        print("request failed!!")
        return
    tmp_mail_id = 1
    write_data_file(mailpage.text, fpath='./output/{}/eml/qqmail_emal_{}.eml'.format(user, tmp_mail_id))



if __name__ == '__main__':
    main()