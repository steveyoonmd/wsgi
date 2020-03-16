import pymysql


class Database:
    def __init__(self, cfg):
        self.cfg = cfg
        self.conn = {}
        self.cursor = {}

    def connect(self, db_name):
        if db_name in self.cursor:
            return

        self.conn[db_name] = pymysql.connect(host=self.cfg['database_' + db_name]['host'],
                                             user=self.cfg['database_' + db_name]['user'],
                                             password=self.cfg['database_' + db_name]['password'],
                                             charset=self.cfg['database_' + db_name]['charset'],
                                             database=db_name,
                                             port=self.cfg['database_' + db_name]['port'],
                                             cursorclass=pymysql.cursors.DictCursor)
        self.cursor[db_name] = self.conn[db_name].cursor()

    def close(self):
        for key in self.cursor.keys():
            self.cursor[key].close()

        for key in self.conn.keys():
            self.conn[key].close()
