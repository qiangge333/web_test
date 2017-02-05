from jinja2 import Environment, FileSystemLoader
import os.path
import time


log_config = {
    'file': 'log.gua.text'
}


def set_time():
    format = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    return dt


def set_log_path():
    format = '%Y%m%d%H%M%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    path = 'logs/log.gua.{}.text'.format(dt)
    log_config['file'] = path


def log(*args, **kwargs):
    dt = set_time()
    path = log_config.get('file')
    if path is None:
        set_log_path()
        path = log_config.get('file')
    # 中文 windows 平台默认打开的文件编码是 gbk 所以需要指定一下
    with open(path, 'a', encoding='utf-8') as f:
        # 通过 file 参数可以把输出写入到文件 f 中
        # 需要注意的是 **kwargs 必须是最后一个参数
        print(dt, *args, file=f, **kwargs)


# __file__ 就是本文件的名字
# 得到用于加载模板的目录
path = '{}/templates/'.format(os.path.dirname(__file__))
# 创建一个加载器, jinja2 会从这个目录中加载模板
loader = FileSystemLoader(path)
# 用加载器创建一个环境, 有了它才能读取模板文件
env = Environment(loader=loader)


def template(path, **kwargs):
    """
    本函数接受一个路径和一系列参数
    读取模板并渲染返回
    """
    t = env.get_template(path)
    return t.render(**kwargs)


def error(request, code=404):
    """
    根据 code 返回不同的错误响应
    目前只有 404
    """
    # 之前上课我说过不要用数字来作为字典的 key
    # 但是在 HTTP 协议中 code 都是数字似乎更方便所以打破了这个原则
    e = {
        404: b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')
