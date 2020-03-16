from datetime import datetime


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

    @classmethod
    def _json_serializable(cls, rows):
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
                        tmp[key] = '{0:%Y-%m-%d %H:%M:%S}'.format(value)
                    else:
                        tmp[key] = value

                serializable.append(tmp)
        elif isinstance(rows, dict):
            serializable = {}
            for key, value in rows.items():
                if isinstance(value, bytes):
                    serializable[key] = value.decode('utf-8')
                elif isinstance(value, datetime):
                    serializable[key] = '{0:%Y-%m-%d %H:%M:%S}'.format(value)
                else:
                    serializable[key] = value

        return serializable

    def _execute(self, sql, params=()):
        self.db.cursor[self.db_name].execute(sql, params)

    def _fetchone(self):
        return self._json_serializable(self.db.cursor[self.db_name].fetchone())

    def _fetchall(self):
        return self._json_serializable(self.db.cursor[self.db_name].fetchall())

    def _commit(self):
        self.db.conn[self.db_name].commit()

    def _last_row_id(self):
        return self.db.cursor[self.db_name].lastrowid

    def _row_count(self):
        return self.db.cursor[self.db_name].rowcount

    def _select(self, columns=(), count=False, sum_of='', distinct_of='', where='', equal=None, like='', in_=(),
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
                where_clause = 'WHERE {0} = %s'.format(where)
                param_list.append(equal)
            elif like != '':
                where_clause = 'WHERE {0} LIKE %s'.format(where)
                param_list.append('%{0}%'.format(like))
            elif in_ != '':
                where_clause = 'WHERE {0} IN (%s)'.format(where)
                param_list.append(','.join(in_))

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

        self._execute(sql, params)
        if fetch_one != '':
            return self._fetchone()[fetch_one]
        else:
            return self._fetchall()

    def get(self, key):
        sql = 'SELECT * FROM {0}.{1} WHERE {2} = %s LIMIT 1 OFFSET 0'.format(self.db_name, self.table_name,
                                                                             self.primary_key)
        params = (key,)
        self._print_if_debug(sql % params)

        self._execute(sql, params)
        return self._fetchone()

    def select(self, columns=(), where='', equal=None, like='', in_=(), order_asc='', order_desc='', limit=1, offset=0):
        return self._select(columns=columns, where=where, equal=equal, like=like, in_=in_, order_asc=order_asc,
                            order_desc=order_desc, limit=limit, offset=offset)

    def count(self, where='', equal=None, like='', in_=()):
        return self._select(count=True, where=where, equal=equal, like=like, in_=in_)

    def sum(self, of, where='', equal=None, like='', in_=()):
        return self._select(sum_of=of, where=where, equal=equal, like=like, in_=in_)

    def distinct(self, of, where='', equal=None, like='', in_=(), order_asc='', order_desc='', limit=1, offset=0):
        return self._select(distinct_of=of, where=where, equal=equal, like=like, in_=in_, order_asc=order_asc,
                            order_desc=order_desc, limit=limit, offset=offset)

    def insert(self, d):
        sql = 'INSERT INTO {0}.{1}({2}) VALUES({3})'.format(self.db_name, self.table_name, ', '.join(d.keys()),
                                                            ', '.join(['%s' for _ in range(len(d))]))
        params = tuple(d.values())
        self._print_if_debug(sql % params)

        self._execute(sql, params)
        self._commit()
        return self._last_row_id()

    def update(self, d, where, equal):
        column_equal_value = ', '.join(['{} = %s'.format(k) for k in d.keys()])
        sql = 'UPDATE {0}.{1} SET {2} WHERE {3} = %s'.format(self.db_name, self.table_name, column_equal_value, where,
                                                             equal)

        values = list(d.values())
        values.append(equal)

        params = tuple(values)
        self._print_if_debug(sql % params)

        self._execute(sql, params)
        self._commit()
        return self._row_count()

    def delete(self, key):
        sql = 'DELETE FROM {0}.{1} WHERE {2} = %s'.format(self.db_name, self.table_name, self.primary_key)
        params = (key,)
        self._print_if_debug(sql % params)

        self._execute(sql, params)
        self._commit()
        return self._row_count()
