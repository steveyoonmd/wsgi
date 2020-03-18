def test_upload(this):
    print(this.req.form.getvalue('name', ''))
    if 'file' not in this.req.form:
        this.resp.body = 'file not found'
        return

    file = this.req.form['file']
    print(file.filename)

    # print(g.req.form_get.getvalue('a', 3))
    # print(g.req.form_get.getvalue('b', 4))
    # print(g.req.form_get.getvalue('c', 5))
    this.resp.body = 'test_upload'


def test_json(this):
    print(this.req.json.get('a', 3))
    # print(g.req.form_post.getvalue('a', 3))
    # print(g.req.form_post.getvalue('b', 4))
    # print(g.req.form_post.getvalue('c', 5))
    this.resp.body = 'test_json'
