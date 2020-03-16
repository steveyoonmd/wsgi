from base.model import Model


class Test1(Model):
    def __init__(self, db, debug=False):
        self.db_name = 'database1'
        self.table_name = 'test1'
        self.primary_key = 'test1_id'

        super().__init__(db, self.db_name, self.table_name, self.primary_key, debug)
