import json
from datetime import timezone, timedelta
from urllib.parse import quote

from libs.date_time import DateTime
from libs.dict_as_obj import DictAsObj
from libs.enums import Error
from libs.enums import HttpStatusCode
from libs.http_status import HttpStatus


class Response:
    def __init__(self, cfg):
        self.cfg = cfg
        self.status = ''
        self.headers = []
        self.body = DictAsObj({
            'err': Error.UNKNOWN,
            'msg': '',
            'url': '',
            'dat': None,
        })

    def set_http_status(self, http_status_code):
        http_status_text = HttpStatus.texts[http_status_code]

        self.status = '{0} {1}'.format(http_status_code, http_status_text)
        if http_status_code != HttpStatusCode.OK:
            self.headers = [('Content-Type', 'application/json')]
            self.body = json.dumps({http_status_code: http_status_text})

    # SameSite: Strict, Lax, None
    def set_cookie(self, name, value, expires_in_minutes=0, path='/', domain='', secure=True, http_only=False,
                   same_site='None'):
        cookie_parts = ['{0}={1}'.format(quote(name), quote(value))]

        if expires_in_minutes > 0:
            expires = DateTime().dt + timedelta(minutes=expires_in_minutes)
            cookie_parts.append('Expires={0}'.format(expires.strftime('%a, %d %b %Y %H:%M:%S GMT')))

        cookie_parts.append('Path={0}'.format(path))

        if domain == '':
            domain = self.cfg['application']['domain']
        cookie_parts.append('Domain={0}'.format(domain))

        if secure:
            cookie_parts.append('Secure')

        if http_only:
            cookie_parts.append('HttpOnly')

        if same_site != '':
            cookie_parts.append('SameSite={0}'.format(same_site))

        set_cookie_header = ('Set-Cookie', '; '.join(cookie_parts))
        self.headers.append(set_cookie_header)
