from flask import Flask, g
from RedisController import RedisClient

# 是一个特殊的模块级变量，定义了导入该模块时，需要导入那些符号
# 是一个列表，包含了希望用户可以直接访问的名称
# 相当于定义了一个对外的接口
__all__ = ['app']
# 定义flask实例。一个轻量级的python web框架
# 提供了基础的路由、请求处理、模版渲染等功能
# 很像springboot的web部分
app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'redis'):
        g.redis = RedisClient()
    return g.redis


@app.route('/')
def welcome():
    return '<h2>Welcome to My Proxy Pool System</h2>'


@app.route('/random')
def get_proxy():
    """
    获取随机可用代理
    :return: 随机代理
    """
    conn = get_conn()
    return conn.random()


@app.route('/count')
def get_counts():
    """
    获取代理池总量
    :return: 代理池总量
    """
    conn = get_conn()
    return str(conn.count())


if __name__ == '__main__':
    app.run()


