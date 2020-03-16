def test_get(g):
    print(g.req.form.getvalue('a', 3))
    print(g.req.form.getvalue('b', 4))
    print(g.req.form.getvalue('c', 5))
    g.resp.body = 'test_get'


def test_post(g):
    print(g.req.form.getvalue('a', 3))
    print(g.req.form.getvalue('b', 4))
    print(g.req.form.getvalue('c', 5))
    g.resp.body = 'test_post'
