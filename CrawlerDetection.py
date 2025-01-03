import asyncio
import time

import RedisController
import aiohttp

valid_status_codes = [200]
test_url = 'https://www.baidu.com'
batch_test_size = 100


class Tester(object):
    def __init__(self):
        self.redis = RedisController.RedisClient()

    async def test_single_proxy(self, proxy):
        """
        测试单个代理
        :param proxy: 单个代理
        :return: None
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'https://' + proxy
                print('正在测试', proxy)
                # 这下面的操作有点像用winhttpapi的流程。当然更加方便
                # session.get是个异步请求，其内部是有await的，因此也会将控制权交还给事件循环，从而进行协程的切换
                async with session.get(test_url, proxy=real_proxy, timeout=15) as response:
                    if response.status in valid_status_codes:
                        self.redis.max(proxy)
                        print('代理可用', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应码不合法', proxy)
            except (ConnectionError, TimeoutError, AttributeError, Exception):
                self.redis.decrease(proxy)
                print('代理请求失败', proxy)

    def run(self):
        """
        测试主函数
        :return:None
        """
        print('测试器开始运行')
        # 这部分其实可以用asyncio.gather重写
        try:
            proxies = self.redis.all()
            # 检查有无事件循环，如果无则创建
            loop = asyncio.get_event_loop()
            for i in range(0, len(proxies), batch_test_size):
                test_proxies = proxies[i:i + batch_test_size]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                # await只能在协程内部使用，等待某个协程执行完毕。同时控制权会转交回事件循环
                # wait是接收一组协程，并等待执行完毕。也可以指定条件，是FIRST_COMPLETED还是ALL_COMPLETED等
                # run_until_complete是等待指定的协程执行完毕 一般在主线程中使用，以启动事件循环并运行单个协程
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误', e.args)
