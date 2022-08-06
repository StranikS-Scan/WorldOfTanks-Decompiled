# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sqlite3/test/regression.py
import datetime
import unittest
import sqlite3 as sqlite
import weakref
from test import support

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

        with self.assertRaisesRegexp(sqlite.ProgrammingError, '^Base Cursor\\.__init__ not called\\.$'):
            cur.close()

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

    def CheckNullCharacter(self):
        con = sqlite.connect(':memory:')
        self.assertRaises(ValueError, con, '\x00select 1')
        self.assertRaises(ValueError, con, 'select 1\x00')
        cur = con.cursor()
        self.assertRaises(ValueError, cur.execute, ' \x00select 2')
        self.assertRaises(ValueError, cur.execute, 'select 2\x00')

    def CheckCommitCursorReset(self):
        con = sqlite.connect(':memory:')
        con.executescript('\n        create table t(c);\n        create table t2(c);\n        insert into t values(0);\n        insert into t values(1);\n        insert into t values(2);\n        ')
        self.assertEqual(con.isolation_level, '')
        counter = 0
        for i, row in enumerate(con.execute('select c from t')):
            con.execute('insert into t2(c) values (?)', (i,))
            con.commit()
            if counter == 0:
                self.assertEqual(row[0], 0)
            elif counter == 1:
                self.assertEqual(row[0], 1)
            elif counter == 2:
                self.assertEqual(row[0], 2)
            counter += 1

        self.assertEqual(counter, 3, 'should have returned exactly three rows')

    def CheckBpo31770(self):

        def callback(*args):
            pass

        con = sqlite.connect(':memory:')
        cur = sqlite.Cursor(con)
        ref = weakref.ref(cur, callback)
        cur.__init__(con)
        del cur
        del ref
        support.gc_collect()

    def CheckDelIsolation_levelSegfault(self):
        with self.assertRaises(AttributeError):
            del self.con.isolation_level


class UnhashableFunc():

    def __hash__(self):
        raise TypeError('unhashable type')

    def __init__(self, return_value=None):
        self.calls = 0
        self.return_value = return_value

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.return_value


class UnhashableCallbacksTestCase(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')

    def tearDown(self):
        self.con.close()

    def test_progress_handler(self):
        f = UnhashableFunc(return_value=0)
        with self.assertRaisesRegexp(TypeError, 'unhashable type'):
            self.con.set_progress_handler(f, 1)
        self.con.execute('SELECT 1')
        self.assertFalse(f.calls)

    def test_func(self):
        func_name = 'func_name'
        f = UnhashableFunc()
        with self.assertRaisesRegexp(TypeError, 'unhashable type'):
            self.con.create_function(func_name, 0, f)
        msg = 'no such function: %s' % func_name
        with self.assertRaisesRegexp(sqlite.OperationalError, msg):
            self.con.execute('SELECT %s()' % func_name)
        self.assertFalse(f.calls)

    def test_authorizer(self):
        f = UnhashableFunc(return_value=sqlite.SQLITE_DENY)
        with self.assertRaisesRegexp(TypeError, 'unhashable type'):
            self.con.set_authorizer(f)
        self.con.execute('SELECT 1')
        self.assertFalse(f.calls)

    def test_aggr(self):

        class UnhashableType(type):
            __hash__ = None

        aggr_name = 'aggr_name'
        with self.assertRaisesRegexp(TypeError, 'unhashable type'):
            self.con.create_aggregate(aggr_name, 0, UnhashableType('Aggr', (), {}))
        msg = 'no such function: %s' % aggr_name
        with self.assertRaisesRegexp(sqlite.OperationalError, msg):
            self.con.execute('SELECT %s()' % aggr_name)


def suite():
    regression_suite = unittest.makeSuite(RegressionTests, 'Check')
    return unittest.TestSuite((regression_suite, unittest.makeSuite(UnhashableCallbacksTestCase)))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    test()
