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
import pprint
sys.path.append('./')

reload(sys)
sys.setdefaultencoding('utf8')


def get_headers(cookie=None, para):
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
def get_url_args(buf):
    args = {'sid': '', 'folderid':'', 'folderkey':''}
    sid = get_sid(buf)
    if not sid:
        return args
    try:
        args['folderid'] = get_sid(buf, 'folderid=', '&')
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
            url_tmp = 'http://mail.qq.com/cgi-bin/readmail?folderid={}&folderkey={}&t=readmail&mailid={}&mode=pre&maxage=3600&base=12.9&ver=14705&'.format(
                args['folderid'], args['folderkey'], mailid, args['sid'])
            url_list.append(url_tmp)
    return url_list




def write_data_file(buf, fpath, ftype):
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


def get_file_data(fpath, ftype):
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
    # 解析出邮件主页导航栏中每一类别邮件的URL
    buf = get_file_data(fpath='./output/page/qqmail_main.html')
    dirs = get_mail_dirs(buf)
    pprint.pprint(dirs)


    mail_cat = get_file_data(fpath='./output/page/maillist_page1.html', ftype='html')
    cnt = mail_page_cnt(mail_cat)
    print("cnt:", )

    mail_url = ""
    args = get_url_args(mail_url)

    url_list = get_one_page_url(mail_cat, args)
    pprint.pprint(url_list)
    print(len(url_list))



if __name__ == '__main__':
    test()