# ISC License

# Copyright (c) 2018-2020 Adam Johnson

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

# https://github.com/adamchainz/apig-wsgi

import sys
from base64 import b64decode
from io import BytesIO

from base.application import Application


def env(evt):
    this = {
        'REQUEST_METHOD': evt['httpMethod'],
        'PATH_INFO': evt['path'],
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'REMOTE_ADDR': '127.0.0.1',

        'wsgi.version': (1, 0),
        'wsgi.errors': sys.stderr,
        'wsgi.input': None,
        'wsgi.url_scheme': '',
        'wsgi.run_once': False,
        'wsgi.multiprocess': False,
        'wsgi.multithread': False,
    }

    query_string_parameters = evt.get('queryStringParameters', {}) or {}
    this['QUERY_STRING'] = '&'.join('{}={}'.format(k, v) for k, v in query_string_parameters.items())

    headers = evt.get('headers', {}) or {}
    for key, value in headers.items():
        key = key.upper().replace('-', '_')

        if key == 'CONTENT_TYPE':
            this['CONTENT_TYPE'] = value
        elif key == 'HOST':
            this['SERVER_NAME'] = value
        elif key == 'X_FORWARDED_PORT':
            this['SERVER_PORT'] = value
        elif key == 'X_FORWARDED_FOR':
            this['REMOTE_ADDR'] = value.split(', ')[0]
        elif key == 'X_FORWARDED_PROTO':
            this['wsgi.url_scheme'] = value

        this['HTTP_' + key] = value

    # When you send multipart/form-data to AWS Lambda via AWS API Gateway,
    # Python receives the multipart body as utf-8 string, even if it's an image file.
    # For Python, the multipart body needs to be encoded in base64.
    # 1. AWS API Gateway -> Resources -> Create Method -> Use Lambda Proxy integration
    # 2. AWS API Gateway -> Settings -> Binary Media Types -> multipart/form-data
    # 3. Browser -> XMLHttpRequest -> xhr.setRequestHeader('Accept', 'multipart/form-data');
    body = evt.get('body', '') or ''
    if evt.get('isBase64Encoded', False):
        body = b64decode(body)
    else:
        body = body.encode('utf-8')

    this['CONTENT_LENGTH'] = str(len(body))
    this['wsgi.input'] = BytesIO(body)

    return this


class AwsLambdaResponse:
    def __init__(self):
        self.statusCode = '200'
        self.headers = []
        self.body = BytesIO()

    def start(self, status, headers, exc_info=None):
        self.statusCode = status[:3]
        self.headers.extend(headers)

    def write(self, stream):
        try:
            for data in stream:
                if data:
                    self.body.write(data)
        finally:
            if hasattr(stream, 'close'):
                stream.close()

    def as_dict(self):
        return {
            'statusCode': self.statusCode,
            'headers': dict(self.headers),
            'body': self.body.getvalue().decode('utf-8'),
        }


class AwsLambdaApplication:
    def __call__(self, evt, ctx):
        app = Application()

        resp = AwsLambdaResponse()
        resp.write(app.__call__(env(evt), resp.start))

        return resp.as_dict()
