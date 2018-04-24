# -*- coding: utf-8 -*-
import requests
import re
import os
import json
from multiprocessing.dummy import Pool


class ProxyIPCheck(object):
    def __init__(self):
        self.proxy_addr = "http://www.gatherproxy.com/zh/"
        self.proxy_addr_xici = "http://www.xicidaili.com/nn/1"
        self.check_addr = "http://ip.chinaz.com/getip.aspx"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }

    def proxyIPGet(self):
        res = requests.get(self.proxy_addr, headers=self.headers, timeout=30)
        proxy_index = res.text
        proxy_rule = r'gp.insertPrx\((.*?)\)'
        proxy_json = re.findall(proxy_rule, proxy_index, re.S | re.M)
        proxy_ips = []
        for p in proxy_json:
            ip = json.loads(p)["PROXY_IP"]
            port = json.loads(p)["PROXY_PORT"]
            ip_info = "{ip}:{port}".format(ip=ip, port=int(port, 16))
            proxy_ips.append(ip_info)
        return proxy_ips


    def proxyIPGet_XiciDaili(self):                             # 西刺代理
        from bs4 import BeautifulSoup
        res = requests.get(self.proxy_addr_xici, headers=self.headers, timeout=30)
        proxy_index = res.text
        soup   = BeautifulSoup(proxy_index, 'lxml')
        ipList = soup.findAll('tr')
        proxy_ips = []
        for index in range(1, len(ipList)):
            item = ipList[index]
            tds  = item.findAll('td')
            ip_tmp   = tds[1].contents[0]                        # ip
            if ip_tmp.count('.') != 3:                           # simple check ip
                continue
            else:
                ip   = ip_tmp
            port_tmp = tds[2].contents[0]                        # port
            try:
                port = int(port_tmp)                             # simple check port
            except Exception as e:
                continue
            ip_info = "{ip}:{port}".format(ip=ip, port=port)
            proxy_ips.append(ip_info)
        return proxy_ips


    def __checkip(self, ip):
        proxies = {"http": "http://" + ip}
        s = requests.session()
        s.keep_alive = False
        try:
            res = s.get(self.check_addr, proxies=proxies, timeout=5)
            if "window.location" not in res.text:
                return ip
        except BaseException:
            pass

    def validIPGet(self, proxyinfo):
        thread = len(proxyinfo)
        pool = Pool(thread)
        ips = pool.map(self.__checkip, proxyinfo)
        pool.close()
        pool.join()
        ips = [i for i in ips if i]
        return ips


    def saveIP(self, ips, fpath, fname):
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        try:
            with open(fpath+fname, 'wb') as f:
                for i in ips:
                    f.write(i+'\r\n')
            return True
        except Exception as e:
            print(e)
            return False


def main():
    pObj = ProxyIPCheck()

    print("Gets ip list...")
    # proxyinfo = pObj.proxyIPGet()
    proxyinfo = pObj.proxyIPGet_XiciDaili()       # 西刺代理

    print("Check ip alive...")
    if len(proxyinfo) < 1:
        print("proxyIPGet failed!!")
        sys.exit(1)
    else:
        ips = pObj.validIPGet(proxyinfo)

        print("Save to proxyip.txt")
        ret = pObj.saveIP(ips, './proxy_file/', 'proxyip.txt')
        if not ret:
            print("Save to ./proxy_file/proxyip.txt failed!!!")


if __name__ == "__main__":
    main()