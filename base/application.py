import json

from base.handler import Handler


class Application:
    def __init__(self):
        self.cfg = {}
        self.routes = {}

        with open('./cfg.json', encoding='utf-8') as cfg_json:
            self.cfg = json.loads(cfg_json.read())

        from routes.index import index_get, index_post
        from routes.tests1 import test_get, test_post
        from routes.tests2 import test_upload, test_json
        from routes.tests3 import test_orm, test_aes

        self.routes = {
            '/': index_get,
            '/index_post': index_post,
            '/tests1/test_get': test_get,
            '/tests1/test_post': test_post,
            '/tests2/test_upload': test_upload,
            '/tests2/test_json': test_json,
            '/tests3/test_orm': test_orm,
            '/tests3/test_aes': test_aes,
        }

    def __call__(self, env, start_resp):
        env['CFG'] = self.cfg
        handler = Handler(env, start_resp)

        path_info = env.get('PATH_INFO', '/')
        func = self.routes.get(path_info)

        if func is not None:
            return handler.handle_func(func)

        return handler.handle_file(path_info)
