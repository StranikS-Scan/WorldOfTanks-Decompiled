# Embedded file name: scripts/common/Lib/idlelib/idle_test/test_calltips.py
import unittest
import idlelib.CallTips as ct
CTi = ct.CallTips()
import textwrap
import types
import warnings
default_tip = ''

class TC(object):
    """doc"""
    tip = '(ai=None, *args)'

    def __init__(self, ai = None, *b):
        """doc"""
        pass

    __init__.tip = '(self, ai=None, *args)'

    def t1(self):
        """doc"""
        pass

    t1.tip = '(self)'

    def t2(self, ai, b = None):
        """doc"""
        pass

    t2.tip = '(self, ai, b=None)'

    def t3(self, ai, *args):
        """doc"""
        pass

    t3.tip = '(self, ai, *args)'

    def t4(self, *args):
        """doc"""
        pass

    t4.tip = '(self, *args)'

    def t5(self, ai, b = None, *args, **kw):
        """doc"""
        pass

    t5.tip = '(self, ai, b=None, *args, **kwds)'

    def t6(no, self):
        """doc"""
        pass

    t6.tip = '(no, self)'

    def __call__(self, ci):
        """doc"""
        pass

    __call__.tip = '(self, ci)'

    @classmethod
    def cm(cls, a):
        """doc"""
        pass

    @staticmethod
    def sm(b):
        """doc"""
        pass


tc = TC()
signature = ct.get_arg_text

class Get_signatureTest(unittest.TestCase):

    def test_builtins(self):

        class List(list):
            """List() doc"""
            pass

        class SB:
            __call__ = None

        def gtest(obj, out):
            self.assertEqual(signature(obj), out)

        gtest(List, '()\n' + List.__doc__)
        gtest(list.__new__, 'T.__new__(S, ...) -> a new object with type S, a subtype of T')
        gtest(list.__init__, 'x.__init__(...) initializes x; see help(type(x)) for signature')
        append_doc = 'L.append(object) -- append object to end'
        gtest(list.append, append_doc)
        gtest([].append, append_doc)
        gtest(List.append, append_doc)
        gtest(types.MethodType, '()\ninstancemethod(function, instance, class)')
        gtest(SB(), default_tip)

    def test_signature_wrap(self):
        self.assertEqual(signature(textwrap.TextWrapper), "(width=70, initial_indent='', subsequent_indent='', expand_tabs=True,\n    replace_whitespace=True, fix_sentence_endings=False, break_long_words=True,\n    drop_whitespace=True, break_on_hyphens=True)")

    def test_docline_truncation(self):

        def f():
            pass

        f.__doc__ = 'a' * 300
        self.assertEqual(signature(f), '()\n' + 'a' * (ct._MAX_COLS - 3) + '...')

    def test_multiline_docstring(self):
        self.assertEqual(signature(list), "()\nlist() -> new empty list\nlist(iterable) -> new list initialized from iterable's items")

        def f():
            pass

        s = 'a\nb\nc\nd\n'
        f.__doc__ = s + 300 * 'e' + 'f'
        self.assertEqual(signature(f), '()\n' + s + (ct._MAX_COLS - 3) * 'e' + '...')

    def test_functions(self):

        def t1():
            """doc"""
            pass

        t1.tip = '()'

        def t2(a, b = None):
            """doc"""
            pass

        t2.tip = '(a, b=None)'

        def t3(a, *args):
            """doc"""
            pass

        t3.tip = '(a, *args)'

        def t4(*args):
            """doc"""
            pass

        t4.tip = '(*args)'

        def t5(a, b = None, *args, **kwds):
            """doc"""
            pass

        t5.tip = '(a, b=None, *args, **kwds)'
        for func in (t1,
         t2,
         t3,
         t4,
         t5,
         TC):
            self.assertEqual(signature(func), func.tip + '\ndoc')

        return

    def test_methods(self):
        for meth in (TC.t1,
         TC.t2,
         TC.t3,
         TC.t4,
         TC.t5,
         TC.t6,
         TC.__call__):
            self.assertEqual(signature(meth), meth.tip + '\ndoc')

        self.assertEqual(signature(TC.cm), '(a)\ndoc')
        self.assertEqual(signature(TC.sm), '(b)\ndoc')

    def test_bound_methods(self):
        for meth, mtip in ((tc.t1, '()'),
         (tc.t4, '(*args)'),
         (tc.t6, '(self)'),
         (tc.__call__, '(ci)'),
         (tc, '(ci)'),
         (TC.cm, '(a)')):
            self.assertEqual(signature(meth), mtip + '\ndoc')

    def test_starred_parameter(self):

        class C:

            def m1(*args):
                pass

            def m2(**kwds):
                pass

        c = C()
        for meth, mtip in ((C.m1, '(*args)'),
         (c.m1, '(*args)'),
         (C.m2, '(**kwds)'),
         (c.m2, '(**kwds)')):
            self.assertEqual(signature(meth), mtip)

    def test_no_docstring(self):

        def nd(s):
            pass

        TC.nd = nd
        self.assertEqual(signature(nd), '(s)')
        self.assertEqual(signature(TC.nd), '(s)')
        self.assertEqual(signature(tc.nd), '()')

    def test_attribute_exception(self):

        class NoCall(object):

            def __getattr__(self, name):
                raise BaseException

        class Call(NoCall):

            def __call__(self, ci):
                pass

        for meth, mtip in ((NoCall, '()'),
         (Call, '()'),
         (NoCall(), ''),
         (Call(), '(ci)')):
            self.assertEqual(signature(meth), mtip)

    def test_non_callables(self):
        for obj in (0,
         0.0,
         '0',
         '0',
         [],
         {}):
            self.assertEqual(signature(obj), '')


class Get_entityTest(unittest.TestCase):

    def test_bad_entity(self):
        self.assertIsNone(CTi.get_entity('1/0'))

    def test_good_entity(self):
        self.assertIs(CTi.get_entity('int'), int)


class Py2Test(unittest.TestCase):

    def test_paramtuple_float(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            exec 'def f((a,b), c=0.0): pass'
        self.assertEqual(signature(f), '(<tuple>, c=0.0)')


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
