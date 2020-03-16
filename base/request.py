import cgi
import json

from urllib.parse import unquote


class Request:
    def __init__(self, env):
        self.env = env

        self.cfg = self.env.get('CFG')
        self.method = self.env.get('REQUEST_METHOD')
        self.origin = self.env.get('HTTP_ORIGIN', '')
        self.content_type = env['CONTENT_TYPE']

        self.remote_ip_addr = ''
        self.remote_ip_addr_ends_with_asterisk = ''

        self.headers = {}
        self.cookies = {}

        self.form = None
        self.json = None

    def parse(self):
        self.remote_ip_addr = self.env.get('REMOTE_ADDR')

        x_forwarded_for = self.env.get('X_FORWARDED_FOR')
        if x_forwarded_for is not None:
            self.remote_ip_addr = x_forwarded_for.split(', ')[0]

        if self.remote_ip_addr is not None:
            remote_ip_addr_split = self.remote_ip_addr.split('.')
            remote_ip_addr_split.pop()
            remote_ip_addr_split.append('*')

            self.remote_ip_addr_ends_with_asterisk = '.'.join(remote_ip_addr_split)

        http_cookie = self.env.get('HTTP_COOKIE', '')
        http_cookie_split = http_cookie.split('; ')
        for name_value in http_cookie_split:
            if '=' not in name_value:
                continue
            name_value_split = name_value.split('=')
            self.cookies[unquote(name_value_split[0])] = unquote(name_value_split[1])

        if self.content_type.startswith('application/json'):
            content_length = int(self.env.get('CONTENT_LENGTH', 0))
            if content_length == 0:
                raise ValueError('CONTENT_LENGTH')

            wsgi_input = self.env.get('wsgi.input')
            if wsgi_input is None:
                raise ValueError('wsgi_input')

            wsgi_input_read = wsgi_input.read(content_length)
            self.json = json.loads(wsgi_input_read)
        else:
            self.form = cgi.FieldStorage(
                environ=self.env,
                fp=self.env['wsgi.input'],
                keep_blank_values=True,
            )
