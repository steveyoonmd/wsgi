from models.test1 import Test1


def index_get(this):
    test1 = Test1(this.db)
    print(test1)
    # this.resp.err = Error.NONE
    this.resp.body = 'index_get'


def index_post(this):
    this.resp.body = 'index_post'
