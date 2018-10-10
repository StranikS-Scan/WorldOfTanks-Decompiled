# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sqlite3/test/userfunctions.py
import unittest
import sqlite3 as sqlite

def func_returntext():
    pass


def func_returnunicode():
    pass


def func_returnint():
    pass


def func_returnfloat():
    pass


def func_returnnull():
    return None


def func_returnblob():
    return buffer('blob')


def func_returnlonglong():
    pass


def func_raiseexception():
    5 // 0


def func_isstring(v):
    return type(v) is unicode


def func_isint(v):
    return type(v) is int


def func_isfloat(v):
    return type(v) is float


def func_isnone(v):
    return type(v) is type(None)


def func_isblob(v):
    return type(v) is buffer


def func_islonglong(v):
    return isinstance(v, (int, long)) and v >= 2147483648L


class AggrNoStep:

    def __init__(self):
        pass

    def finalize(self):
        pass


class AggrNoFinalize:

    def __init__(self):
        pass

    def step(self, x):
        pass


class AggrExceptionInInit:

    def __init__(self):
        5 // 0

    def step(self, x):
        pass

    def finalize(self):
        pass


class AggrExceptionInStep:

    def __init__(self):
        pass

    def step(self, x):
        5 // 0

    def finalize(self):
        pass


class AggrExceptionInFinalize:

    def __init__(self):
        pass

    def step(self, x):
        pass

    def finalize(self):
        5 // 0


class AggrCheckType:

    def __init__(self):
        self.val = None
        return

    def step(self, whichType, val):
        theType = {'str': unicode,
         'int': int,
         'float': float,
         'None': type(None),
         'blob': buffer}
        self.val = int(theType[whichType] is type(val))
        return

    def finalize(self):
        return self.val


class AggrSum:

    def __init__(self):
        self.val = 0.0

    def step(self, val):
        self.val += val

    def finalize(self):
        return self.val


