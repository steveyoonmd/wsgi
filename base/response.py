from libs.enums import HttpStatusCode
from libs.http_status import HttpStatus


class Response:
    def __init__(self, env):
        self.cfg = env['CFG']
        self.status = ''
        self.headers = []
        self.body = ''

    def status_text(self, http_status):
        http_status_text = HttpStatus.texts[http_status]

        self.status = '{0} {1}'.format(http_status, http_status_text)
        if http_status != HttpStatusCode.OK:
            self.headers = [('Content-Type', 'text/plain')]
            self.body = http_status_text

    # SameSite: None, Strict, Lax
    def set_cookie(self, name, value, expires='', path='/', domain='', secure=True, http_only=False, same_site=''):
        self.headers.append(('Set-Cookie', 'a'))
