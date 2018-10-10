# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/unittest/loader.py
import os
import re
import sys
import traceback
import types
from functools import cmp_to_key as _CmpToKey
from fnmatch import fnmatch
from . import case, suite
__unittest = True
VALID_MODULE_NAME = re.compile('[_a-z]\\w*\\.py$', re.IGNORECASE)

def _make_failed_import_test(name, suiteClass):
    message = 'Failed to import test module: %s\n%s' % (name, traceback.format_exc())
    return _make_failed_test('ModuleImportFailure', name, ImportError(message), suiteClass)


def _make_failed_load_tests(name, exception, suiteClass):
    return _make_failed_test('LoadTestsFailure', name, exception, suiteClass)


def _make_failed_test(classname, methodname, exception, suiteClass):

    def testFailure(self):
        raise exception

    attrs = {methodname: testFailure}
    TestClass = type(classname, (case.TestCase,), attrs)
    return suiteClass((TestClass(methodname),))


class TestLoader(object):
    testMethodPrefix = 'test'
    sortTestMethodsUsing = cmp
    suiteClass = suite.TestSuite
    _top_level_dir = None

    def loadTestsFromTestCase(self, testCaseClass):
        if issubclass(testCaseClass, suite.TestSuite):
            raise TypeError('Test cases should not be derived from TestSuite. Maybe you meant to derive from TestCase?')
        testCaseNames = self.getTestCaseNames(testCaseClass)
        if not testCaseNames and hasattr(testCaseClass, 'runTest'):
            testCaseNames = ['runTest']
        loaded_suite = self.suiteClass(map(testCaseClass, testCaseNames))
        return loaded_suite

    def loadTestsFromModule(self, module, use_load_tests=True):
        tests = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, case.TestCase):
                tests.append(self.loadTestsFromTestCase(obj))

        load_tests = getattr(module, 'load_tests', None)
        tests = self.suiteClass(tests)
        if use_load_tests and load_tests is not None:
            try:
                return load_tests(self, tests, None)
            except Exception as e:
                return _make_failed_load_tests(module.__name__, e, self.suiteClass)

        return tests

    def loadTestsFromName(self, name, module=None):
        parts = name.split('.')
        if module is None:
            parts_copy = parts[:]
            while parts_copy:
                try:
                    module = __import__('.'.join(parts_copy))
                    break
                except ImportError:
                    del parts_copy[-1]
                    if not parts_copy:
                        raise

            parts = parts[1:]
        obj = module
        for part in parts:
            parent, obj = obj, getattr(obj, part)

        if isinstance(obj, types.ModuleType):
            return self.loadTestsFromModule(obj)
        elif isinstance(obj, type) and issubclass(obj, case.TestCase):
            return self.loadTestsFromTestCase(obj)
        elif isinstance(obj, types.UnboundMethodType) and isinstance(parent, type) and issubclass(parent, case.TestCase):
            name = parts[-1]
            inst = parent(name)
            return self.suiteClass([inst])
        elif isinstance(obj, suite.TestSuite):
            return obj
        else:
            if hasattr(obj, '__call__'):
                test = obj()
                if isinstance(test, suite.TestSuite):
                    return test
                if isinstance(test, case.TestCase):
                    return self.suiteClass([test])
                raise TypeError('calling %s returned %s, not a test' % (obj, test))
            else:
                raise TypeError("don't know how to make test from: %s" % obj)
            return

    def loadTestsFromNames(self, names, module=None):
        suites = [ self.loadTestsFromName(name, module) for name in names ]
        return self.suiteClass(suites)

    def getTestCaseNames(self, testCaseClass):

        def isTestMethod(attrname, testCaseClass=testCaseClass, prefix=self.testMethodPrefix):
            return attrname.startswith(prefix) and hasattr(getattr(testCaseClass, attrname), '__call__')

        testFnNames = filter(isTestMethod, dir(testCaseClass))
        if self.sortTestMethodsUsing:
            testFnNames.sort(key=_CmpToKey(self.sortTestMethodsUsing))
        return testFnNames

    def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        set_implicit_top = False
        if top_level_dir is None and self._top_level_dir is not None:
            top_level_dir = self._top_level_dir
        elif top_level_dir is None:
            set_implicit_top = True
            top_level_dir = start_dir
        top_level_dir = os.path.abspath(top_level_dir)
        if top_level_dir not in sys.path:
            sys.path.insert(0, top_level_dir)
        self._top_level_dir = top_level_dir
        is_not_importable = False
        if os.path.isdir(os.path.abspath(start_dir)):
            start_dir = os.path.abspath(start_dir)
            if start_dir != top_level_dir:
                is_not_importable = not os.path.isfile(os.path.join(start_dir, '__init__.py'))
        else:
            try:
                __import__(start_dir)
            except ImportError:
                is_not_importable = True
            else:
                the_module = sys.modules[start_dir]
                top_part = start_dir.split('.')[0]
                start_dir = os.path.abspath(os.path.dirname(the_module.__file__))
                if set_implicit_top:
                    self._top_level_dir = self._get_directory_containing_module(top_part)
                    sys.path.remove(top_level_dir)

        if is_not_importable:
            raise ImportError('Start directory is not importable: %r' % start_dir)
        tests = list(self._find_tests(start_dir, pattern))
        return self.suiteClass(tests)

    def _get_directory_containing_module(self, module_name):
        module = sys.modules[module_name]
        full_path = os.path.abspath(module.__file__)
        if os.path.basename(full_path).lower().startswith('__init__.py'):
            return os.path.dirname(os.path.dirname(full_path))
        else:
            return os.path.dirname(full_path)

    def _get_name_from_path(self, path):
        path = os.path.splitext(os.path.normpath(path))[0]
        _relpath = os.path.relpath(path, self._top_level_dir)
        name = _relpath.replace(os.path.sep, '.')
        return name

    def _get_module_from_name(self, name):
        __import__(name)
        return sys.modules[name]

    def _match_path(self, path, full_path, pattern):
        return fnmatch(path, pattern)

    def _find_tests(self, start_dir, pattern):
        paths = os.listdir(start_dir)
        for path in paths:
            full_path = os.path.join(start_dir, path)
            if os.path.isfile(full_path):
                if not VALID_MODULE_NAME.match(path):
                    continue
                if not self._match_path(path, full_path, pattern):
                    continue
                name = self._get_name_from_path(full_path)
                try:
                    module = self._get_module_from_name(name)
                except:
                    yield _make_failed_import_test(name, self.suiteClass)
                else:
                    mod_file = os.path.abspath(getattr(module, '__file__', full_path))
                    realpath = os.path.splitext(os.path.realpath(mod_file))[0]
                    fullpath_noext = os.path.splitext(os.path.realpath(full_path))[0]
                    if realpath.lower() != fullpath_noext.lower():
                        module_dir = os.path.dirname(realpath)
                        mod_name = os.path.splitext(os.path.basename(full_path))[0]
                        expected_dir = os.path.dirname(full_path)
                        msg = '%r module incorrectly imported from %r. Expected %r. Is this module globally installed?'
                        raise ImportError(msg % (mod_name, module_dir, expected_dir))
                    yield self.loadTestsFromModule(module)

            if os.path.isdir(full_path):
                if not os.path.isfile(os.path.join(full_path, '__init__.py')):
                    continue
                load_tests = None
                tests = None
                if fnmatch(path, pattern):
                    name = self._get_name_from_path(full_path)
                    package = self._get_module_from_name(name)
                    load_tests = getattr(package, 'load_tests', None)
                    tests = self.loadTestsFromModule(package, use_load_tests=False)
                if load_tests is None:
                    if tests is not None:
                        yield tests
                    for test in self._find_tests(full_path, pattern):
                        yield test

                else:
                    try:
                        yield load_tests(self, tests, pattern)
                    except Exception as e:
                        yield _make_failed_load_tests(package.__name__, e, self.suiteClass)

        return


defaultTestLoader = TestLoader()

def _makeLoader(prefix, sortUsing, suiteClass=None):
    loader = TestLoader()
    loader.sortTestMethodsUsing = sortUsing
    loader.testMethodPrefix = prefix
    if suiteClass:
        loader.suiteClass = suiteClass
    return loader


def getTestCaseNames(testCaseClass, prefix, sortUsing=cmp):
    return _makeLoader(prefix, sortUsing).getTestCaseNames(testCaseClass)


def makeSuite(testCaseClass, prefix='test', sortUsing=cmp, suiteClass=suite.TestSuite):
    return _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromTestCase(testCaseClass)


def findTestCases(module, prefix='test', sortUsing=cmp, suiteClass=suite.TestSuite):
    return _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromModule(module)
