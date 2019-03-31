# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sqlite3/test/transactions.py
# Compiled at: 2010-05-25 20:46:16
import sys
import os, unittest
import sqlite3 as sqlite

def get_db_path():
    pass


class TransactionTests(unittest.TestCase):

    def setUp(self):
        try:
            os.remove(get_db_path())
        except OSError:
            pass

        self.con1 = sqlite.connect(get_db_path(), timeout=0.1)
        self.cur1 = self.con1.cursor()
        self.con2 = sqlite.connect(get_db_path(), timeout=0.1)
        self.cur2 = self.con2.cursor()

    def tearDown(self):
        self.cur1.close()
        self.con1.close()
        self.cur2.close()
        self.con2.close()
        try:
            os.unlink(get_db_path())
        except OSError:
            pass

    def CheckDMLdoesAutoCommitBefore(self):
        self.cur1.execute('create table test(i)')
        self.cur1.execute('insert into test(i) values (5)')
        self.cur1.execute('create table test2(j)')
        self.cur2.execute('select i from test')
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)

    def CheckInsertStartsTransaction(self):
        self.cur1.execute('create table test(i)')
        self.cur1.execute('insert into test(i) values (5)')
        self.cur2.execute('select i from test')
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 0)

    def CheckUpdateStartsTransaction(self):
        self.cur1.execute('create table test(i)')
        self.cur1.execute('insert into test(i) values (5)')
        self.con1.commit()
        self.cur1.execute('update test set i=6')
        self.cur2.execute('select i from test')
        res = self.cur2.fetchone()[0]
        self.failUnlessEqual(res, 5)

    def CheckDeleteStartsTransaction(self):
        self.cur1.execute('create table test(i)')
        self.cur1.execute('insert into test(i) values (5)')
        self.con1.commit()
        self.cur1.execute('delete from test')
        self.cur2.execute('select i from test')
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)

    def CheckReplaceStartsTransaction(self):
        self.cur1.execute('create table test(i)')
        self.cur1.execute('insert into test(i) values (5)')
        self.con1.commit()
        self.cur1.execute('replace into test(i) values (6)')
        self.cur2.execute('select i from test')
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)
        self.failUnlessEqual(res[0][0], 5)

    def CheckToggleAutoCommit(self):
        self.cur1.execute('create table test(i)')
        self.cur1.execute('insert into test(i) values (5)')
        self.con1.isolation_level = None
        self.failUnlessEqual(self.con1.isolation_level, None)
        self.cur2.execute('select i from test')
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)
        self.con1.isolation_level = 'DEFERRED'
        self.failUnlessEqual(self.con1.isolation_level, 'DEFERRED')
        self.cur1.execute('insert into test(i) values (5)')
        self.cur2.execute('select i from test')
        res = self.cur2.fetchall()
        self.failUnlessEqual(len(res), 1)
        return

    def CheckRaiseTimeout(self):
        if sqlite.sqlite_version_info < (3, 2, 2):
            return
        self.cur1.execute('create table test(i)')
        self.cur1.execute('insert into test(i) values (5)')
        try:
            self.cur2.execute('insert into test(i) values (5)')
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError:
            pass
        except:
            self.fail('should have raised an OperationalError')

    def CheckLocking(self):
        """
        This tests the improved concurrency with pysqlite 2.3.4. You needed
        to roll back con2 before you could commit con1.
        """
        if sqlite.sqlite_version_info < (3, 2, 2):
            return
        self.cur1.execute('create table test(i)')
        self.cur1.execute('insert into test(i) values (5)')
        try:
            self.cur2.execute('insert into test(i) values (5)')
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError:
            pass
        except:
            self.fail('should have raised an OperationalError')

        self.con1.commit()


class SpecialCommandTests(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')
        self.cur = self.con.cursor()

    def CheckVacuum(self):
        self.cur.execute('create table test(i)')
        self.cur.execute('insert into test(i) values (5)')
        self.cur.execute('vacuum')

    def CheckDropTable(self):
        self.cur.execute('create table test(i)')
        self.cur.execute('insert into test(i) values (5)')
        self.cur.execute('drop table test')

    def CheckPragma(self):
        self.cur.execute('create table test(i)')
        self.cur.execute('insert into test(i) values (5)')
        self.cur.execute('pragma count_changes=1')

    def tearDown(self):
        self.cur.close()
        self.con.close()


def suite():
    default_suite = unittest.makeSuite(TransactionTests, 'Check')
    special_command_suite = unittest.makeSuite(SpecialCommandTests, 'Check')
    return unittest.TestSuite((default_suite, special_command_suite))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    test()
