# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sqlite3/test/regression.py
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
        self.assertEqual(cur.description[0][0], 'foo bar')
        cur.execute('select 1 as "foo baz"')
        self.assertEqual(cur.description[0][0], 'foo baz')

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
        self.con.execute('create table foo(bar)')
        self.con.execute('drop table foo')
        self.con.execute('create table foo(bar)')

    def CheckEmptyStatement(self):
        self.con.execute('')

    def CheckUnicodeConnect(self):
        con = sqlite.connect(u':memory:')
        con.close()

    def CheckTypeMapUsage(self):
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
        self.assertRaises(TypeError, sqlite.register_adapter, {}, None)
        return

    def CheckSetIsolationLevel(self):
        con = sqlite.connect(':memory:')
        self.assertRaises(UnicodeEncodeError, setattr, con, 'isolation_level', u'\xe9')

    def CheckCursorConstructorCallCheck(self):

        class Cursor(sqlite.Cursor):

            def __init__(self, con):
                pass

        con = sqlite.connect(':memory:')
        cur = Cursor(con)
        try:
            cur.execute('select 4+5').fetchall()
            self.fail('should have raised ProgrammingError')
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail('should have raised ProgrammingError')

    def CheckConnectionConstructorCallCheck(self):

        class Connection(sqlite.Connection):

            def __init__(self, name):
                pass

        con = Connection(':memory:')
        try:
            cur = con.cursor()
            self.fail('should have raised ProgrammingError')
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail('should have raised ProgrammingError')

    def CheckCursorRegistration(self):

        class Connection(sqlite.Connection):

            def cursor(self):
                return Cursor(self)

        class Cursor(sqlite.Cursor):

            def __init__(self, con):
                sqlite.Cursor.__init__(self, con)

        con = Connection(':memory:')
        cur = con.cursor()
        cur.execute('create table foo(x)')
        cur.executemany('insert into foo(x) values (?)', [(3,), (4,), (5,)])
        cur.execute('select x from foo')
        con.rollback()
        try:
            cur.fetchall()
            self.fail('should have raised InterfaceError')
        except sqlite.InterfaceError:
            pass
        except:
            self.fail('should have raised InterfaceError')

    def CheckAutoCommit(self):
        con = sqlite.connect(':memory:', isolation_level=None)
        return

    def CheckPragmaAutocommit(self):
        cur = self.con.cursor()
        cur.execute('create table foo(bar)')
        cur.execute('insert into foo(bar) values (5)')
        cur.execute('pragma page_size')
        row = cur.fetchone()

    def CheckSetDict(self):

        class NotHashable:

            def __call__(self, *args, **kw):
                pass

            def __hash__(self):
                raise TypeError()

        var = NotHashable()
        self.assertRaises(TypeError, self.con.create_function, var)
        self.assertRaises(TypeError, self.con.create_aggregate, var)
        self.assertRaises(TypeError, self.con.set_authorizer, var)
        self.assertRaises(TypeError, self.con.set_progress_handler, var)

    def CheckConnectionCall(self):
        self.assertRaises(sqlite.Warning, self.con, 1)

    def CheckRecursiveCursorUse(self):
        con = sqlite.connect(':memory:')
        cur = con.cursor()
        cur.execute('create table a (bar)')
        cur.execute('create table b (baz)')

        def foo():
            cur.execute('insert into a (bar) values (?)', (1,))
            yield 1

        with self.assertRaises(sqlite.ProgrammingError):
            cur.executemany('insert into b (baz) values (?)', ((i,) for i in foo()))

    def CheckConvertTimestampMicrosecondPadding(self):
        con = sqlite.connect(':memory:', detect_types=sqlite.PARSE_DECLTYPES)
        cur = con.cursor()
        cur.execute('CREATE TABLE t (x TIMESTAMP)')
        cur.execute("INSERT INTO t (x) VALUES ('2012-04-04 15:06:00.456')")
        cur.execute("INSERT INTO t (x) VALUES ('2012-04-04 15:06:00.123456789')")
        cur.execute('SELECT * FROM t')
        values = [ x[0] for x in cur.fetchall() ]
        self.assertEqual(values, [datetime.datetime(2012, 4, 4, 15, 6, 0, 456000), datetime.datetime(2012, 4, 4, 15, 6, 0, 123456)])

    def CheckInvalidIsolationLevelType(self):
        self.assertRaises(TypeError, sqlite.connect, ':memory:', isolation_level=123)


def suite():
    regression_suite = unittest.makeSuite(RegressionTests, 'Check')
    return unittest.TestSuite((regression_suite,))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    test()