class FunctionTests(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')
        self.con.create_function('returntext', 0, func_returntext)
        self.con.create_function('returnunicode', 0, func_returnunicode)
        self.con.create_function('returnint', 0, func_returnint)
        self.con.create_function('returnfloat', 0, func_returnfloat)
        self.con.create_function('returnnull', 0, func_returnnull)
        self.con.create_function('returnblob', 0, func_returnblob)
        self.con.create_function('returnlonglong', 0, func_returnlonglong)
        self.con.create_function('raiseexception', 0, func_raiseexception)
        self.con.create_function('isstring', 1, func_isstring)
        self.con.create_function('isint', 1, func_isint)
        self.con.create_function('isfloat', 1, func_isfloat)
        self.con.create_function('isnone', 1, func_isnone)
        self.con.create_function('isblob', 1, func_isblob)
        self.con.create_function('islonglong', 1, func_islonglong)

    def tearDown(self):
        self.con.close()

    def CheckFuncErrorOnCreate(self):
        try:
            self.con.create_function('bla', -100, lambda x: 2 * x)
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError:
            pass

    def CheckFuncRefCount(self):

        def getfunc():

            def f():
                pass

            return f

        f = getfunc()
        globals()['foo'] = f
        self.con.create_function('reftest', 0, f)
        cur = self.con.cursor()
        cur.execute('select reftest()')

    def CheckFuncReturnText(self):
        cur = self.con.cursor()
        cur.execute('select returntext()')
        val = cur.fetchone()[0]
        self.assertEqual(type(val), unicode)
        self.assertEqual(val, 'foo')

    def CheckFuncReturnUnicode(self):
        cur = self.con.cursor()
        cur.execute('select returnunicode()')
        val = cur.fetchone()[0]
        self.assertEqual(type(val), unicode)
        self.assertEqual(val, u'bar')

    def CheckFuncReturnInt(self):
        cur = self.con.cursor()
        cur.execute('select returnint()')
        val = cur.fetchone()[0]
        self.assertEqual(type(val), int)
        self.assertEqual(val, 42)

    def CheckFuncReturnFloat(self):
        cur = self.con.cursor()
        cur.execute('select returnfloat()')
        val = cur.fetchone()[0]
        self.assertEqual(type(val), float)
        if val < 3.139 or val > 3.141:
            self.fail('wrong value')

    def CheckFuncReturnNull(self):
        cur = self.con.cursor()
        cur.execute('select returnnull()')
        val = cur.fetchone()[0]
        self.assertEqual(type(val), type(None))
        self.assertEqual(val, None)
        return

    def CheckFuncReturnBlob(self):
        cur = self.con.cursor()
        cur.execute('select returnblob()')
        val = cur.fetchone()[0]
        self.assertEqual(type(val), buffer)
        self.assertEqual(val, buffer('blob'))

    def CheckFuncReturnLongLong(self):
        cur = self.con.cursor()
        cur.execute('select returnlonglong()')
        val = cur.fetchone()[0]
        self.assertEqual(val, 2147483648L)

    def CheckFuncException(self):
        cur = self.con.cursor()
        try:
            cur.execute('select raiseexception()')
            cur.fetchone()
            self.fail('should have raised OperationalError')
        except sqlite.OperationalError as e:
            self.assertEqual(e.args[0], 'user-defined function raised exception')

    def CheckParamString(self):
        cur = self.con.cursor()
        cur.execute('select isstring(?)', ('foo',))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamInt(self):
        cur = self.con.cursor()
        cur.execute('select isint(?)', (42,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamFloat(self):
        cur = self.con.cursor()
        cur.execute('select isfloat(?)', (3.14,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamNone(self):
        cur = self.con.cursor()
        cur.execute('select isnone(?)', (None,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)
        return None

    def CheckParamBlob(self):
        cur = self.con.cursor()
        cur.execute('select isblob(?)', (buffer('blob'),))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckParamLongLong(self):
        cur = self.con.cursor()
        cur.execute('select islonglong(?)', (4398046511104L,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)


class AggregateTests(unittest.TestCase):

    def setUp(self):
        self.con = sqlite.connect(':memory:')
        cur = self.con.cursor()
        cur.execute('\n            create table test(\n                t text,\n                i integer,\n                f float,\n                n,\n                b blob\n                )\n            ')
        cur.execute('insert into test(t, i, f, n, b) values (?, ?, ?, ?, ?)', ('foo',
         5,
         3.14,
         None,
         buffer('blob')))
        self.con.create_aggregate('nostep', 1, AggrNoStep)
        self.con.create_aggregate('nofinalize', 1, AggrNoFinalize)
        self.con.create_aggregate('excInit', 1, AggrExceptionInInit)
        self.con.create_aggregate('excStep', 1, AggrExceptionInStep)
        self.con.create_aggregate('excFinalize', 1, AggrExceptionInFinalize)
        self.con.create_aggregate('checkType', 2, AggrCheckType)
        self.con.create_aggregate('mysum', 1, AggrSum)
        return

    def tearDown(self):
        pass

    def CheckAggrErrorOnCreate(self):
        try:
            self.con.create_function('bla', -100, AggrSum)
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError:
            pass

    def CheckAggrNoStep(self):
        cur = self.con.cursor()
        try:
            cur.execute('select nostep(t) from test')
            self.fail('should have raised an AttributeError')
        except AttributeError as e:
            self.assertEqual(e.args[0], "AggrNoStep instance has no attribute 'step'")

    def CheckAggrNoFinalize(self):
        cur = self.con.cursor()
        try:
            cur.execute('select nofinalize(t) from test')
            val = cur.fetchone()[0]
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError as e:
            self.assertEqual(e.args[0], "user-defined aggregate's 'finalize' method raised error")

    def CheckAggrExceptionInInit(self):
        cur = self.con.cursor()
        try:
            cur.execute('select excInit(t) from test')
            val = cur.fetchone()[0]
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError as e:
            self.assertEqual(e.args[0], "user-defined aggregate's '__init__' method raised error")

    def CheckAggrExceptionInStep(self):
        cur = self.con.cursor()
        try:
            cur.execute('select excStep(t) from test')
            val = cur.fetchone()[0]
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError as e:
            self.assertEqual(e.args[0], "user-defined aggregate's 'step' method raised error")

    def CheckAggrExceptionInFinalize(self):
        cur = self.con.cursor()
        try:
            cur.execute('select excFinalize(t) from test')
            val = cur.fetchone()[0]
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError as e:
            self.assertEqual(e.args[0], "user-defined aggregate's 'finalize' method raised error")

    def CheckAggrCheckParamStr(self):
        cur = self.con.cursor()
        cur.execute("select checkType('str', ?)", ('foo',))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckParamInt(self):
        cur = self.con.cursor()
        cur.execute("select checkType('int', ?)", (42,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckParamFloat(self):
        cur = self.con.cursor()
        cur.execute("select checkType('float', ?)", (3.14,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckParamNone(self):
        cur = self.con.cursor()
        cur.execute("select checkType('None', ?)", (None,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)
        return None

    def CheckAggrCheckParamBlob(self):
        cur = self.con.cursor()
        cur.execute("select checkType('blob', ?)", (buffer('blob'),))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    def CheckAggrCheckAggrSum(self):
        cur = self.con.cursor()
        cur.execute('delete from test')
        cur.executemany('insert into test(i) values (?)', [(10,), (20,), (30,)])
        cur.execute('select mysum(i) from test')
        val = cur.fetchone()[0]
        self.assertEqual(val, 60)


class AuthorizerTests(unittest.TestCase):

    @staticmethod
    def authorizer_cb(action, arg1, arg2, dbname, source):
        if action != sqlite.SQLITE_SELECT:
            return sqlite.SQLITE_DENY
        return sqlite.SQLITE_DENY if arg2 == 'c2' or arg1 == 't2' else sqlite.SQLITE_OK

    def setUp(self):
        self.con = sqlite.connect(':memory:')
        self.con.executescript('\n            create table t1 (c1, c2);\n            create table t2 (c1, c2);\n            insert into t1 (c1, c2) values (1, 2);\n            insert into t2 (c1, c2) values (4, 5);\n            ')
        self.con.execute('select c2 from t2')
        self.con.set_authorizer(self.authorizer_cb)

    def tearDown(self):
        pass

    def test_table_access(self):
        try:
            self.con.execute('select * from t2')
        except sqlite.DatabaseError as e:
            if not e.args[0].endswith('prohibited'):
                self.fail('wrong exception text: %s' % e.args[0])
            return

        self.fail('should have raised an exception due to missing privileges')

    def test_column_access(self):
        try:
            self.con.execute('select c2 from t1')
        except sqlite.DatabaseError as e:
            if not e.args[0].endswith('prohibited'):
                self.fail('wrong exception text: %s' % e.args[0])
            return

        self.fail('should have raised an exception due to missing privileges')


class AuthorizerRaiseExceptionTests(AuthorizerTests):

    @staticmethod
    def authorizer_cb(action, arg1, arg2, dbname, source):
        if action != sqlite.SQLITE_SELECT:
            raise ValueError
        if arg2 == 'c2' or arg1 == 't2':
            raise ValueError
        return sqlite.SQLITE_OK


class AuthorizerIllegalTypeTests(AuthorizerTests):

    @staticmethod
    def authorizer_cb(action, arg1, arg2, dbname, source):
        if action != sqlite.SQLITE_SELECT:
            return 0.0
        return 0.0 if arg2 == 'c2' or arg1 == 't2' else sqlite.SQLITE_OK


class AuthorizerLargeIntegerTests(AuthorizerTests):

    @staticmethod
    def authorizer_cb(action, arg1, arg2, dbname, source):
        if action != sqlite.SQLITE_SELECT:
            return 4294967296L
        return 4294967296L if arg2 == 'c2' or arg1 == 't2' else sqlite.SQLITE_OK


def suite():
    function_suite = unittest.makeSuite(FunctionTests, 'Check')
    aggregate_suite = unittest.makeSuite(AggregateTests, 'Check')
    authorizer_suite = unittest.makeSuite(AuthorizerTests)
    return unittest.TestSuite((function_suite,
     aggregate_suite,
     authorizer_suite,
     unittest.makeSuite(AuthorizerRaiseExceptionTests),
     unittest.makeSuite(AuthorizerIllegalTypeTests),
     unittest.makeSuite(AuthorizerLargeIntegerTests)))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    test()
