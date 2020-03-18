def test_get(this):
    print(this.req.form.getvalue('a', 3))
    print(this.req.form.getvalue('b', 4))
    print(this.req.form.getvalue('c', 5))
    this.resp.body = 'test_get'


def test_post(this):
    print(this.req.form.getvalue('a', 3))
    print(this.req.form.getvalue('b', 4))
    print(this.req.form.getvalue('c', 5))
    this.resp.body = 'test_post'
