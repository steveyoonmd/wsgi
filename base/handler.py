import mimetypes
import os
from datetime import datetime
from os import path

from base.database import Database
from base.request import Request
from base.response import Response
from libs.session import Session
from libs.enums import HttpStatusCode


class Handler:
    def __init__(self, env, start_resp):
        self._env = env
        self._start_resp = start_resp

        self.cfg = self._env['CFG']
        self.db = Database(self.cfg)

        self.req = Request(self._env)
        self.resp = Response(self._env)
        self.sess = Session(self)

    def handle_func(self, func):
        if self.req.origin != '' or self.req.origin in self.cfg['access_allowed_http_origins']:
            self.resp.headers.extend([
                ('Access-Control-Allow-Origin', self.req.origin),
                ('Access-Control-Allow-Methods', 'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT'),
                ('Access-Control-Allow-Headers', 'Authorization, Content-Type, Cookie, Origin, X-Amz-Date, '
                                                 'X-Amz-Security-Token, X-Api-Key, x-forced-preflight'),
                ('Access-Control-Allow-Credentials', 'true'),
            ])

        if self.req.method == 'OPTIONS':
            self.resp.status_text(HttpStatusCode.OK)
            self._start_resp(self.resp.status, self.resp.headers)
            return [self.resp.body.encode('utf-8')]

        try:
            self.req.parse()
            func(self)
        except Exception as ex:
            print(ex)
            self.resp.status_text(HttpStatusCode.INTERNAL_SERVER_ERROR)
            self._start_resp(self.resp.status, self.resp.headers)
            return [self.resp.body.encode('utf-8')]
        else:
            self.db.close()

        # if not isinstance(self.resp.body, str):
        #     self.resp.body = json.dumps(self.resp.body)

        self.resp.status_text(HttpStatusCode.OK)
        self._start_resp(self.resp.status, self.resp.headers)
        return [self.resp.body.encode('utf-8')]

    def file_type(self, file_path):
        mime_type, encoding = mimetypes.guess_type(file_path)

        if mime_type not in self.cfg['text_mime_types']:
            return mime_type

        return '{0}; charset={1}'.format(mime_type, 'utf-8')

    @classmethod
    def file_read(cls, file):
        while True:
            try:
                file_read = file.read(64 * 1024)
                if file_read:
                    yield file_read
                else:
                    raise StopIteration
            except StopIteration:
                file.close()
                break

    def file_body(self, file_path):
        if self.req.method == 'HEAD':
            return []

        return self.file_read(open(file_path, 'rb'))

    def handle_file(self, path_info):
        path_info = path_info.strip('/')
        if not path_info.startswith('{0}/'.format(self.cfg['application']['static_path'].strip('/'))):
            self.resp.status_text(HttpStatusCode.NOT_FOUND)
            self._start_resp(self.resp.status, self.resp.headers)
            return [self.resp.body.encode('utf-8')]

        file_path = path.join(path.abspath('.'), path_info)
        if not path.exists(file_path) or not path.isfile(file_path):
            self.resp.status_text(HttpStatusCode.NOT_FOUND)
            self._start_resp(self.resp.status, self.resp.headers)
            return [self.resp.body.encode('utf-8')]

        if not os.access(file_path, os.R_OK):
            self.resp.status_text(HttpStatusCode.FORBIDDEN)
            self._start_resp(self.resp.status, self.resp.headers)
            return [self.resp.body.encode('utf-8')]

        if self.req.method not in ('GET', 'HEAD'):
            self.resp.status_text(HttpStatusCode.METHOD_NOT_ALLOWED)
            self._start_resp(self.resp.status, self.resp.headers)
            return [self.resp.body.encode('utf-8')]

        self.resp.headers.extend([
            ('Content-Type', self.file_type(file_path)),
            ('Content-Length', str(os.stat(file_path).st_size)),
            ('Accept-Ranges', 'bytes'),
            ('Last-Modified', datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ])

        self.resp.status_text(HttpStatusCode.OK)
        self._start_resp(self.resp.status, self.resp.headers)
        return self.file_body(file_path)
