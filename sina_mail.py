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
pwd = os.path.dirname(os.path.realpath(__file__))           #pwd2 = sys.path[0]
# pardir = os.path.abspath(os.path.join(pwd, os.pardir))
sys.path.append(pwd)
from selenium_login import SinaEmailLogin
reload(sys)
sys.setdefaultencoding('utf8')


class SinaMail(object):
    def __init__(self, username, cookie, dpath):
        self.user   =  username.split('@')[0]
        self.header = self._get_header(cookie)
        self.fpath  = self._get_path(dpath)
        self.mySession = requests.session()
        self._save_data(self.header, 'sinamail_login.json', ftype='json')


    def _get_header(self, cookie=None, para=None):
        header  = {}
        if cookie:
            header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
            header['Cookie'] = cookie
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


    def get_mail_dir_list(self):
        url = 'http://m0.mail.sina.com.cn/wa.php?a=list_folder&calltype=auto'
        try:
            res = self.mySession.get(url, headers=self.header)
            if str(res.status_code)[0] != '2':
                print("request failed!!")
                return None

            res_data = res.text
            if res_data.find('data') == -1 and res_data.find('id')  ==-1:
                return None

            res_loads = json.loads(res_data)                           # to dic
            self._save_data(res_loads, 'sinamail_main_page.json', ftype='json')

            id_data = res_loads['data']
            id_list = [item['id'] for item in id_data]
            return id_list if id_list else None
        except Exception as e:
            return None


    def get_one_box_mail(self, fid):
        box_url = 'http://m0.mail.sina.com.cn/wa.php?a=list_mail'
        para = {'Origin': 'http://m0.mail.sina.com.cn',
                'Referer':'http://m0.mail.sina.com.cn/classic/index.php',
                'Host':'m0.mail.sina.com.cn'}
        header = self._get_header(para=para)
        page = 1
        one_box_mails = []
        while True:
            postdata =  {'fid':'%s'%fid, 'order':'htime', 'sorttype':'desc', 'type':0, 'pageno':'%d'%page, 'tag':-1, 'webmail':1}
            res = self.mySession.post(box_url, headers=header, data = postdata)
            res_loads = json.loads(res.text)
            if not res_loads['data']['maillist']:
                break
            self._save_data(res_loads, 'sinamail_box_{}.json'.format(page), ftype='json')

            for item in res_loads['data']['maillist']:
                one_box_mails.append((item[0], item[3], item[4], fid))
            page += 1
        one_box_mails.reverse()
        news_ids = []

        # qvchong
        for item in one_box_mails:
            if item not in news_ids:
                news_ids.append(item)
        return news_ids


    def get_mail_page(self, para):
        try:
            url_para = para[0]
            mid  = url_para[0]
            fid  = url_para[-1]
            num  = para[1]
            url  = 'http://m0.mail.sina.com.cn/classic/readmail.php?webmail=1&fid={}&mid={}&ts=17644'.format(fid, mid)
            para = {'Referer':'http://m0.mail.sina.com.cn/classic/index.php',
                    'Host':'m0.mail.sina.com.cn'}
            header = self._get_header(para=para)
            res = self.mySession.get(url, headers=header, timeout=30, stream=True)
            if str(res.status_code)[0] != '2':
                print('request failed!!')
                return

            res_data = res.text
            res_loads = json.loads(res_data)                      # to dic
            if not res_loads['result']:
                return
            self._save_data(res_loads, 'eml/sinamail_emal_{}.json'.format(num), ftype='json')   #note: eml/ ,not /emlm
        except Exception as e:
            print(e)
            return


def main():
    username = 'xxxxxxxx@sina.com'
    password = 'xxxxxxxx'
    fpath    = './output'

    # selenium get  sina login cookie
    loginObj = SinaEmailLogin(username, password, dtype='chrome')    # chrome, firefox
    cookie   = loginObj.cookie
    host_url = loginObj.host_url
    if not cookie:
        print('Get Cookie Failed!!')
        sys.exit(1)

    # get sina Mail object,
    sObj = SinaMail(username, cookie, fpath)
    id_list = sObj.get_mail_dir_list()
    if not id_list:
        print('id_list is None')
        sys.exit(1)


    if 'all' in id_list:
        fid = 'all'
        one_box_mails = sObj.get_one_box_mail(fid)

        num  = len(one_box_mails)
        nums = range(1, num+1)
        print('all maillist len: %d'%num)

        pool = Pool(20)
        pool.map(sObj.get_mail_page, zip(one_box_mails, nums))
        pool.close()
        pool.join()


def test():
    username = 'xxxxxxxx@sina.com'
    password = 'xxxxxxxx'
    fpath    = './output'

    cookie  = 'afasfasfs'
    sObj = SinaMail(username, cookie, fpath)



if __name__ == '__main__':
    main()
    # test()