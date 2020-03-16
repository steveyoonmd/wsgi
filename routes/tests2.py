def test_upload(g):
    print(g.req.form.getvalue('name', ''))
    if 'file' not in g.req.form:
        g.resp.body = 'file not found'
        return

    file = g.req.form['file']
    print(file.filename)

    # print(g.req.form_get.getvalue('a', 3))
    # print(g.req.form_get.getvalue('b', 4))
    # print(g.req.form_get.getvalue('c', 5))
    g.resp.body = 'test_upload'


def test_json(g):
    print(g.req.json.get('a', 3))
    # print(g.req.form_post.getvalue('a', 3))
    # print(g.req.form_post.getvalue('b', 4))
    # print(g.req.form_post.getvalue('c', 5))
    g.resp.body = 'test_json'
