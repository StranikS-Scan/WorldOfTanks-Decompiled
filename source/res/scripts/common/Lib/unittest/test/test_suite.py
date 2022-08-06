# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/unittest/test/test_suite.py
import unittest
import sys
from unittest.test.support import LoggingResult, TestEquality

class Test(object):

    class Foo(unittest.TestCase):

        def test_1(self):
            pass

        def test_2(self):
            pass

        def test_3(self):
            pass

        def runTest(self):
            pass


def _mk_TestSuite(*names):
    return unittest.TestSuite((Test.Foo(n) for n in names))


class Test_TestSuite(unittest.TestCase, TestEquality):
    eq_pairs = [(unittest.TestSuite(), unittest.TestSuite()), (unittest.TestSuite(), unittest.TestSuite([])), (_mk_TestSuite('test_1'), _mk_TestSuite('test_1'))]
    ne_pairs = [(unittest.TestSuite(), _mk_TestSuite('test_1')),
     (unittest.TestSuite([]), _mk_TestSuite('test_1')),
     (_mk_TestSuite('test_1', 'test_2'), _mk_TestSuite('test_1', 'test_3')),
     (_mk_TestSuite('test_1'), _mk_TestSuite('test_2'))]

    def test_init__tests_optional(self):
        suite = unittest.TestSuite()
        self.assertEqual(suite.countTestCases(), 0)

    def test_init__empty_tests(self):
        suite = unittest.TestSuite([])
        self.assertEqual(suite.countTestCases(), 0)

    def test_init__tests_from_any_iterable(self):

        def tests():
            yield unittest.FunctionTestCase(lambda : None)
            yield unittest.FunctionTestCase(lambda : None)

        suite_1 = unittest.TestSuite(tests())
        self.assertEqual(suite_1.countTestCases(), 2)
        suite_2 = unittest.TestSuite(suite_1)
        self.assertEqual(suite_2.countTestCases(), 2)
        suite_3 = unittest.TestSuite(set(suite_1))
        self.assertEqual(suite_3.countTestCases(), 2)

    def test_init__TestSuite_instances_in_tests(self):

        def tests():
            ftc = unittest.FunctionTestCase(lambda : None)
            yield unittest.TestSuite([ftc])
            yield unittest.FunctionTestCase(lambda : None)

        suite = unittest.TestSuite(tests())
        self.assertEqual(suite.countTestCases(), 2)

    def test_iter(self):
        test1 = unittest.FunctionTestCase(lambda : None)
        test2 = unittest.FunctionTestCase(lambda : None)
        suite = unittest.TestSuite((test1, test2))
        self.assertEqual(list(suite), [test1, test2])

    def test_countTestCases_zero_simple(self):
        suite = unittest.TestSuite()
        self.assertEqual(suite.countTestCases(), 0)

    def test_countTestCases_zero_nested(self):

        class Test1(unittest.TestCase):

            def test(self):
                pass

        suite = unittest.TestSuite([unittest.TestSuite()])
        self.assertEqual(suite.countTestCases(), 0)

    def test_countTestCases_simple(self):
        test1 = unittest.FunctionTestCase(lambda : None)
        test2 = unittest.FunctionTestCase(lambda : None)
        suite = unittest.TestSuite((test1, test2))
        self.assertEqual(suite.countTestCases(), 2)

    def test_countTestCases_nested(self):

        class Test1(unittest.TestCase):

            def test1(self):
                pass

            def test2(self):
                pass

        test2 = unittest.FunctionTestCase(lambda : None)
        test3 = unittest.FunctionTestCase(lambda : None)
        child = unittest.TestSuite((Test1('test2'), test2))
        parent = unittest.TestSuite((test3, child, Test1('test1')))
        self.assertEqual(parent.countTestCases(), 4)

    def test_run__empty_suite(self):
        events = []
        result = LoggingResult(events)
        suite = unittest.TestSuite()
        suite.run(result)
        self.assertEqual(events, [])

    def test_run__requires_result(self):
        suite = unittest.TestSuite()
        try:
            suite.run()
        except TypeError:
            pass
        else:
            self.fail('Failed to raise TypeError')

    def test_run(self):
        events = []
        result = LoggingResult(events)

        class LoggingCase(unittest.TestCase):

            def run(self, result):
                events.append('run %s' % self._testMethodName)

            def test1(self):
                pass

            def test2(self):
                pass

        tests = [LoggingCase('test1'), LoggingCase('test2')]
        unittest.TestSuite(tests).run(result)
        self.assertEqual(events, ['run test1', 'run test2'])

    def test_addTest__TestCase(self):

        class Foo(unittest.TestCase):

            def test(self):
                pass

        test = Foo('test')
        suite = unittest.TestSuite()
        suite.addTest(test)
        self.assertEqual(suite.countTestCases(), 1)
        self.assertEqual(list(suite), [test])

    def test_addTest__TestSuite(self):

        class Foo(unittest.TestCase):

            def test(self):
                pass

        suite_2 = unittest.TestSuite([Foo('test')])
        suite = unittest.TestSuite()
        suite.addTest(suite_2)
        self.assertEqual(suite.countTestCases(), 1)
        self.assertEqual(list(suite), [suite_2])

    def test_addTests(self):

        class Foo(unittest.TestCase):

            def test_1(self):
                pass

            def test_2(self):
                pass

        test_1 = Foo('test_1')
        test_2 = Foo('test_2')
        inner_suite = unittest.TestSuite([test_2])

        def gen():
            yield test_1
            yield test_2
            yield inner_suite

        suite_1 = unittest.TestSuite()
        suite_1.addTests(gen())
        self.assertEqual(list(suite_1), list(gen()))
        suite_2 = unittest.TestSuite()
        for t in gen():
            suite_2.addTest(t)

        self.assertEqual(suite_1, suite_2)

    def test_addTest__noniterable(self):
        suite = unittest.TestSuite()
        try:
            suite.addTests(5)
        except TypeError:
            pass
        else:
            self.fail('Failed to raise TypeError')

    def test_addTest__noncallable(self):
        suite = unittest.TestSuite()
        self.assertRaises(TypeError, suite.addTest, 5)

    def test_addTest__casesuiteclass(self):
        suite = unittest.TestSuite()
        self.assertRaises(TypeError, suite.addTest, Test_TestSuite)
        self.assertRaises(TypeError, suite.addTest, unittest.TestSuite)

    def test_addTests__string(self):
        suite = unittest.TestSuite()
        self.assertRaises(TypeError, suite.addTests, 'foo')

    def test_function_in_suite(self):

        def f(_):
            pass

        suite = unittest.TestSuite()
        suite.addTest(f)
        suite.run(unittest.TestResult())

    def test_basetestsuite(self):

        class Test(unittest.TestCase):
            wasSetUp = False
            wasTornDown = False

            @classmethod
            def setUpClass(cls):
                cls.wasSetUp = True

            @classmethod
            def tearDownClass(cls):
                cls.wasTornDown = True

            def testPass(self):
                pass

            def testFail(self):
                fail

        class Module(object):
            wasSetUp = False
            wasTornDown = False

            @staticmethod
            def setUpModule():
                Module.wasSetUp = True

            @staticmethod
            def tearDownModule():
                Module.wasTornDown = True

        Test.__module__ = 'Module'
        sys.modules['Module'] = Module
        self.addCleanup(sys.modules.pop, 'Module')
        suite = unittest.BaseTestSuite()
        suite.addTests([Test('testPass'), Test('testFail')])
        self.assertEqual(suite.countTestCases(), 2)
        result = unittest.TestResult()
        suite.run(result)
        self.assertFalse(Module.wasSetUp)
        self.assertFalse(Module.wasTornDown)
        self.assertFalse(Test.wasSetUp)
        self.assertFalse(Test.wasTornDown)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(result.testsRun, 2)

    def test_overriding_call(self):

        class MySuite(unittest.TestSuite):
            called = False

            def __call__(self, *args, **kw):
                self.called = True
                unittest.TestSuite.__call__(self, *args, **kw)

        suite = MySuite()
        result = unittest.TestResult()
        wrapper = unittest.TestSuite()
        wrapper.addTest(suite)
        wrapper(result)
        self.assertTrue(suite.called)
        self.assertFalse(result._testRunEntered)


if __name__ == '__main__':
    unittest.main()
