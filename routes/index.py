from models.test1 import Test1


def index_get(g):
    test1 = Test1(g.db)
    g.resp.body = 'index_get'


def index_post(g):
    g.resp.body = 'index_post'
