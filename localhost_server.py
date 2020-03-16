from wsgiref.simple_server import make_server

from base.application import Application


def run():
    app = Application()

    host = '0.0.0.0'
    port = 5000

    try:
        server = make_server(host, port, app)
        print('starting server on {0}:{1}..'.format(host, port))
        server.serve_forever()
    except KeyboardInterrupt:
        print('stopping server..')


run()
