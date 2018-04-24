#coding=utf-8
'''
    @File    test  qq_mail.py
    @Author  tx
    @Created On 2018-04-20
    @Updated On 2018-04-24
'''
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
pwd = os.path.dirname(os.path.realpath(__file__))           #pwd2 = sys.path[0]
# pardir = os.path.abspath(os.path.join(pwd, os.pardir))
from selenium_login import QQEmailLogin
reload(sys)
sys.setdefaultencoding('utf8')


def get_value(buf, head_str='?sid=', tail_str='&'):
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


def get_file_data(fpath, ftype=None):
    try:
        if ftype == 'json':
            with open(fpath, 'r') as fjp:
                buf = json.load(fjp)
        else:
            with open(fpath, 'r') as fp:
                buf = fp.read()
        return buf
    except Exception as e:
        print(e)
        return None


class QQMail(object):
    def __init__(self, username, hosturl, cookie, dpath):
        self.user   =  username.split('@')[0]
        self.sid    = self._get_sid(hosturl)
        self.header = self._get_header(cookie)
        self.fpath  = self._get_path(dpath)
        self.mySession = requests.session()
        self._save_data(self.header, 'qqmail_login.json', ftype='json')

    def _get_header(self, cookie=None, para=None):
        header  = {}
        if cookie:
            header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
            header['referer'] = 'https://mail.qq.com/cgi-bin/frame_html?sid=%s'%self.sid
            header['Cookie']  = cookie
        if para:
            header.update(self.header)
            header.update(para)
        return header

    def _get_path(self, dpath):
        path = os.path.realpath(dpath)
        mypath = os.path.join(path, self.user)
        if not os.path.exists(mypath):
            os.makedirs(mypath)
        return mypath

    def _save_data(self, buf, fname, ftype=None):
        try:
            fullpath = os.path.join(self.fpath, fname)
            path = os.path.split(fullpath)[0]
            if not os.path.exists(path):
                os.makedirs(path)
            if ftype == 'json':
                with open(fullpath, 'w') as fjp:
                    json.dump(buf, fjp)
            else:
                with open(fullpath, 'w') as fp:
                    fp.write(buf.encode('gbk', 'ignore'))
            return True
        except Exception as e:
            print(e)
            return False

    def _get_sid(self, buf):
        sid = get_value(buf, head_str='?sid=', tail_str='&')
        if not sid:
            print('not get sid!')
            sys.exit(1)
        return sid

    # get sid, folderid, folderkey
    def _get_url_args(self, buf):
        args = {'sid': '', 'folderid':'', 'folderkey':''}
        args['sid'] = self.sid
        try:
            folderid = get_value(buf, 'folderid=', '&')
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
    def _analyse_mail_dirs(self, buf):
        try:
            dirs = []
            restr = r'<ul.*?class="fdul">(.*?)</ul>'
            ret = re.findall(restr, buf, re.S | re.M)
            if not ret:
                print("Step1: _analyse_mail_dirs failed!!")
                return None
            restr = r'<li id="folder_.*?<a id="folder.*?href="(.*?)"'
            folders = re.findall(restr, str(ret), re.S | re.M)
            if not folders:
                print("Step2: _analyse_mail_dirs failed!!")
                return None
            dirs = ['http://mail.qq.com' + item.strip() for item in folders if item]
            return dirs
        except Exception as e:
            print(e)
            return None


    # 解析每类邮件主页 显示的邮件页数
    def _get_page_cnt(self, buf):
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

    # 解析每类邮件，邮件URL
    def _get_one_page_url(self, buf, args):
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

            for mailid in mailid_list:
                # url_tmp = 'http://mail.qq.com/cgi-bin/readmail?folderid={}&folderkey={}&t=readmail&mailid={}&mode=pre&maxage=3600&base=12.9&ver=14705&sid={}'.format(
                #     args['folderid'], args['folderkey'], mailid, args['sid'])
                url_args = {}
                url_args['mailid'] = mailid
                url_args.update(args)
                url_list.append(url_args)
        return url_list


    # 请求主页，获取主页导航栏中每一类别邮件的URL
    def get_mail_dir_list(self, hosturl):
        try:
            res = self.mySession.get(hosturl, headers=self.header)
            if str(res.status_code)[0] != '2':
                print("request qqmail main_page failed!!")
                return None
            self._save_data(res.text, 'qqmail_main_page.html')

            dirs = self._analyse_mail_dirs(res.text)
            return dirs if dirs else None
        except Exception as e:
            return None


    # 获取每一类邮件中，邮件URL
    def get_one_box_mail(self, url):
        args = self._get_url_args(url)

        res = self.mySession.get(url, headers=self.header)              # 请求每一类邮件main html
        if str(res.status_code)[0] != '2':
            print("request get_one_box_mail failed!!")
            return None
        res_data = res.text
        self._save_data(res_data, 'maillist_page{}.html'.format(args['folderid']))

        # 获取每类邮件主页中显示的邮件页数 (无法获取页数或者页数为0，则该类中没有邮件)
        cnt = self._get_page_cnt(res_data)
        if not cnt:
            return None

        mail_list = []
        # for i in range(0, cnt+1):
        for i in range(1):
            url_list = self._get_one_page_url(res_data, args)
            if not url_list:
                continue
            mail_list.extend(url_list)

        return mail_list


    def get_mail_page(self, para):
        try:
            url_args = para[0]
            folderid  = url_args['folderid']
            folderkey = url_args['folderkey']
            mailid    = url_args['mailid']
            num = para[1]
            url = 'http://mail.qq.com/cgi-bin/readmail?folderid={}&folderkey={}&t=readmail&mailid={}&mode=pre&maxage=3600&base=12.9&ver=14705&sid={}'.format(
                        folderid, folderkey, mailid, self.sid)
            print(url)
            res = self.mySession.get(url, headers=self.header, timeout=30, stream=True)
            if str(res.status_code)[0] != '2':
                print("request per mail_page failed!!")
                return
            self._save_data(res.text, 'eml/qqmail_emal_{}.html'.format(num))   #note: eml/ ,not /emlm
        except Exception as e:
            print(e)
            return


def main():
    username = "740954235@qq.com"
    password = "Tessie1126"
    fpath    = './output'

    # selenium get  qq login cookie
    loginObj = QQEmailLogin(username, password, dtype='chrome')    # chrome, firefox
    cookie   = loginObj.cookie
    host_url = loginObj.host_url
    if not cookie:
        print('Get Cookie Failed!!')
        sys.exit(1)

    # get qq Mail object,
    qqObj = QQMail(username, host_url, cookie, fpath)
    dirs  = qqObj.get_mail_dir_list(host_url)
    if not dirs:
        print('dirs is None')
        sys.exit(1)

    all_mail_list = []
    for url in dirs:
        mail_list = qqObj.get_one_box_mail(url)
        if not mail_list:
            continue
        # qvchong
        for item in mail_list:
            if item not in all_mail_list:
                all_mail_list.append(item)
            else:
                pass

    num = len(all_mail_list)
    nums = range(1, num +1)
    print("all mail_list len: ", num)

    pool = Pool(20)
    pool.map(qqObj.get_mail_page, zip(all_mail_list, nums))
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()