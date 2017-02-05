from models import Comment
from models import User
from utlis import log
from utlis import template

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


def new(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    tid = int(request.query.get('tweet_id'))
    body = template('comment_new.html', tweet_id=tid)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def add(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    # log('debug session_id and user_id', session_id, user_id)
    form = request.form()
    Comment.new(form, user_id)
    tid = int(form.get('tweet_id'))
    return redirect('/tweet/index?user_id={}'.format(tid))


def edit(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    id = int(request.query.get('id'))
    t = Comment.find(id)
    body = template('tweet_edit.html', tweet=t)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def update(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    form = request.form()
    id = int(form.get('id'))
    # log('debug update: ', id, form, user_id)
    c = Comment.find(id)
    if c.tweet_id == user_id:
        Comment.update(id, form)
    return redirect('/tweet/index?user_id={}'.format(c.tweet_id))


def delete(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    id = int(request.query.get('id'))
    # log('user_id and id: ', user_id, id)
    c = Comment.find(id)
    if c.tweet_id == user_id:
        Comment.delete(id)
    return redirect('/tweet/index?user_id={}'.format(c.tweet_id))


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
    '/comment/new': login_required(new),
    '/comment/add': login_required(add),
    '/comment/edit': login_required(edit),
    '/comment/update': login_required(update),
    '/comment/delete': login_required(delete),
}
