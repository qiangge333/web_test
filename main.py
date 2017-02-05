import socket
import urllib.parse

from route.user import route_dict as route_users
from route.todo import route_dict as route_todos
from route.tweet import route_dict as route_tweets
from route.comment import route_dict as route_comments
from route.session import load_session
from utlis import log
from utlis import error


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def reset(self):
        self.__init__()

    def add_headers(self, header):
        """
        Accept-Language: zh-CN,zh;q=0.8
        Cookie: height=169; user=gua
        """
        # lines = header.split('\r\n')
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        self.add_cookies()

    def add_cookies(self):
        """
        height=169; user=gua
        """
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        args = body.split('&')
        form = {}
        for arg in args:
            k, v = arg.split('=')
            form[k] = v
        return form


request = Request()


def parsed_path(path):
    """
    message=hello&author=gua
    {
        'message': 'hello',
        'author': 'gua',
    }
    """
    i = path.find('?')
    if i == -1:
        path = path
        query = {}
    else:
        path, query_string = path.split('?')
        args = query_string.split('&')
        log('query', args)
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
    return path, query


def register_route(base_routes, routes, prefix=''):
    routes = {prefix + k: v for k, v in routes.items()}
    base_routes.update(routes)


def response_for_path(path):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    path, query = parsed_path(path)
    request.path = path
    request.query = query
    routes = {}
    # 导入route
    routes.update(route_users)
    routes.update(route_todos)
    routes.update(route_tweets)
    routes.update(route_comments)
    # register_route(routes, route_comments, '/comment')
    #
    response = routes.get(path, error)
    return response(request)


def run(host='', port=3000):
    """
    启动服务器
    """
    # 载入 session
    load_session()
    # 初始化 socket 套路
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    print('start at', '{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环来处理请求
        while True:
            # 监听 接受 读取请求数据 解码成字符串
            s.listen(3)
            connection, address = s.accept()
            # 用 while 循环全部 recv
            r = b''
            buffer_size = 1024
            while True:
                r1 = connection.recv(buffer_size)
                r += r1
                if len(r1) < buffer_size:
                    break
            # 循环结束
            r = r.decode('utf-8')
            # log('ip and request, {}\n{}'.format(address, request))
            # 因为 chrome 会发送空请求导致 split 得到空 list
            # 所以这里判断一下防止程序崩溃
            if len(r.split()) < 2:
                continue
            # log('完整请求')
            # log(r.replace('\r\n', '\n'))
            # log('请求结束')
            path = r.split()[1]
            #重置 request类的属性为空
            request.reset()
            # 设置 request 的 method
            request.method = r.split()[0]
            # 把 body 放入 request 中
            request.body = r.split('\r\n\r\n', 1)[1]
            request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
            # 用 response_for_path 函数来得到 path 对应的响应内容
            response = response_for_path(path)
            log('path and query:', request.path, request.query)
            # 把响应发送给客户端
            connection.sendall(response)
            # log('完整响应')
            # try:
            #     log(response.decode('utf-8').replace('\r\n', '\n'))
            # except Exception as e:
            #     log('异常', e)
            # log('响应结束')
            connection.close()


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='',
        port=3000,
    )
    # 如果不了解 **kwargs 的用法, 上过基础课的请复习函数, 新同学自行搜索
    run(**config)
