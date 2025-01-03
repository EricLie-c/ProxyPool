import time
from multiprocessing import Process
from WebAPI import app
from Getter import Getter
from CrawlerDetection import Tester

TESTER_CYCLE = 20
GETTER_CYCLE = 20
TESTER_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = True
API_HOST = 'localhost'
API_PORT = '5555'


class Runner(object):
    def run_tester(self, cycle=TESTER_CYCLE):
        """
        定时测试代理
        :param cycle:
        :return: None
        """
        tester = Tester()
        while True:
            print('测试器开始运行')
            tester.run()
            time.sleep(cycle)

    def run_getter(self, cycle=GETTER_CYCLE):
        """
        定时获取代理
        """
        getter = Getter()
        while True:
            print('开始抓取代理')
            getter.run()
            time.sleep(cycle)

    def run_api(self):
        """
        开启API
        """
        app.run(API_HOST, API_PORT)

    def run(self):
        # 多进程分别执行对应的检测、爬取和维护webapi的任务
        print('代理池开始运行')
        if TESTER_ENABLED:
            tester_process = Process(target=self.run_tester)
            tester_process.start()

        if GETTER_ENABLED:
            getter_process = Process(target=self.run_getter)
            getter_process.start()

        if API_ENABLED:
            api_process = Process(target=self.run_api)
            api_process.start()


if __name__ == '__main__':
    runner = Runner()
    runner.run()
