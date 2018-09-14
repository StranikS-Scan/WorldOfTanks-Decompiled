# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/bsddb/test/test_join.py
"""TestCases for using the DB.join and DBCursor.join_item methods.
"""
import os
import unittest
from test_all import db, dbshelve, test_support, verbose, get_new_environment_path, get_new_database_path
ProductIndex = [('apple', 'Convenience Store'),
 ('blueberry', "Farmer's Market"),
 ('shotgun', 'S-Mart'),
 ('pear', "Farmer's Market"),
 ('chainsaw', 'S-Mart'),
 ('strawberry', "Farmer's Market")]
ColorIndex = [('blue', 'blueberry'),
 ('red', 'apple'),
 ('red', 'chainsaw'),
 ('red', 'strawberry'),
 ('yellow', 'peach'),
 ('yellow', 'pear'),
 ('black', 'shotgun')]

class JoinTestCase(unittest.TestCase):
    keytype = ''

    def setUp(self):
        self.filename = self.__class__.__name__ + '.db'
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()
        self.env.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL | db.DB_INIT_LOCK)

    def tearDown(self):
        self.env.close()
        test_support.rmtree(self.homeDir)

    def test01_join(self):
        if verbose:
            print '\n', '-=' * 30
            print 'Running %s.test01_join...' % self.__class__.__name__
        priDB = db.DB(self.env)
        priDB.open(self.filename, 'primary', db.DB_BTREE, db.DB_CREATE)
        map(lambda t, priDB=priDB: priDB.put(*t), ProductIndex)
        secDB = db.DB(self.env)
        secDB.set_flags(db.DB_DUP | db.DB_DUPSORT)
        secDB.open(self.filename, 'secondary', db.DB_BTREE, db.DB_CREATE)
        map(lambda t, secDB=secDB: secDB.put(*t), ColorIndex)
        sCursor = None
        jCursor = None
        try:
            sCursor = secDB.cursor()
            tmp = sCursor.set('red')
            self.assertTrue(tmp)
            jCursor = priDB.join([sCursor])
            if jCursor.get(0) != ('apple', 'Convenience Store'):
                self.fail('join cursor positioned wrong')
            if jCursor.join_item() != 'chainsaw':
                self.fail('DBCursor.join_item returned wrong item')
            if jCursor.get(0)[0] != 'strawberry':
                self.fail('join cursor returned wrong thing')
            if jCursor.get(0):
                self.fail('join cursor returned too many items')
        finally:
            if jCursor:
                jCursor.close()
            if sCursor:
                sCursor.close()
            priDB.close()
            secDB.close()

        return


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JoinTestCase))
    return suite
