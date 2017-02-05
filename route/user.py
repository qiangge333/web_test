from models import User
from utlis import log
from utlis import template
from . import response_with_headers
from . import redirect
from .session import session


import random


def random_str():
    seed = '`~!@#$%^&*()_+-=|\[]{};:,.<>?/ 0123456789 AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
    s = ''
    for i in range(32):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def current_user(request):
    session_id = request.cookies.get('user', '')
    uid = session(session_id)
    if uid is not None:
        u = User.find(uid)
        return u
    else:
        return None


def username_for_user(request):
    username = '游客'
    u = current_user(request)
    if u is not None:
        username = u.username
    return username


def route_index(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    # username = username_for_user(request)
    # body = body.replace('{{username}}', username)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def route_login(request):
    """
    页面登录路由
    """
    headers = {
        'Content-Type': 'text/html'
    }
    if request.method == 'POST':
        form = request.form()
        u = User(form)
        if u.validate_login():
            user = User.find_by(username=u.username)
            session_id = random_str()
            session(session_id, user.id)
            headers['Set-Cookie'] = 'user={}'.format(session_id)
            log('session: ', session)
            return redirect('/todo/', headers)
        else:
            result = '用户名或密码错误'
    else:
        result = ''
    body = template('login.html', result=result)
    header = response_with_headers(headers)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def route_register(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    if request.method == 'POST':
        form = request.form()
        u = User(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(u.all())
        else:
            result = '用户名或密码长度必须大于2'
    else:
        result = ''
    body = template('register.html', result=result)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def profile(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('profile.html')
    user = current_user(request)
    if user is None:
        user = '非登录用户'
    body = body.replace('{{user}}', str(user))
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def route_static(request):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n\r\n'
    filename = request.query.get('file', 'dog.gif')
    path = 'static/{}'.format(filename)
    with open(path, 'rb') as f:
        body = f.read()
        img = header + body
        return img

route_dict = {
    '/': route_index,
    '/static': route_static,
    '/login': route_login,
    '/register': route_register,
    '/profile': profile,
}
