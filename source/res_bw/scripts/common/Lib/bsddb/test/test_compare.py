# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/bsddb/test/test_compare.py
# Compiled at: 2010-05-25 20:46:16
"""
TestCases for python DB Btree key comparison function.
"""
import sys, os, re
import test_all
from cStringIO import StringIO
import unittest
from test_all import db, dbshelve, test_support, get_new_environment_path, get_new_database_path
lexical_cmp = cmp

def lowercase_cmp(left, right):
    return cmp(left.lower(), right.lower())


def make_reverse_comparator(cmp):

    def reverse(left, right, delegate=cmp):
        return -delegate(left, right)

    return reverse


_expected_lexical_test_data = ['',
 'CCCP',
 'a',
 'aaa',
 'b',
 'c',
 'cccce',
 'ccccf']
_expected_lowercase_test_data = ['',
 'a',
 'aaa',
 'b',
 'c',
 'CC',
 'cccce',
 'ccccf',
 'CCCP']

class ComparatorTests(unittest.TestCase):

    def comparator_test_helper(self, comparator, expected_data):
        data = expected_data[:]
        import sys
        if sys.version_info[0] < 3:
            if sys.version_info[:3] < (2, 4, 0):
                data.sort(comparator)
            else:
                data.sort(cmp=comparator)
        else:
            data2 = []
            for i in data:
                for j, k in enumerate(data2):
                    r = comparator(k, i)
                    if r == 1:
                        data2.insert(j, i)
                        break
                else:
                    data2.append(i)

            data = data2
        self.failUnless(data == expected_data, "comparator `%s' is not right: %s vs. %s" % (comparator, expected_data, data))

    def test_lexical_comparator(self):
        self.comparator_test_helper(lexical_cmp, _expected_lexical_test_data)

    def test_reverse_lexical_comparator(self):
        rev = _expected_lexical_test_data[:]
        rev.reverse()
        self.comparator_test_helper(make_reverse_comparator(lexical_cmp), rev)

    def test_lowercase_comparator(self):
        self.comparator_test_helper(lowercase_cmp, _expected_lowercase_test_data)


class AbstractBtreeKeyCompareTestCase(unittest.TestCase):
    env = None
    db = None

    def setUp(self):
        self.filename = self.__class__.__name__ + '.db'
        self.homeDir = get_new_environment_path()
        env = db.DBEnv()
        env.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_THREAD)
        self.env = env

    def tearDown(self):
        self.closeDB()
        if self.env is not None:
            self.env.close()
            self.env = None
        test_support.rmtree(self.homeDir)
        return

    def addDataToDB(self, data):
        i = 0
        for item in data:
            self.db.put(item, str(i))
            i = i + 1

    def createDB(self, key_comparator):
        self.db = db.DB(self.env)
        self.setupDB(key_comparator)
        self.db.open(self.filename, 'test', db.DB_BTREE, db.DB_CREATE)

    def setupDB(self, key_comparator):
        self.db.set_bt_compare(key_comparator)

    def closeDB(self):
        if self.db is not None:
            self.db.close()
            self.db = None
        return

    def startTest(self):
        pass

    def finishTest(self, expected=None):
        if expected is not None:
            self.check_results(expected)
        self.closeDB()
        return

    def check_results(self, expected):
        curs = self.db.cursor()
        try:
            index = 0
            rec = curs.first()
            while 1:
                key, ignore = rec and rec
                self.failUnless(index < len(expected), 'to many values returned from cursor')
                self.failUnless(expected[index] == key, "expected value `%s' at %d but got `%s'" % (expected[index], index, key))
                index = index + 1
                rec = curs.next()

            self.failUnless(index == len(expected), 'not enough values returned from cursor')
        finally:
            curs.close()


class BtreeKeyCompareTestCase(AbstractBtreeKeyCompareTestCase):

    def runCompareTest(self, comparator, data):
        self.startTest()
        self.createDB(comparator)
        self.addDataToDB(data)
        self.finishTest(data)

    def test_lexical_ordering(self):
        self.runCompareTest(lexical_cmp, _expected_lexical_test_data)

    def test_reverse_lexical_ordering(self):
        expected_rev_data = _expected_lexical_test_data[:]
        expected_rev_data.reverse()
        self.runCompareTest(make_reverse_comparator(lexical_cmp), expected_rev_data)

    def test_compare_function_useless(self):
        self.startTest()

        def socialist_comparator(l, r):
            pass

        self.createDB(socialist_comparator)
        self.addDataToDB(['b', 'a', 'd'])
        self.finishTest(['b'])


class BtreeExceptionsTestCase(AbstractBtreeKeyCompareTestCase):

    def test_raises_non_callable(self):
        self.startTest()
        self.assertRaises(TypeError, self.createDB, 'abc')
        self.assertRaises(TypeError, self.createDB, None)
        self.finishTest()
        return

    def test_set_bt_compare_with_function(self):
        self.startTest()
        self.createDB(lexical_cmp)
        self.finishTest()

    def check_results(self, results):
        pass

    def test_compare_function_incorrect(self):
        self.startTest()

        def bad_comparator(l, r):
            pass

        self.assertRaises(TypeError, self.createDB, bad_comparator)
        self.finishTest()

    def verifyStderr(self, method, successRe):
        """
        Call method() while capturing sys.stderr output internally and
        call self.fail() if successRe.search() does not match the stderr
        output.  This is used to test for uncatchable exceptions.
        """
        stdErr = sys.stderr
        sys.stderr = StringIO()
        try:
            method()
        finally:
            temp = sys.stderr
            sys.stderr = stdErr
            errorOut = temp.getvalue()
            if not successRe.search(errorOut):
                self.fail('unexpected stderr output:\n' + errorOut)

    def _test_compare_function_exception(self):
        self.startTest()

        def bad_comparator(l, r):
            if l == r:
                return 0
            raise RuntimeError, "i'm a naughty comparison function"

        self.createDB(bad_comparator)
        self.addDataToDB(['a', 'b', 'c'])
        self.finishTest()

    def test_compare_function_exception(self):
        self.verifyStderr(self._test_compare_function_exception, re.compile('(^RuntimeError:.* naughty.*){2}', re.M | re.S))

    def _test_compare_function_bad_return(self):
        self.startTest()

        def bad_comparator(l, r):
            if l == r:
                return 0
            return l

        self.createDB(bad_comparator)
        self.addDataToDB(['a', 'b', 'c'])
        self.finishTest()

    def test_compare_function_bad_return(self):
        self.verifyStderr(self._test_compare_function_bad_return, re.compile('(^TypeError:.* return an int.*){2}', re.M | re.S))

    def test_cannot_assign_twice(self):

        def my_compare(a, b):
            pass

        self.startTest()
        self.createDB(my_compare)
        try:
            self.db.set_bt_compare(my_compare)
            self.assert_(0, 'this set should fail')
        except RuntimeError as msg:
            pass


def test_suite():
    res = unittest.TestSuite()
    res.addTest(unittest.makeSuite(ComparatorTests))
    res.addTest(unittest.makeSuite(BtreeExceptionsTestCase))
    res.addTest(unittest.makeSuite(BtreeKeyCompareTestCase))
    return res


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
