# Embedded file name: scripts/common/Lib/bsddb/test/test_early_close.py
"""TestCases for checking that it does not segfault when a DBEnv object
is closed before its DB objects.
"""
import os, sys
import unittest
from test_all import db, test_support, verbose, get_new_environment_path, get_new_database_path
try:
    import warnings
except ImportError:
    pass
else:
    warnings.filterwarnings('ignore', message='DB could not be closed in', category=RuntimeWarning)

class DBEnvClosedEarlyCrash(unittest.TestCase):

    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.filename = 'test'

    def tearDown(self):
        test_support.rmtree(self.homeDir)

    def test01_close_dbenv_before_db(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir, db.DB_INIT_CDB | db.DB_CREATE | db.DB_THREAD | db.DB_INIT_MPOOL, 438)
        d = db.DB(dbenv)
        d2 = db.DB(dbenv)
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 438)
        self.assertRaises(db.DBNoSuchFileError, d2.open, self.filename + '2', db.DB_BTREE, db.DB_THREAD, 438)
        d.put('test', 'this is a test')
        self.assertEqual(d.get('test'), 'this is a test', 'put!=get')
        dbenv.close()
        self.assertRaises(db.DBError, d.get, 'test')

    def test02_close_dbenv_before_dbcursor(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir, db.DB_INIT_CDB | db.DB_CREATE | db.DB_THREAD | db.DB_INIT_MPOOL, 438)
        d = db.DB(dbenv)
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 438)
        d.put('test', 'this is a test')
        d.put('test2', 'another test')
        d.put('test3', 'another one')
        self.assertEqual(d.get('test'), 'this is a test', 'put!=get')
        c = d.cursor()
        c.first()
        c.next()
        d.close()
        self.assertRaises(db.DBError, c.next)
        d = db.DB(dbenv)
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 438)
        c = d.cursor()
        c.first()
        c.next()
        dbenv.close()
        self.assertRaises(db.DBError, c.next)

    def test03_close_db_before_dbcursor_without_env(self):
        import os.path
        path = os.path.join(self.homeDir, self.filename)
        d = db.DB()
        d.open(path, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 438)
        d.put('test', 'this is a test')
        d.put('test2', 'another test')
        d.put('test3', 'another one')
        self.assertEqual(d.get('test'), 'this is a test', 'put!=get')
        c = d.cursor()
        c.first()
        c.next()
        d.close()
        self.assertRaises(db.DBError, c.next)

    def test04_close_massive(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir, db.DB_INIT_CDB | db.DB_CREATE | db.DB_THREAD | db.DB_INIT_MPOOL, 438)
        dbs = [ db.DB(dbenv) for i in xrange(16) ]
        cursors = []
        for i in dbs:
            i.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 438)

        dbs[10].put('test', 'this is a test')
        dbs[10].put('test2', 'another test')
        dbs[10].put('test3', 'another one')
        self.assertEqual(dbs[4].get('test'), 'this is a test', 'put!=get')
        for i in dbs:
            cursors.extend([ i.cursor() for j in xrange(32) ])

        for i in dbs[::3]:
            i.close()

        for i in cursors[::3]:
            i.close()

        self.assertRaises(db.DBError, dbs[9].get, 'test')
        self.assertRaises(db.DBError, cursors[101].first)
        cursors[80].first()
        cursors[80].next()
        dbenv.close()
        self.assertRaises(db.DBError, cursors[80].next)

    def test05_close_dbenv_delete_db_success(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir, db.DB_INIT_CDB | db.DB_CREATE | db.DB_THREAD | db.DB_INIT_MPOOL, 438)
        d = db.DB(dbenv)
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 438)
        dbenv.close()
        del d
        try:
            import gc
        except ImportError:
            gc = None

        if gc:
            gc.collect()
        return

    def test06_close_txn_before_dup_cursor(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir, db.DB_INIT_TXN | db.DB_INIT_MPOOL | db.DB_INIT_LOG | db.DB_CREATE)
        d = db.DB(dbenv)
        txn = dbenv.txn_begin()
        d.open(self.filename, dbtype=db.DB_HASH, flags=db.DB_CREATE, txn=txn)
        d.put('XXX', 'yyy', txn=txn)
        txn.commit()
        txn = dbenv.txn_begin()
        c1 = d.cursor(txn)
        c2 = c1.dup()
        self.assertEqual(('XXX', 'yyy'), c1.first())
        import warnings
        if sys.version_info < (2, 6):
            warnings.simplefilter('ignore')
            txn.commit()
            warnings.resetwarnings()
        else:
            w = warnings.catch_warnings()
            w.__enter__()
            try:
                warnings.simplefilter('ignore')
                txn.commit()
            finally:
                w.__exit__()

        self.assertRaises(db.DBCursorClosedError, c2.first)

    def test07_close_db_before_sequence(self):
        import os.path
        path = os.path.join(self.homeDir, self.filename)
        d = db.DB()
        d.open(path, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 438)
        dbs = db.DBSequence(d)
        d.close()
        dbs.close()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DBEnvClosedEarlyCrash))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
