# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sqlite3/test/factory.py
# Compiled at: 2010-05-25 20:46:16
import unittest
import sqlite3 as sqlite

class MyConnection(sqlite.Connection):

    def __init__(self, *args, **kwargs):
        sqlite.Connection.__init__(self, *args, **kwargs)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]

    return d


class MyCursor(sqlite.Cursor):

    def __init__(self, *args, **kwargs):
        sqlite.Cursor.__init__(self, *args, **kwargs)
        self.row_factory = dict_factory


class ConnectionFactoryTests(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:', factory=MyConnection)

    def tearDown(self):
        self.con.close()

    def CheckIsInstance(self):
        self.failUnless(isinstance(self.con, MyConnection), 'connection is not instance of MyConnection')


class CursorFactoryTests(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')

    def tearDown(self):
        self.con.close()

    def CheckIsInstance(self):
        cur = self.con.cursor(factory=MyCursor)
        self.failUnless(isinstance(cur, MyCursor), 'cursor is not instance of MyCursor')


class RowFactoryTestsBackwardsCompat(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')

    def CheckIsProducedByFactory(self):
        cur = self.con.cursor(factory=MyCursor)
        cur.execute('select 4+5 as foo')
        row = cur.fetchone()
        self.failUnless(isinstance(row, dict), 'row is not instance of dict')
        cur.close()

    def tearDown(self):
        self.con.close()


class RowFactoryTests(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')

    def CheckCustomFactory(self):
        self.con.row_factory = lambda cur, row: list(row)
        row = self.con.execute('select 1, 2').fetchone()
        self.failUnless(isinstance(row, list), 'row is not instance of list')

    def CheckSqliteRowIndex(self):
        self.con.row_factory = sqlite.Row
        row = self.con.execute('select 1 as a, 2 as b').fetchone()
        self.failUnless(isinstance(row, sqlite.Row), 'row is not instance of sqlite.Row')
        col1, col2 = row['a'], row['b']
        self.failUnless(col1 == 1, "by name: wrong result for column 'a'")
        self.failUnless(col2 == 2, "by name: wrong result for column 'a'")
        col1, col2 = row['A'], row['B']
        self.failUnless(col1 == 1, "by name: wrong result for column 'A'")
        self.failUnless(col2 == 2, "by name: wrong result for column 'B'")
        col1, col2 = row[0], row[1]
        self.failUnless(col1 == 1, 'by index: wrong result for column 0')
        self.failUnless(col2 == 2, 'by index: wrong result for column 1')

    def CheckSqliteRowIter(self):
        """Checks if the row object is iterable"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute('select 1 as a, 2 as b').fetchone()
        for col in row:
            pass

    def CheckSqliteRowAsTuple(self):
        """Checks if the row object can be converted to a tuple"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute('select 1 as a, 2 as b').fetchone()
        t = tuple(row)

    def CheckSqliteRowAsDict(self):
        """Checks if the row object can be correctly converted to a dictionary"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute('select 1 as a, 2 as b').fetchone()
        d = dict(row)
        self.failUnlessEqual(d['a'], row['a'])
        self.failUnlessEqual(d['b'], row['b'])

    def CheckSqliteRowHashCmp(self):
        """Checks if the row object compares and hashes correctly"""
        self.con.row_factory = sqlite.Row
        row_1 = self.con.execute('select 1 as a, 2 as b').fetchone()
        row_2 = self.con.execute('select 1 as a, 2 as b').fetchone()
        row_3 = self.con.execute('select 1 as a, 3 as b').fetchone()
        self.failUnless(row_1 == row_1)
        self.failUnless(row_1 == row_2)
        self.failUnless(row_2 != row_3)
        self.failIf(row_1 != row_1)
        self.failIf(row_1 != row_2)
        self.failIf(row_2 == row_3)
        self.failUnlessEqual(row_1, row_2)
        self.failUnlessEqual(hash(row_1), hash(row_2))
        self.failIfEqual(row_1, row_3)
        self.failIfEqual(hash(row_1), hash(row_3))

    def tearDown(self):
        self.con.close()


class TextFactoryTests(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')

    def CheckUnicode(self):
        austria = unicode('\xd6sterreich', 'latin1')
        row = self.con.execute('select ?', (austria,)).fetchone()
        self.failUnless(type(row[0]) == unicode, 'type of row[0] must be unicode')

    def CheckString(self):
        self.con.text_factory = str
        austria = unicode('\xd6sterreich', 'latin1')
        row = self.con.execute('select ?', (austria,)).fetchone()
        self.failUnless(type(row[0]) == str, 'type of row[0] must be str')
        self.failUnless(row[0] == austria.encode('utf-8'), 'column must equal original data in UTF-8')

    def CheckCustom(self):
        self.con.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
        austria = unicode('\xd6sterreich', 'latin1')
        row = self.con.execute('select ?', (austria.encode('latin1'),)).fetchone()
        self.failUnless(type(row[0]) == unicode, 'type of row[0] must be unicode')
        self.failUnless(row[0].endswith(u'reich'), 'column must contain original data')

    def CheckOptimizedUnicode(self):
        self.con.text_factory = sqlite.OptimizedUnicode
        austria = unicode('\xd6sterreich', 'latin1')
        germany = unicode('Deutchland')
        a_row = self.con.execute('select ?', (austria,)).fetchone()
        d_row = self.con.execute('select ?', (germany,)).fetchone()
        self.failUnless(type(a_row[0]) == unicode, 'type of non-ASCII row must be unicode')
        self.failUnless(type(d_row[0]) == str, 'type of ASCII-only row must be str')

    def tearDown(self):
        self.con.close()


def suite():
    connection_suite = unittest.makeSuite(ConnectionFactoryTests, 'Check')
    cursor_suite = unittest.makeSuite(CursorFactoryTests, 'Check')
    row_suite_compat = unittest.makeSuite(RowFactoryTestsBackwardsCompat, 'Check')
    row_suite = unittest.makeSuite(RowFactoryTests, 'Check')
    text_suite = unittest.makeSuite(TextFactoryTests, 'Check')
    return unittest.TestSuite((connection_suite,
     cursor_suite,
     row_suite_compat,
     row_suite,
     text_suite))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    test()
