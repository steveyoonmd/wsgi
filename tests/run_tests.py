import hashlib
import json
import ssl
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen, Request


def print_if_debug(var, values):
    if var['debug']:
        print(values)


def md5hex(plain_text):
    m = hashlib.md5()
    m.update(plain_text.encode('utf-8'))

    return m.hexdigest()


def send_http_request(var, req, params=None):
    resp = None

    try:
        ssl_ctx = ssl._create_unverified_context()
        if params is None:
            resp = urlopen(req, context=ssl_ctx)
        else:
            resp = urlopen(req, params.encode('utf-8'), context=ssl_ctx)
    except HTTPError as ex:
        print(ex)

    result = 'ERROR'
    if resp is None:
        return resp, result

    if resp.getcode() != 200:
        return resp, result

    body = resp.read().decode('utf-8')
    json_loaded = json.loads(body)
    print_if_debug(var, 'RES: ' + json.dumps(json_loaded))

    if 'err' in json_loaded and json_loaded['err'] == 0:
        result = 'OK'

    return resp, result


def users_login(var):
    func_name = sys._getframe().f_code.co_name

    http_post_params = json.dumps({
        'user_id': var['user_id'],
        'md5_hash': md5hex(var['user_id'] + md5hex(var['passwd'])),
    })

    url = '{0}/{1}'.format(var['base_url'], 'users/login')
    print_if_debug(var, url + ' (' + func_name + ')')
    print_if_debug(var, 'REQ: ' + http_post_params)

    req = Request(url, headers={
        'Content-Type': 'application/json'
    })

    (resp, result) = send_http_request(var, req, http_post_params)

    cookie = resp.info()['Set-Cookie']
    print_if_debug(var, cookie)
    var['cookie'] = cookie

    print('{0}: {1}'.format(result, func_name))
    print_if_debug(var, '\n')


def tests1_test_get(var):
    func_name = sys._getframe().f_code.co_name
    http_get_params = urlencode({
        'a': 1,
        'b': 2,
    })

    url = '{0}/{1}?{2}'.format(var['base_url'], 'tests1/test_get', http_get_params)
    print_if_debug(var, url + ' (' + func_name + ')')
    print_if_debug(var, 'REQ: ' + http_get_params)

    req = Request(url, headers={
        'Cookie': var['cookie'],
    })

    (resp, result) = send_http_request(var, req)

    print('{0}: {1}'.format(result, func_name))
    print_if_debug(var, '\n')


def tests1_test_post(var):
    func_name = sys._getframe().f_code.co_name
    http_post_params = urlencode({
        'a': 1,
        'b': 2,
    })

    url = '{0}/{1}'.format(var['base_url'], 'tests1/test_post')
    print_if_debug(var, url + ' (' + func_name + ')')
    print_if_debug(var, 'REQ: ' + http_post_params)

    req = Request(url, headers={
        'Cookie': var['cookie'],
    })

    (resp, result) = send_http_request(var, req, http_post_params)

    print('{0}: {1}'.format(result, func_name))
    print_if_debug(var, '\n')


def tests2_test_json(var):
    func_name = sys._getframe().f_code.co_name
    http_post_params = json.dumps({
        'a': 1,
        'b': 2,
    })

    url = '{0}/{1}'.format(var['base_url'], 'tests2/test_json')
    print_if_debug(var, url + ' (' + func_name + ')')
    print_if_debug(var, 'REQ: ' + http_post_params)

    req = Request(url, headers={
        'Cookie': var['cookie'],
        'Content-Type': 'application/json',
    })

    (resp, result) = send_http_request(var, req, http_post_params)

    print('{0}: {1}'.format(result, func_name))
    print_if_debug(var, '\n')


def tests3_test_orm(var):
    func_name = sys._getframe().f_code.co_name
    http_post_params = json.dumps({})

    url = '{0}/{1}'.format(var['base_url'], 'tests3/test_orm')
    print_if_debug(var, url + ' (' + func_name + ')')
    print_if_debug(var, 'REQ: ' + http_post_params)

    req = Request(url, headers={
        'Cookie': var['cookie'],
        'Content-Type': 'application/json',
    })

    (resp, result) = send_http_request(var, req, http_post_params)

    print('{0}: {1}'.format(result, func_name))
    print_if_debug(var, '\n')


def tests3_test_aes(var):
    func_name = sys._getframe().f_code.co_name
    http_post_params = json.dumps({})

    url = '{0}/{1}'.format(var['base_url'], 'tests3/test_aes')
    print_if_debug(var, url + ' (' + func_name + ')')
    print_if_debug(var, 'REQ: ' + http_post_params)

    req = Request(url, headers={
        'Cookie': var['cookie'],
        'Content-Type': 'application/json',
    })

    (resp, result) = send_http_request(var, req, http_post_params)

    print('{0}: {1}'.format(result, func_name))
    print_if_debug(var, '\n')


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 ./run_tests.py localhost')
        sys.exit()

    funcs = list()
    funcs.append(users_login)
    funcs.append(tests1_test_get)
    funcs.append(tests1_test_post)
    funcs.append(tests2_test_json)
    funcs.append(tests3_test_orm)
    funcs.append(tests3_test_aes)

    json_loaded = {}
    with open('./tests.json', encoding='utf-8') as tests_json:
        json_loaded = json.loads(tests_json.read())

    var = json_loaded[sys.argv[1]]
    var['debug'] = False

    print()
    for f in funcs:
        f(var)


main()
