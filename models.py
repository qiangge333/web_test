import json
import time
import hashlib
import random

from utlis import log
from utlis import set_time


def random_str():
    seed = '`~!@#$%^&*()_+-=|\[]{};:,.<>?/ 0123456789 AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
    s = ''
    for i in range(16):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def db_save(data, path):
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(s)


def db_load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        return json.loads(s)


class Model(object):
    def __repr__(self):
        """
        __repr__ 是一个魔法方法
        简单来说, 它的作用是得到类的 字符串表达 形式
        比如 print(u) 实际上是 print(u.__repr__())
        """
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(classname, s)

    @classmethod
    def db_path(cls):
        name = cls.__name__
        path = 'dbfiles/{}.text'.format(name)
        return path

    @classmethod
    def all(cls):
        path = cls.db_path()
        models = db_load(path)
        ms = [cls(m) for m in models]
        return ms

    @classmethod
    def find_all(cls, **kwargs):
        ms = []
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        models = cls.all()
        for m in models:
            if m.__dict__[k] == v:
                ms.append(m)
        return ms

    @classmethod
    def find_by(cls, **kwargs):
        """
        用法如下，kwargs 是只有一个元素的 dict
        u = User.find_by(username='gua')
        """
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        ms = cls.all()
        # log('users: ', ms)
        for m in ms:
            log('user.id: ', m.id, type(m.id),)
            if m.__dict__[k] == v:
                return m
        return None

    @classmethod
    def find(cls, id):
        return cls.find_by(id=id)

    @classmethod
    def delete(cls, id):
        models = cls.all()
        index = -1
        for i, e in enumerate(models):
            if e.id == id:
                index = i
        if index != -1:
            models.pop(index)
            ms = [m.__dict__ for m in models]
            path = cls.db_path()
            db_save(ms, path)

    @classmethod
    def update(cls, id, form):
        m = cls.find(id)
        valid_names = [
            'task',
            'completed',
            'content',
        ]
        for key in form:
            if key in valid_names:
                setattr(m, key, form[key])
        m.updated_time = set_time()
        m.save()

    def save(self):
        models = self.all()
        if self.id is None:
            if len(models) == 0:
                self.id = 1
            else:
                m = models[-1]
                self.id = m.id + 1
            models.append(self)
        else:
            # self = models.find(index)
            index = -1
            for i, m in enumerate(models):
                if self.id == m.id:
                    index = i
                models[index] = self
        l = [m.__dict__ for m in models]
        path = self.db_path()
        db_save(l, path)


class User(Model):
    def __init__(self, form):
        self.id = form.get('id')
        self.username = form.get('username')
        self.password = form.get('password')
        self.salt = form.get('salt', random_str())

    def sha1_password(self, pwd):
        def sha1hex(ascii_str):
            # log('degug password: ', pwd, type(pwd))
            return hashlib.sha1(ascii_str.encode('ascii')).hexdigest()
        hash1 = sha1hex(pwd)
        log('debug hash1', hash1, self.salt)
        hash2 = sha1hex(hash1 + self.salt)
        return hash2

    def validate_login(self):
        u = self.find_by(username=self.username)
        if u is not None:
            log('debug u.salt', u.salt)
            self.salt = u.salt
            log('debug salt: ', self.salt, u.salt, self.salt == u.salt)
            pwd = self.sha1_password(self.password)
            return u.password == pwd
        else:
            return False

    def validate_register(self):
        m = self.find_by(username=self.username)
        # log('debug', m)
        valid_length = len(self.username) > 2 and len(self.password) > 2
        if m is None and valid_length:
            pwd = self.sha1_password(self.password)
            self.password = pwd
            log('注册成功')
        return m is None and valid_length

    def todos(self):
        return [m for m in Todo.all() if m.user_id == self.id]


class Todo(Model):
    @classmethod
    def new(cls, form, user_id=-1):
        t = cls(form, user_id)
        t.save()

    @classmethod
    def completed(cls, id, completed):
        t = cls.find(id)
        t.completed = completed
        t.save()

    def __init__(self, form, user_id=-1):
        self.id = form.get('id')
        self.task = form.get('task', '')
        self.completed = form.get('completed', False)
        # 和别的数据关联的方式, 用 user_id 表明拥有它的 user 实例
        self.user_id = form.get('user_id',user_id)
        self.updated_time = set_time()
        self.created_time = form.get('created_time', set_time())


class Tweet(Model):
    @classmethod
    def new(cls, form, user_id=-1):
        t = cls(form, user_id)
        t.save()

    def load_comments(self):
        # self.comments = Comment.find_all(tweet_id=self.id)
        self.comments = [c for c in Comment.all() if c.tweet_id == self.id]

    def __init__(self, form, user_id=-1):
        self.id = form.get('id')
        self.content = form.get('content')
        self.user_id = form.get('user_id', user_id)
        self.updated_time = set_time()
        self.created_time = form.get('created_time', set_time())


class Comment(Model):
    @classmethod
    def new(cls, form, user_id=-1):
        t = cls(form, user_id)
        t.save()

    def __init__(self, form, user_id=-1):
        self.id = form.get('id')
        self.content = form.get('content')
        self.user_id = form.get('user_id', user_id)
        self.tweet_id = int(form.get('tweet_id', -1))
        self.updated_time = set_time()
        self.created_time = form.get('created_time', set_time())


class Message(Model):
    def __init__(self, form):
        self.id = form.get('id')
        self.author = form.get('author')
        self.message = form.get('message')


def test_tweet():
    form = {
        'content': 'hello tweet',
    }
    t = Tweet(form, 1)
    t.save()


def test():
    # test_created()
    # test_read()
    # test_update()
    test_delete()
    # test_tweet()


def test_created():
    form = {
        'task': '喝水'
    }
    Todo.new(form, 1)


def test_read():
    # ts = Todo.all()
    # ts = Todo.find(1)
    # ts = Todo.find_all(user_id=1)
    u = User.find(1)
    ts = u.todos()
    log('所有的TODO', ts)


def test_update():
    # form = {
    #     'id': 100,
    #     'task': '吃瓜 吃瓜',
    #     'completed': True
    # }
    # Todo.update(1, form)
    # log('todo_update_test', Todo.find(1))
    Todo.completed(1, False)


def test_delete():
    Todo.delete(4, 1)
    t = Todo.find(4)
    assert t is None, '删除失败'


if __name__ == '__main__':
    test()

