"""
要写多线程爬虫，第一步是建立自己的代理池
为了建立代理池，必须要先考虑如何有效存储
为了实现存储，利用Redis作为数据库
为了实现爬取的IP不重复，使用有序集合作为数据结构
集合名即为proxies，键为Ip，值为分数
分数用来排序，从而能够选取到爬取的最佳代理
"""

max_score = 100
min_score = 0
initial_score = 10
redis_host = 'localhost'
redis_port = 6379
redis_password = None  # 相当于null
redis_key = "proxies"

import redis
from random import choice


class PoolEmptyError(Exception):
    """代理池空错误"""
    def __init__(self, message):
        self.message = message

    # print的时候会自动调用该方法
    def __str__(self):
        return f"[Error]: {self.message}"


class RedisClient(object):
    def __init__(self, host=redis_host, port=redis_port, password=redis_password):
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        # 设置为true代表从服务器返回的数据解析为字符串（通常为utf-8编码），否则为字节数据

    def add(self, proxy, score=initial_score):
        """
        添加代理，设置分数为最高。
        这样可以保证所有可用代理有更大的机会被获取到
        当检测到代理不可用时，将分数减 1，减至 0 后移除，一共 100 次机会，
        也就是说当一个可用代理接下来如果尝试了 100 次都失败了，就一直减分直到移除，一旦成功就重新置回 100，
        尝试机会越多代表将这个代理拯救回来的机会越多，这样不容易将曾经的一个可用代理丢弃，
        因为代理不可用的原因可能是网络繁忙或者其他人用此代理请求太过频繁，所以在这里设置为 100 。
        :param proxy: 代理名
        :param score: 分数
        :return: 添加结果（成功与否）
        """
        # zscore 方法用于获取有序集合（sorted set）中特定成员的分数（score）。
        # 有序集合是一种用于存储一组唯一元素，且每个元素都有一个关联的浮点数分数的数据结构。
        # 根据分数，元素会被自动排序。
        if not self.db.zscore(redis_key, proxy):
            return self.db.zadd(redis_key, {proxy: score})

    def random(self):
        """
        随机获取有效代理
        先看看有无满分代理，然后再按排名获取
        :return: 随机代理
        """
        # 若有withscore=true参数则返回元组列表，否则一般列表
        result = self.db.zrangebyscore(redis_key, max_score, max_score)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrange(redis_key, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError

    def decrease(self, proxy):
        """
        代理的分数衰减处理函数
        :param proxy: 代理
        :return: 衰减后的分数
        """
        score = self.db.zscore(redis_key, proxy)
        if score > min_score:
            print('代理IP: ', proxy, '当前分数: ', score, '- 1')
            return self.db.zincrby(redis_key, -1, proxy)
        else:
            print('代理IP: ', proxy, '当前分数: ', score, ', 移除')
            return self.db.zrem(redis_key, proxy)

    def exists(self, proxy):
        """判断是否已存在该代理"""
        return not self.db.zscore(redis_key, proxy) is None

    def max(self, proxy):
        """
        将代理设置为max_score
        :param proxy:
        :return: 设置后的分数
        """
        print('代理IP: ', proxy, '可用，设置分数为: ', max_score)
        return self.db.zadd(redis_key, {proxy: max_score})

    def count(self):
        """
        获取代理池的IP总数
        :return: 数量
        """
        return self.db.zcard(redis_key)

    def all(self, withscores=False):
        """
        获取全部代理的列表
        使用参数withscore则会把对应分数也返回
        默认不使用
        :return:
        """
        return self.db.zrangebyscore(redis_key, min_score, max_score, withscores=withscores)
