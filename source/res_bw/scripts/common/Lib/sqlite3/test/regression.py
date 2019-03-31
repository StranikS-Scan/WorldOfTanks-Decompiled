# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sqlite3/test/regression.py
# Compiled at: 2010-05-25 20:46:16
import datetime
import unittest
import sqlite3 as sqlite

class RegressionTests(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')

    def tearDown(self):
        self.con.close()

    def CheckPragmaUserVersion(self):
        cur = self.con.cursor()
        cur.execute('pragma user_version')

    def CheckPragmaSchemaVersion(self):
        con = sqlite.connect(':memory:', detect_types=sqlite.PARSE_COLNAMES)
        try:
            cur = self.con.cursor()
            cur.execute('pragma schema_version')
        finally:
            cur.close()
            con.close()

    def CheckStatementReset(self):
        con = sqlite.connect(':memory:', cached_statements=5)
        cursors = [ con.cursor() for x in xrange(5) ]
        cursors[0].execute('create table test(x)')
        for i in range(10):
            cursors[0].executemany('insert into test(x) values (?)', [ (x,) for x in xrange(10) ])

        for i in range(5):
            cursors[i].execute(' ' * i + 'select x from test')

        con.rollback()

    def CheckColumnNameWithSpaces(self):
        cur = self.con.cursor()
        cur.execute('select 1 as "foo bar [datetime]"')
        self.failUnlessEqual(cur.description[0][0], 'foo bar')
        cur.execute('select 1 as "foo baz"')
        self.failUnlessEqual(cur.description[0][0], 'foo baz')

    def CheckStatementAvailable(self):
        con = sqlite.connect(':memory:', detect_types=sqlite.PARSE_DECLTYPES)
        cur = con.cursor()
        cur.execute('select 4 union select 5')
        cur.close()
        cur.fetchone()
        cur.fetchone()

    def CheckStatementFinalizationOnCloseDb(self):
        con = sqlite.connect(':memory:')
        cursors = []
        for i in range(105):
            cur = con.cursor()
            cursors.append(cur)
            cur.execute('select 1 x union select ' + str(i))

        con.close()

    def CheckOnConflictRollback(self):
        if sqlite.sqlite_version_info < (3, 2, 2):
            return
        con = sqlite.connect(':memory:')
        con.execute('create table foo(x, unique(x) on conflict rollback)')
        con.execute('insert into foo(x) values (1)')
        try:
            con.execute('insert into foo(x) values (1)')
        except sqlite.DatabaseError:
            pass

        con.execute('insert into foo(x) values (2)')
        try:
            con.commit()
        except sqlite.OperationalError:
            self.fail('pysqlite knew nothing about the implicit ROLLBACK')

    def CheckWorkaroundForBuggySqliteTransferBindings(self):
        """
        pysqlite would crash with older SQLite versions unless
        a workaround is implemented.
        """
        self.con.execute('create table foo(bar)')
        self.con.execute('drop table foo')
        self.con.execute('create table foo(bar)')

    def CheckEmptyStatement(self):
        """
        pysqlite used to segfault with SQLite versions 3.5.x. These return NULL
        for "no-operation" statements
        """
        self.con.execute('')

    def CheckUnicodeConnect(self):
        """
        With pysqlite 2.4.0 you needed to use a string or a APSW connection
        object for opening database connections.
        
        Formerly, both bytestrings and unicode strings used to work.
        
        Let's make sure unicode strings work in the future.
        """
        con = sqlite.connect(u':memory:')
        con.close()

    def CheckTypeMapUsage(self):
        """
        pysqlite until 2.4.1 did not rebuild the row_cast_map when recompiling
        a statement. This test exhibits the problem.
        """
        SELECT = 'select * from foo'
        con = sqlite.connect(':memory:', detect_types=sqlite.PARSE_DECLTYPES)
        con.execute('create table foo(bar timestamp)')
        con.execute('insert into foo(bar) values (?)', (datetime.datetime.now(),))
        con.execute(SELECT)
        con.execute('drop table foo')
        con.execute('create table foo(bar integer)')
        con.execute('insert into foo(bar) values (5)')
        con.execute(SELECT)

    def CheckRegisterAdapter(self):
        """
        See issue 3312.
        """
        self.assertRaises(TypeError, sqlite.register_adapter, {}, None)
        return

    def CheckSetIsolationLevel(self):
        """
        See issue 3312.
        """
        con = sqlite.connect(':memory:')
        self.assertRaises(UnicodeEncodeError, setattr, con, 'isolation_level', u'\xe9')


def suite():
    regression_suite = unittest.makeSuite(RegressionTests, 'Check')
    return unittest.TestSuite((regression_suite,))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    test()
