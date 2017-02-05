from models import Todo
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


def index(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    log('session and cookies: ', session, request.cookies)
    todo_list = Todo.find_all(user_id=user_id)
    body = template('todo_index.html', todo_list=todo_list)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def add(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    log('debug session_id and user_id', session_id, user_id)
    form = request.form()
    Todo.new(form, user_id)
    return redirect('/todo/')


def edit(request):
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    id = int(request.query.get('id'))
    t = Todo.find(id)
    body = template('todo_edit.html', todo=t)
    response = header + '\r\n' + body
    return response.encode(encoding='utf-8')


def update(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    form = request.form()
    id = int(form.get('id'))
    t = Todo.find(id)
    if t.user_id == user_id:
        Todo.update(id, form)
    return redirect('/todo/')


def delete(request):
    session_id = request.cookies.get('user', '')
    user_id = session(session_id)
    id = int(request.query.get('id'))
    log('user_id and id: ', user_id, id)
    t = Todo.find(id)
    if t.user_id == user_id:
        Todo.delete(id)
    return redirect('/todo/')


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
    '/todo/': login_required(index),
    '/todo/add': login_required(add),
    '/todo/edit': login_required(edit),
    '/todo/update': login_required(update),
    '/todo/delete': login_required(delete),
}
