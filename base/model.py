from datetime import datetime

from libs.date_time import DateTime


class Model:
    def __init__(self, db, db_name, table_name, primary_key, debug):
        self.db = db
        self.db_name = db_name
        self.table_name = table_name
        self.primary_key = primary_key

        self.debug = debug
        self.db.connect(self.db_name)

    def _print_if_debug(self, sql):
        if self.debug:
            print(sql)

    def json_serializable(self, rows):
        if rows is None:
            return None

        serializable = None
        if isinstance(rows, list):
            serializable = []
            for row in rows:
                tmp = {}
                for key, value in row.items():
                    if isinstance(value, bytes):
                        tmp[key] = value.decode('utf-8')
                    elif isinstance(value, datetime):
                        tmp[key] = DateTime(value, self.db.cfg['application']['time_zone']).localtime_str()
                    else:
                        tmp[key] = value

                serializable.append(tmp)
        elif isinstance(rows, dict):
            serializable = {}
            for key, value in rows.items():
                if isinstance(value, bytes):
                    serializable[key] = value.decode('utf-8')
                elif isinstance(value, datetime):
                    serializable[key] = DateTime(value, self.db.cfg['application']['time_zone']).localtime_str()
                else:
                    serializable[key] = value

        return serializable

    def execute(self, sql, params=()):
        self.db.cursor[self.db_name].execute(sql, params)

    def fetchone(self):
        return self.json_serializable(self.db.cursor[self.db_name].fetchone())

    def fetchall(self):
        return self.json_serializable(self.db.cursor[self.db_name].fetchall())

    def commit(self):
        self.db.conn[self.db_name].commit()

    def last_row_id(self):
        return self.db.cursor[self.db_name].lastrowid

    def row_count(self):
        return self.db.cursor[self.db_name].rowcount

    def select(self, columns=(), count=False, sum_of='', distinct_of='', where='', equal=None, like='', in_=(),
               order_asc='', order_desc='', limit=1, offset=0):
        select_clause = ''
        fetch_one = ''
        if len(columns) > 0:
            select_clause = 'SELECT {0} FROM {1}.{2}'.format(', '.join(columns), self.db_name, self.table_name)
        elif count:
            select_clause = 'SELECT COUNT({0}) AS count_ FROM {1}.{2}'.format(self.primary_key, self.db_name,
                                                                              self.table_name)
            fetch_one = 'count_'
        elif sum_of != '':
            select_clause = 'SELECT SUM({0}) AS sum_ FROM {1}.{2}'.format(sum_of, self.db_name, self.table_name)
            fetch_one = 'sum_'
        elif distinct_of != '':
            select_clause = 'SELECT DISTINCT({0}) FROM {1}.{2}'.format(distinct_of, self.db_name, self.table_name)
        else:
            select_clause = 'SELECT * FROM {0}.{1}'.format(self.db_name, self.table_name)

        param_list = []
        where_clause = ''
        if where != '':
            if equal is not None:
                where_clause = 'WHERE deleted_time = 0 AND {0} = %s'.format(where)
                param_list.append(equal)
            elif like != '':
                where_clause = 'WHERE deleted_time = 0 AND {0} LIKE %s'.format(where)
                param_list.append('%{0}%'.format(like))
            elif len(in_) > 0:
                where_clause = 'WHERE deleted_time = 0 AND {0} IN (%s)'.format(where)
                param_list.append(', '.join(in_))

        order_clause = ''
        if order_asc != '':
            order_clause = 'ORDER BY {0} ASC'.format(order_asc)
        elif order_desc != '':
            order_clause = 'ORDER BY {0} DESC'.format(order_desc)

        limit_clause = 'LIMIT %s OFFSET %s'
        param_list.extend((limit, offset))

        sql = '{0} {1} {2} {3}'.format(select_clause, where_clause, order_clause, limit_clause)
        params = tuple(param_list)
        self._print_if_debug(sql % params)

        self.execute(sql, params)
        if fetch_one != '':
            return self.fetchone()[fetch_one]
        else:
            return self.fetchall()

    def get(self, key):
        sql = 'SELECT * FROM {0}.{1} WHERE {2} = %s AND deleted_time = 0 LIMIT 1 OFFSET 0'.format(self.db_name,
                                                                                                  self.table_name,
                                                                                                  self.primary_key)
        params = (key,)
        self._print_if_debug(sql % params)

        self.execute(sql, params)
        return self.fetchone()

    def rows(self, columns=(), where='', equal=None, like='', in_=(), order_asc='', order_desc='', limit=1, offset=0):
        return self.select(columns=columns, where=where, equal=equal, like=like, in_=in_, order_asc=order_asc,
                           order_desc=order_desc, limit=limit, offset=offset)

    def count(self, where='', equal=None, like='', in_=()):
        return self.select(count=True, where=where, equal=equal, like=like, in_=in_)

    def sum(self, of, where='', equal=None, like='', in_=()):
        return self.select(sum_of=of, where=where, equal=equal, like=like, in_=in_)

    def distinct(self, of, where='', equal=None, like='', in_=(), order_asc='', order_desc='', limit=1, offset=0):
        return self.select(distinct_of=of, where=where, equal=equal, like=like, in_=in_, order_asc=order_asc,
                           order_desc=order_desc, limit=limit, offset=offset)

    def insert(self, data):
        sql = 'INSERT INTO {0}.{1}({2}) VALUES({3})'.format(self.db_name, self.table_name, ', '.join(data.keys()),
                                                            ', '.join(['%s' for _ in range(len(data))]))
        params = tuple(data.values())
        self._print_if_debug(sql % params)

        self.execute(sql, params)
        self.commit()
        last_row_id = self.last_row_id()

        # log_sql = 'INSERT INTO {0}.{1}('
        return last_row_id

    def update(self, data, where, equal):
        column_equal_value = ', '.join(['{} = %s'.format(k) for k in data.keys()])
        sql = 'UPDATE {0}.{1} SET {2} WHERE {3} = %s'.format(self.db_name, self.table_name, column_equal_value, where,
                                                             equal)

        values = list(data.values())
        values.append(equal)

        params = tuple(values)
        self._print_if_debug(sql % params)

        self.execute(sql, params)
        self.commit()
        row_count = self.row_count()

        # log_sql = 'INSERT INTO {0}.{1}('
        return row_count

    def delete(self, key):
        # sql = 'DELETE FROM {0}.{1} WHERE {2} = %s'.format(self.db_name, self.table_name, self.primary_key)

        deleted_time = DateTime(datetime.now()).time_stamp()
        sql = 'UPDATE {0}.{1} SET deleted_time = %s WHERE {2} = %s'.format(self.db_name, self.table_name,
                                                                           self.primary_key)
        params = (key, deleted_time)
        self._print_if_debug(sql % params)

        self.execute(sql, params)
        self.commit()
        row_count = self.row_count()

        # log_sql = 'INSERT INTO {0}.{1}('
        return row_count
