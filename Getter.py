from RedisController import RedisClient
from ProxiesCrawler import Crawler

pool_upper_threshold = 10000


class Getter(object):
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        """
        判断ip数量是否达到了上限
        :return: true or false
        """
        if self.redis.count() >= pool_upper_threshold:
            return True
        else:
            return False

    def run(self):
        """
        开始抓取
        :return:
        """
        print('获取器开始执行')
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                # 把每个爬取方法看做一个回调函数
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
                for proxy in proxies:
                    self.redis.add(proxy)



