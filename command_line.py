from pprint import pprint
from wsgiref.util import setup_testing_defaults

from base.application import Application


def start_resp(status, headers, exc_info=None):
    print(status)
    print(headers)


def run():
    env = {
        'HTTP_COOKIE': '',
        'CONTENT_TYPE': 'application/x-www-form-urlencoded',
        'PATH_INFO': '/tests1/test_get'
    }
    setup_testing_defaults(env)
    pprint(env)

    app = Application()
    body = app.__call__(env, start_resp)
    print(body)


run()
