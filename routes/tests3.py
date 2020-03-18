from libs.aes_crypto import AESCrypto
from models.test1 import Test1


def test_orm(this):
    test1 = Test1(db=this.db, debug=True)

    test1_get = test1.get(1)
    print('test1_get: {0}\n'.format(test1_get))

    test1_select = test1.rows(('test1_id',), where='test1_id', equal=2)
    print('test1_select: {0}\n'.format(test1_select))

    test1_count = test1.count(where='test1_id', equal=3)
    print('test1_count: {0}\n'.format(test1_count))

    test1_sum = test1.sum(of='test1_id', where='test1_id', equal=4)
    print('test1_sum: {0}\n'.format(test1_sum))

    test1_distinct = test1.distinct(of='test1_id')
    print('test1_distinct: {0}\n'.format(test1_distinct))

    test1_insert = test1.insert(
        {'col01': 255, 'col02': 65535, 'col03': 429496729, 'col04': 1844674407370955161, 'col05': 5.01, 'col06': 6.01,
         'col07': 'param7', 'col08': 'param8', 'col09': 'param9', 'col10': '2020-03-14 21:25:20', 'col11': None,
         'col12': '2020-03-14 21:25:20'})
    print('test1_insert: {0}\n'.format(test1_insert))

    test1_update = test1.update(
        {'col01': 254, 'col02': 65535, 'col03': 429496729, 'col04': 1844674407370955161, 'col05': 5.01, 'col06': 6.01,
         'col07': 'param7', 'col08': 'param8', 'col09': 'param9', 'col10': '2020-03-14 21:25:20', 'col11': None,
         'col12': '2020-03-14 21:25:20'}, where='test1_id', equal=test1_insert)
    print('test1_update: {0}\n'.format(test1_update))

    test1_delete = test1.delete(test1_insert)
    print('test1_delete: {0}\n'.format(test1_delete))

    this.resp.body = 'test_orm'


def test_aes(this):
    a = AESCrypto(this.cfg['aes_crypto']['key'])
    e = a.encrypt('한글')
    print(e)
    d = a.decrypt(e)
    print(d)

    this.resp.body = 'test_aes'
