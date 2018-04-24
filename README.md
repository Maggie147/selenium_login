#  selenium login [python 2.7]

## 相关环境参数:
* python2.7, selenium(3.8.1)
* [selenium](https://pypi.org/project/selenium/#history)选择对应版本，查看相关信息。
* Google Chrome Version 64.0.3282.119(64位)/chromedriver_win32.zip。
* Firefox Version 58.0（64位）/geckodriver-v0.19.1-win64.zip。

## 项目主要功能介绍：
* 1、selenium_login.py 通过selenium登录邮箱并获取登录的cookie数据(包括：QQ邮箱、sina邮箱)
* 2、主要通过 re 解析页面
* 3、分别获取每类邮箱链接，再获取该类别下的邮件。
* 4、主要数据目录结构, 在主程序`qqmail.py` 同目录下的`output`下。
	```
	output
	|
	|___邮箱账号1
	|        |
	|        |___eml[保存的邮件]
	|        |
	|        页面.html及其他文件
	|        ...
	|
	|___邮箱账号2
	|        |
	|        |___eml[保存的邮件]
	|        |
	|        页面.html及其他文件
	|        ...
	...
	```


## selenium 安装
	```
	pip install -U selenium
	```
（可能第一次不会成功，需要多尝试几次）

## selenium-webdriver 驱动下载
* 下载相关驱动保存在代码主目录下的'driver'下。
* 火狐浏览器驱动[下载](https://github.com/mozilla/geckodriver/releases/)。
* [chrome浏览器驱动](https://sites.google.com/a/chromium.org/chromedriver/downloads)[下载](http://chromedriver.storage.googleapis.com/index.html)。
* IE浏览器驱动[下载](https://selenium-release.storage.googleapis.com/index.html)* 火狐浏览器驱动[下载](https://github.com/mozilla/geckodriver/releases/)。
* [chrome浏览器驱动](https://sites.google.com/a/chromium.org/chromedriver/downloads)[下载](http://chromedriver.storage.googleapis.com/index.html)。
* IE浏览器驱动[下载](https://selenium-release.storage.googleapis.com/index.html)。

selenium-webdriver相关驱动下载来源：
* https://seleniumhq.github.io/selenium/docs/api/javascript/index.html
* https://pypi.org/project/selenium/3.8.1/

## 运行脚本
	```
	python qq_mail.py
	python sina_mail.py
	```
