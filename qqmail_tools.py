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
import requests
# sys.path.append('./')
reload(sys)
sys.setdefaultencoding('utf8')


def get_headers(cookie=None, para=None):
    header = {}
    header['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"
    if cookie:
        header['Cookie'] = cookie
    if para:
        header.update(para)
    return header

# get_sid
def get_sid(buf, head_str='?sid=', tail_str='&'):
    sid = ''
    try:
        begin = buf.find(head_str)
        if begin:
            if tail_str:
                end = buf[begin+len(head_str):].find(tail_str)
                if end:
                    sid = buf[begin+len(head_str): begin+len(head_str)+end]
                else:
                    sid = buf[begin+len(head_str):]
            else:
                sid = buf[begin+len(head_str):]
        else:
            print("no find head_str")
    except Exception as e:
        print(e)
    return sid

# get sid, folderid, folderkey
def get_url_args(buf, sid):
    args = {'sid': '', 'folderid':'', 'folderkey':''}
    args['sid'] = sid
    try:
        folderid = get_sid(buf, 'folderid=', '&')
        args['folderid'] = folderid if len(folderid) < 4 else ''
    except Exception as e:
        args['folderid'] = '1'
    try:
        folderkey = get_sid(buf, 'folderkey=', '&')
        args['folderkey'] = folderkey if len(folderkey) < 4 else ''
    except Exception as e:
        folderkey = ''
    return args


# 解析出邮件主页导航栏中每一类别邮件的URL
def get_mail_dirs(buf):
    try:
        dirs = []
        restr = r'<ul.*?class="fdul">(.*?)</ul>'
        ret = re.findall(restr, buf, re.S | re.M)
        if not ret:
            print("Step1: get mail dirs failed!!")
            return None
        restr = r'<li id="folder_.*?<a id="folder.*?href="(.*?)"'
        folders = re.findall(restr, str(ret), re.S | re.M)
        if not folders:
            print("Step2: get mail dirs failed!!")
            return None
        dirs = ['http://mail.qq.com' + item.strip() for item in folders if item]
        return dirs
    except Exception as e:
        print(e)
        return None



# 解析每类邮件主页 显示的邮件页数，无法获取页数或者页数为0，该类中没有邮件
def mail_page_cnt(buf):
    restr = r'<div.*?class="right">.*?<script.*?document\.write\((.*?)\);</script>'
    ret = re.findall(restr, buf, re.S | re.M)
    if not ret:
        print("mail_page_cnt  match Failed!!")
        return None
    pagelist = str(ret[0]).split('+')
    # print("pagelist", pagelist)
    try:
        page = int(pagelist[0].strip())+ int(pagelist[1].strip())
        return page
    except Exception as e:
        print("mail_page_cnt page add error!!!")
        return None



# 解析每类邮件列表页面
def get_one_page_url(buf, args):
    url_list = []
    # restr = r'<td\s+hitmailid\s+onclick="getTop\(\)\.RD\(event,\'(.*?)\',(.*?),.*?\);"\s+class=".*?">'
    restr = r'<div\s+id="div_.*?class="toarea"\s+group_id=".*?">(.*?)</div>'
    ret = re.findall(restr, buf, re.S | re.M)
    if not ret:
        print("Step1: get one page url Failed!!")
        return None
    for item in ret:
        restr = r'<td.*?hitmailid.*?onClick="getTop\(\)\.RD\(event,\'(.*?)\',.*?;".*?>'
        mailid_list = re.findall(restr, buf, re.S | re.M)
        if not mailid_list:
            print("Step2: get one page url Failed!!")
            continue
        for mailid_tmp in mailid_list:
            mailid = mailid_tmp
            url_tmp = 'http://mail.qq.com/cgi-bin/readmail?folderid={}&folderkey={}&t=readmail&mailid={}&mode=pre&maxage=3600&base=12.9&ver=14705&sid={}'.format(
                args['folderid'], args['folderkey'], mailid, args['sid'])
            url_list.append(url_tmp)
    return url_list


def write_data_file(buf, fpath, ftype=None):
    try:
        path = os.path.split(fpath)[0]
        if not os.path.exists(path):
            os.makedirs(path)
        if ftype == 'json':
            with open(fpath, 'w') as fjson:
                json.dump(buf, fjson)
        elif ftype == 'html':
            with open(fpath, 'w') as fhtml:
                fhtml.write(buf.encode('gbk', 'ignore'))
        else:
            with open(fpath, 'w') as fp:
                fp.write(buf.encode('gbk', 'ignore'))
    except Exception as e:
        print(e)


def get_file_data(fpath, ftype=None):
    try:
        if ftype == 'json':
            with open(fpath, 'r') as fjson:
                buf = json.load(fjson)
        elif ftype == 'html':
            with open(fpath, 'r') as fhtml:
                buf = fhtml.read()
        else:
            with open(fpath, 'r') as fp:
                buf = fp.read()
        return buf
    except Exception as e:
        print(e)
        return None


def test():
    global user
    user = '740954235'

    # 解析出邮件主页导航栏中每一类别邮件的URL
    buff = get_file_data(fpath='./output/%s/qqmail_main_page.html'%user)
    if buff:
        dirs = get_mail_dirs(buff)
        pprint.pprint(dirs)
        print('Test1: Analyse qqmail_main_page, get mail_list END.\n')


    # 获取sid, folderid, folderkey
    url = "'http://mail.qq.com/cgi-bin/mail_list?sid=rdbiSloWkLpjfVEL&folderid=1&page=0&s=inbox&showinboxtop=1&loc=folderlist,,,1"
    sid = get_sid(url)
    args = get_url_args(url, sid)
    if url:
        print("sid: ", sid)
        pprint.pprint(args)
        print('Test2: Analyse URL, get sid, folderid, folderkey END.\n')


    # 获取登录保存的 header: cookie, referer
    header = get_file_data(fpath='./output/%s/qqmail_login.json'%user, ftype='json')
    pprint.pprint(header)
    print('Test3: get login cookie END.\n')


    # 解析每类邮件主页（分页数，邮件URL列表）
    mbuf = get_file_data(fpath='./output/%s/maillist_page1.html'%user)
    if mbuf:
        # 每一类邮件主页中,获取该类邮件分页数
        cnt  = mail_page_cnt(mbuf)
        print("cnt: ", cnt)

        # 每一类邮件中，邮件URL列表
        url_list = get_one_page_url(mbuf, args)
        pprint.pprint(url_list)
        print("url_list:", len(url_list))
        print('Test4: Analyse per_category mail_page, get mail_list(url_list) END.\n')

        # test requests mail_url
        if header:
            test_url = url_list[0]
            mailpage = requests.get(test_url, header)
            if str(mailpage.status_code)[0] != '2':
                print("request failed!!")
            else:
                write_data_file(mailpage.text, fpath='./output/{}/eml/qqmail_emal_test.eml'.format(user))
            print("URL: ", test_url)
            print('Test5: requests mail_url END.\n')




if __name__ == '__main__':
    test()