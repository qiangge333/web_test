from models import Tweet
from models import User
from utlis import log
from utlis import template
from utlis import error

from . import redirect
from .session import session


def current_user(request):
    session_id = request.cookies.get('user', '')
    uid = session(session_id)
    if uid is not None:
        u = User.find(uid)
        return u
    else:
        return None


def index(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    user_id = int(request.query.get('user_id'))
    user = User.find(user_id)
    log('user_id and user', user_id, type(user_id))
    if user is None:
        log('user is none')
        return error(request)
    tweets = Tweet.find_all(user_id=user_id)
    for t in tweets:
        t.load_comments()
    body = template('tweet_index.html', tweets=tweets, user=user)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def new(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('tweet_new.html')
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def add(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    # log('debug session_id and user_id', session_id, user_id)
    form = request.form()
    Tweet.new(form, user_id)
    return redirect('/tweet/index?user_id={}'.format(user_id))


def edit(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    id = int(request.query.get('id'))
    t = Tweet.find(id)
    body = template('tweet_edit.html', tweet=t)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def update(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    form = request.form()
    id = int(form.get('id'))
    t = Tweet.find(id)
    if t.user_id == user_id:
        Tweet.update(id, form)
    return redirect('/tweet/index?user_id={}'.format(user_id))


def delete(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    id = int(request.query.get('id'))
    # log('user_id and id: ', user_id, id)
    t = Tweet.find(id)
    if t.user_id == user_id:
        Tweet.delete(id)
    return redirect('/tweet/index?user_id={}'.format(user_id))


# 定义一个函数统一检测是否登录
def login_required(route_function):
    def func(request):
        u = current_user(request)
        # log('登录鉴定, u ', u)
        if u is None:
            # log('u is none')
            # 没登录 不让看 重定向到 /login
            return redirect('/login')
        else:
            # log('u is not NONE')
            # 登录了, 正常返回路由函数响应
            return route_function(request)
    return func

route_dict = {
    '/tweet/index': index,
    '/tweet/new': login_required(new),
    '/tweet/add': login_required(add),
    '/tweet/edit': login_required(edit),
    '/tweet/update': login_required(update),
    '/tweet/delete': login_required(delete),
}
