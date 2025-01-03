import json
from pyquery import PyQuery as pq
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import base64
from lxml import etree


# 元类：用于在类的创建和定义阶段注入自定义逻辑，常用于框架和复杂的设计模式。
# 相当于类的装饰器
# 注意和基类的区别
# type是一切类的元类，所以最后还有返回执行type元类的构造方法
# 元类的意义在于可以在创建时添加或修改属性（比如下面就添加了crawlfunc属性），还可以实现强制接口（即确保所有子类实现特定的方法）
# 还有可以自动向某个注册中心登记该类
class ProxyMetaClass(type):
    # cls是元类本身，name是要创建的类名，bases是该类的基类元组，attrs是类属性的字典
    # 还可以定义init方法进一步初始化，如打印日志等
    # python中的类在声明/定义时即初始化。具体表现为：先调用元类的new方法，使用传递的名称、基类和属性来构造一个新的类对象，
    # 返回一个类对象的实例，再调用元类的init方法，对已有的类对象进行初始化
    # 在python中，一切皆对象，包括类本身也是。这与C++等不同。它的初始化并不需要等到创建实例对象时。
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        # items将字典转换为了迭代器。for循环隐含了next方法
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=ProxyMetaClass):
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0'
        }

    def get_proxies(self, callback):
        proxies = []
        # 看到这个eval，想起之前shell脚本也有这个函数，用来执行字符串中的函数
        # 利用这种方法，巧妙地执行所有回调函数。这样可以避免暴露爬取的细节？
        for proxy in eval("self.{}()".format(callback)):
            print('成功获取代理: ', proxy)
            proxies.append(proxy)
        return proxies

    def crawl_daili89(self, page_count=4):
        """
        爬取代理89的代理IP
        :param page_count: 页码 表示爬到这一页
        :return: 代理IP
        """

        start_url = 'http://www.89ip.cn/{}.html'  # 基准url， 字符串模版
        # 列表推导式
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            print('Crawling', url)
            html = requests.get(url=url, headers=self.header).text
            # pyquery 和 xpath都可以解析html，这里使用pyquery
            if html:
                doc = pq(html)
                # jquery风格。从doc中选取containerbox类，然后选取其中的表格，然后选取所有的行，并筛选索引大于0的
                # jQuery 是一个快速、小巧且功能丰富的 JavaScript 库。它使 HTML 文档的遍历和操作、事件处理、动画效果以及 Ajax 交互变得更加简单和高效。
                # jQuery 提供了一种简洁的方式来处理常见的 JavaScript 任务，降低了使用 JavaScript 编程的复杂性。
                trs = doc('.layui-form table tbody tr').items()
                for tr in trs:
                    # CSS选择器，利用nth-child伪类选择相对父类在特定位置的元素
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    # 生成器。有点像协程。一种特殊的迭代器。
                    # print 时用逗号分隔的默认用空格分开
                    # print(ip, ':', port, '\n')
                    # 生成器。有点像协程。一种特殊的迭代器。
                    yield ':'.join([ip, port])

    # def crawl_kuaidaili(self, page_count=4):
    #     """
    #     从快代理中爬取代理IP
    #     :param page_count: 页码
    #     :return: IP
    #     """
    #     start_url = 'https://www.kuaidaili.com/free/dps/{}'
    #     urls = [start_url.format(page) for page in range(1, page_count + 1)]
    #     for url in urls:
    #         print('Crawling', url)
    #         html = requests.get(url=url, headers=self.header).text
    #         # print(html)
    #         if html:
    #             doc = pq(html)
    #             # 无参text可以获得所有匹配的内容，而html只能获得第一个
    #             scripts = doc('script').text()
    #             # print(scripts)
    #             # 对于从js中提取数据，还是得用正则匹配。因为结构太松散了
    #             # re.compile(r'const fpsList = \[(.*?)\];', re.DOTALL)
    #             # 一次编译，可以多次使用
    #             pattern = re.compile(r'const fpsList = \[(.*?)\]', re.DOTALL)
    #             # 返回一个匹配对象
    #             match = pattern.search(scripts)
    #             # print(match)
    #             if match:
    #                 # 分组从1开始
    #                 # match是一个re.Match对象，类似于一个列表（但不是，不支持下标），从中提取出字符串
    #                 list_str = match.group(1)
    #                 # 将字符串转换为 Python 字典列表
    #                 # eval本质上是执行字符串的命令，也可以对字符串进行转化
    #                 # 此时的list_str是应该长字符串，逗号分割
    #                 # 字符串中有true，不透明，会报错，需要先转换
    #                 list_str = list_str.replace('true', 'True').replace('false', 'False')
    #                 fps_list = eval(list_str)
    #                 # 提取 IP 地址
    #                 ips = [item['ip'] for item in fps_list if 'ip' in item]
    #                 ports = [item['port'] for item in fps_list if 'port' in item]
    #                 for i in range(0, len(ips)):
    #                     yield ':'.join((ips[i], ports[i]))

    def specialcrawler_proxy_share(self, website='wikipedia'):
        """
        爬取proxy_share
        好处是稳定，坏处是只能访问特定网站，有访问控制（需要coockie），没法直接作代理
        :return: header（包含coockie） 和 url（供访问） 3h内有效
        用requests访问的话只有url是不够的，要加上coockie才能得到响应头的数据，才能得到响应载荷
        端口号都是443 https协议
        """
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 ' \
             'Safari/537.36 '
        header = {
            'User-Agent': ua,
        }
        url = 'https://www.a.cpfrx.info/_zh/'
        print('Crawling', url)
        option = webdriver.ChromeOptions()
        # 使用老版本的无头模式。新版本的由于驱动太老，导致不匹配，不完全无头，会弹出白框。
        # 同时，完全无头模式下必须设置disable_blink-features，否则也是会被检测到的
        option.add_argument("--headless=old")
        # selenium一样要设置浏览器代理
        option.add_argument(
            f'user-agent={ua}'
        )
        # 防止GPU硬件加速
        # option.add_argument("--disable-gpu")
        # 用于禁用 Chrome 的沙盒安全功能。沙盒是一种安全机制，有时在无头模式下可能会导致一些权限问题，因此可以禁用。
        # option.add_argument("--no-sandbox")
        # option.add_argument("--disable-dev-shm-usage")
        # 禁止使用自动化扩展（可以提供调试信息等额外功能），防止被检测到是自动化程序
        option.add_experimental_option('useAutomationExtension', False)
        # 排除自动化使能开关
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 禁用自动化控制的blink特性（浏览器渲染引擎，相当于html、js等的解释器），隐藏自动化特征
        option.add_argument("--disable-blink-features=AutomationControlled")

        browser = webdriver.Chrome(options=option)
        browser.get(url)
        # 定位到要悬停的元素
        above = browser.find_element(By.LINK_TEXT, "Wikipedia")
        # 对定位到的元素执行鼠标悬停操作
        actions = ActionChains(browser)
        actions.move_to_element(above)
        actions.double_click(above)
        actions.perform()
        time.sleep(8)
        temp_url = browser.current_url
        print(temp_url)
        pattern = re.compile('https://(.*?)/')
        response = requests.get(browser.current_url)
        # 接收响应头cookie信息
        headers = response.headers
        header['Cookie'] = headers['set-cookie']

        proxy = pattern.search(temp_url).group(1)

        website = 'https://www.' + website + '.com'
        # 编码成双字节数据
        website = website.encode('utf-8')
        # 编码成base64类型
        website = base64.b64encode(website)
        # 按双字节解码成单字节字符串
        website = website.decode('utf-8')

        url = 'https://' + proxy + f'/?__cpo={website}'

        return header, url

    def crawl_proxy_list(self):
        """
        爬取proxy_list
        :return: 代理ip
        """
        url = 'https://www.proxy-list.download/api/v2/get?l=en&t=http'
        print('Crawling', url)
        try:
            proxies = requests.get(url, headers=self.header).text
            # .是除了换行符外的任意字符dotall除外，*是匹配前面字符任意多次，？是采取贪婪原则
            ips = re.compile('"IP": "(.*?)", "PORT": ".*?", "ANON": "Elite"')
            ports = re.compile('"IP": ".*?", "PORT": "(.*?)", "ANON": "Elite"')
            ips = ips.findall(proxies)
            ports = ports.findall(proxies)
            for ip, port in zip(ips, ports):
                yield ':'.join([ip, port])
        except Exception:
            print('proxy_list爬取失败')







