# Embedded file name: scripts/common/Lib/lib-tk/test/test_ttk/test_functions.py
import sys
import unittest
import ttk

class MockTclObj(object):
    typename = 'test'

    def __init__(self, val):
        self.val = val

    def __str__(self):
        return unicode(self.val)


class MockStateSpec(object):
    typename = 'StateSpec'

    def __init__(self, *args):
        self.val = args

    def __str__(self):
        return ' '.join(self.val)


class InternalFunctionsTest(unittest.TestCase):

    def test_format_optdict(self):

        def check_against(fmt_opts, result):
            for i in range(0, len(fmt_opts), 2):
                self.assertEqual(result.pop(fmt_opts[i]), fmt_opts[i + 1])

            if result:
                self.fail('result still got elements: %s' % result)

        self.assertFalse(ttk._format_optdict({}))
        check_against(ttk._format_optdict({'fg': 'blue',
         'padding': [1,
                     2,
                     3,
                     4]}), {'-fg': 'blue',
         '-padding': '1 2 3 4'})
        check_against(ttk._format_optdict({'test': (1, 2, '', 0)}), {'-test': '1 2 {} 0'})
        check_against(ttk._format_optdict({'test': {'left': 'as is'}}), {'-test': {'left': 'as is'}})
        check_against(ttk._format_optdict({'test': [1,
                  -1,
                  '',
                  '2m',
                  0],
         'test2': 3,
         'test3': '',
         'test4': 'abc def',
         'test5': '"abc"',
         'test6': '{}',
         'test7': '} -spam {'}, script=True), {'-test': '{1 -1 {} 2m 0}',
         '-test2': '3',
         '-test3': '{}',
         '-test4': '{abc def}',
         '-test5': '{"abc"}',
         '-test6': '\\{\\}',
         '-test7': '\\}\\ -spam\\ \\{'})
        opts = {u'\u03b1\u03b2\u03b3': True,
         u'\xe1': False}
        orig_opts = opts.copy()
        check_against(ttk._format_optdict(opts), {u'-\u03b1\u03b2\u03b3': True,
         u'-\xe1': False})
        self.assertEqual(opts, orig_opts)
        check_against(ttk._format_optdict({'option': ('one two', 'three')}), {'-option': '{one two} three'})
        check_against(ttk._format_optdict({'option': ('one\ttwo', 'three')}), {'-option': '{one\ttwo} three'})
        check_against(ttk._format_optdict({'option': ('', 'one')}), {'-option': '{} one'})
        check_against(ttk._format_optdict({'option': ('one} {two', 'three')}), {'-option': 'one\\}\\ \\{two three'})
        check_against(ttk._format_optdict({'option': ('"one"', 'two')}), {'-option': '{"one"} two'})
        check_against(ttk._format_optdict({'option': ('{one}', 'two')}), {'-option': '\\{one\\} two'})
        amount_opts = len(ttk._format_optdict(opts, ignore=u'\xe1')) // 2
        self.assertEqual(amount_opts, len(opts) - 1)
        amount_opts = len(ttk._format_optdict(opts, ignore=(u'\xe1', 'b'))) // 2
        self.assertEqual(amount_opts, len(opts) - 1)
        self.assertFalse(ttk._format_optdict(opts, ignore=opts.keys()))

    def test_format_mapdict(self):
        opts = {'a': [('b', 'c', 'val'), ('d', 'otherval'), ('', 'single')]}
        result = ttk._format_mapdict(opts)
        self.assertEqual(len(result), len(opts.keys()) * 2)
        self.assertEqual(result, ('-a', '{b c} val d otherval {} single'))
        self.assertEqual(ttk._format_mapdict(opts, script=True), ('-a', '{{b c} val d otherval {} single}'))
        self.assertEqual(ttk._format_mapdict({2: []}), ('-2', ''))
        opts = {u'\xfc\xf1\xed\u0107\xf3d\xe8': [(u'\xe1', u'v\xe3l')]}
        result = ttk._format_mapdict(opts)
        self.assertEqual(result, (u'-\xfc\xf1\xed\u0107\xf3d\xe8', u'\xe1 v\xe3l'))
        valid = {'opt': [('', u'', 'hi')]}
        self.assertEqual(ttk._format_mapdict(valid), ('-opt', '{ } hi'))
        invalid = {'opt': [(1, 2, 'valid val')]}
        self.assertRaises(TypeError, ttk._format_mapdict, invalid)
        invalid = {'opt': [([1], '2', 'valid val')]}
        self.assertRaises(TypeError, ttk._format_mapdict, invalid)
        valid = {'opt': [[1, 'value']]}
        self.assertEqual(ttk._format_mapdict(valid), ('-opt', '1 value'))
        for stateval in (None,
         0,
         False,
         '',
         set()):
            valid = {'opt': [(stateval, 'value')]}
            self.assertEqual(ttk._format_mapdict(valid), ('-opt', '{} value'))

        opts = {'a': None}
        self.assertRaises(TypeError, ttk._format_mapdict, opts)
        self.assertRaises(IndexError, ttk._format_mapdict, {'a': [('invalid',)]})
        return

    def test_format_elemcreate(self):
        self.assertTrue(ttk._format_elemcreate(None), (None, ()))
        self.assertRaises(IndexError, ttk._format_elemcreate, 'image')
        self.assertEqual(ttk._format_elemcreate('image', False, 'test'), ('test ', ()))
        self.assertEqual(ttk._format_elemcreate('image', False, 'test', ('', 'a')), ('test {} a', ()))
        self.assertEqual(ttk._format_elemcreate('image', False, 'test', ('a', 'b', 'c')), ('test {a b} c', ()))
        res = ttk._format_elemcreate('image', False, 'test', ('a', 'b'), a='x', b='y')
        self.assertEqual(res[0], 'test a b')
        self.assertEqual(set(res[1]), {'-a',
         'x',
         '-b',
         'y'})
        self.assertEqual(ttk._format_elemcreate('image', True, 'test', ('a', 'b', 'c', 'd'), x=[2, 3]), ('{test {a b c} d}', '-x {2 3}'))
        self.assertRaises(ValueError, ttk._format_elemcreate, 'vsapi')
        self.assertEqual(ttk._format_elemcreate('vsapi', False, 'a', 'b'), ('a b ', ()))
        self.assertEqual(ttk._format_elemcreate('vsapi', False, 'a', 'b', ('a', 'b', 'c')), ('a b {a b} c', ()))
        self.assertEqual(ttk._format_elemcreate('vsapi', False, 'a', 'b', ('a', 'b'), opt='x'), ('a b a b', ('-opt', 'x')))
        self.assertEqual(ttk._format_elemcreate('vsapi', True, 'a', 'b', ('a', 'b', [1, 2]), opt='x'), ('{a b {a b} {1 2}}', '-opt x'))
        self.assertRaises(IndexError, ttk._format_elemcreate, 'from')
        self.assertEqual(ttk._format_elemcreate('from', False, 'a'), ('a', ()))
        self.assertEqual(ttk._format_elemcreate('from', False, 'a', 'b'), ('a', ('b',)))
        self.assertEqual(ttk._format_elemcreate('from', True, 'a', 'b'), ('{a}', 'b'))
        return

    def test_format_layoutlist(self):

        def sample(indent = 0, indent_size = 2):
            return ttk._format_layoutlist([('a', {'other': [1, 2, 3],
               'children': [('b', {'children': [('c', {'children': [('d', {'nice': 'opt'})],
                                             'something': (1, 2)})]})]})], indent=indent, indent_size=indent_size)[0]

        def sample_expected(indent = 0, indent_size = 2):
            spaces = lambda amount = 0: ' ' * (amount + indent)
            return '%sa -other {1 2 3} -children {\n%sb -children {\n%sc -something {1 2} -children {\n%sd -nice opt\n%s}\n%s}\n%s}' % (spaces(),
             spaces(indent_size),
             spaces(2 * indent_size),
             spaces(3 * indent_size),
             spaces(2 * indent_size),
             spaces(indent_size),
             spaces())

        self.assertEqual(ttk._format_layoutlist([])[0], '')
        smallest = ttk._format_layoutlist([('a', None)], indent=0)
        self.assertEqual(smallest, ttk._format_layoutlist([('a', '')], indent=0))
        self.assertEqual(smallest[0], 'a')
        self.assertEqual(sample(), sample_expected())
        for i in range(4):
            self.assertEqual(sample(i), sample_expected(i))
            self.assertEqual(sample(i, i), sample_expected(i, i))

        self.assertRaises(ValueError, ttk._format_layoutlist, ['bad', 'format'])
        self.assertRaises(TypeError, ttk._format_layoutlist, None)
        self.assertRaises(AttributeError, ttk._format_layoutlist, [('a', 'b')])
        self.assertRaises(ValueError, ttk._format_layoutlist, [('name', {'children': {'a': None}})])
        return

    def test_script_from_settings(self):
        self.assertFalse(ttk._script_from_settings({'name': {'configure': None,
                  'map': None,
                  'element create': None}}))
        self.assertEqual(ttk._script_from_settings({'name': {'layout': None}}), 'ttk::style layout name {\nnull\n}')
        configdict = {u'\u03b1\u03b2\u03b3': True,
         u'\xe1': False}
        self.assertTrue(ttk._script_from_settings({'name': {'configure': configdict}}))
        mapdict = {u'\xfc\xf1\xed\u0107\xf3d\xe8': [(u'\xe1', u'v\xe3l')]}
        self.assertTrue(ttk._script_from_settings({'name': {'map': mapdict}}))
        self.assertRaises(IndexError, ttk._script_from_settings, {'name': {'element create': ['image']}})
        self.assertTrue(ttk._script_from_settings({'name': {'element create': ['image', 'name']}}))
        image = {'thing': {'element create': ['image', 'name', ('state1', 'state2', 'val')]}}
        self.assertEqual(ttk._script_from_settings(image), 'ttk::style element create thing image {name {state1 state2} val} ')
        image['thing']['element create'].append({'opt': 30})
        self.assertEqual(ttk._script_from_settings(image), 'ttk::style element create thing image {name {state1 state2} val} -opt 30')
        image['thing']['element create'][-1]['opt'] = [MockTclObj(3), MockTclObj('2m')]
        self.assertEqual(ttk._script_from_settings(image), 'ttk::style element create thing image {name {state1 state2} val} -opt {3 2m}')
        return

    def test_dict_from_tcltuple(self):
        fakettuple = ('-a', '{1 2 3}', '-something', 'foo')
        self.assertEqual(ttk._dict_from_tcltuple(fakettuple, False), {'-a': '{1 2 3}',
         '-something': 'foo'})
        self.assertEqual(ttk._dict_from_tcltuple(fakettuple), {'a': '{1 2 3}',
         'something': 'foo'})
        self.assertFalse(ttk._dict_from_tcltuple(('single',)))
        sspec = MockStateSpec('a', 'b')
        self.assertEqual(ttk._dict_from_tcltuple(('-a', (sspec, 'val'))), {'a': [('a', 'b', 'val')]})
        self.assertEqual(ttk._dict_from_tcltuple((MockTclObj('-padding'), [MockTclObj('1'), 2, MockTclObj('3m')])), {'padding': [1, 2, '3m']})

    def test_list_from_statespec(self):

        def test_it(sspec, value, res_value, states):
            self.assertEqual(ttk._list_from_statespec((sspec, value)), [states + (res_value,)])

        states_even = tuple(('state%d' % i for i in range(6)))
        statespec = MockStateSpec(*states_even)
        test_it(statespec, 'val', 'val', states_even)
        test_it(statespec, MockTclObj('val'), 'val', states_even)
        states_odd = tuple(('state%d' % i for i in range(5)))
        statespec = MockStateSpec(*states_odd)
        test_it(statespec, 'val', 'val', states_odd)
        test_it(('a', 'b', 'c'), MockTclObj('val'), 'val', ('a', 'b', 'c'))

    def test_list_from_layouttuple(self):
        self.assertFalse(ttk._list_from_layouttuple(()))
        self.assertEqual(ttk._list_from_layouttuple(('name',)), [('name', {})])
        sample_ltuple = ('name', '-option', 'value')
        self.assertEqual(ttk._list_from_layouttuple(sample_ltuple), [('name', {'option': 'value'})])
        self.assertEqual(ttk._list_from_layouttuple(('something', '-children', ())), [('something', {'children': []})])
        ltuple = ('name',
         '-option',
         'niceone',
         '-children',
         ('otherone',
          '-children',
          ('child',),
          '-otheropt',
          'othervalue'))
        self.assertEqual(ttk._list_from_layouttuple(ltuple), [('name', {'option': 'niceone',
           'children': [('otherone', {'otheropt': 'othervalue',
                          'children': [('child', {})]})]})])
        self.assertRaises(ValueError, ttk._list_from_layouttuple, ('name', 'no_minus'))
        self.assertRaises(ValueError, ttk._list_from_layouttuple, ('name', 'no_minus', 'value'))
        self.assertRaises(ValueError, ttk._list_from_layouttuple, ('something', '-children'))
        import Tkinter
        if not Tkinter._default_root or Tkinter._default_root.wantobjects():
            self.assertRaises(ValueError, ttk._list_from_layouttuple, ('something', '-children', 'value'))

    def test_val_or_dict(self):

        def func(opt, val = None):
            if val is None:
                return 'test val'
            else:
                return (opt, val)

        options = {'test': None}
        self.assertEqual(ttk._val_or_dict(options, func), 'test val')
        options = {'test': 3}
        self.assertEqual(ttk._val_or_dict(options, func), options)
        return

    def test_convert_stringval(self):
        tests = ((0, 0),
         ('09', 9),
         ('a', 'a'),
         (u'\xe1\xda', u'\xe1\xda'),
         ([], '[]'),
         (None, 'None'))
        for orig, expected in tests:
            self.assertEqual(ttk._convert_stringval(orig), expected)

        if sys.getdefaultencoding() == 'ascii':
            self.assertRaises(UnicodeDecodeError, ttk._convert_stringval, '\xc3\xa1')
        return None


class TclObjsToPyTest(unittest.TestCase):

    def test_unicode(self):
        adict = {'opt': u'v\xe4l\xfa\xe8'}
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': u'v\xe4l\xfa\xe8'})
        adict['opt'] = MockTclObj(adict['opt'])
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': u'v\xe4l\xfa\xe8'})

    def test_multivalues(self):
        adict = {'opt': [1,
                 2,
                 3,
                 4]}
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': [1,
                 2,
                 3,
                 4]})
        adict['opt'] = [1, 'xm', 3]
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': [1, 'xm', 3]})
        adict['opt'] = (MockStateSpec('a', 'b'), u'v\xe1l\u0169\xe8')
        self.assertEqual(ttk.tclobjs_to_py(adict), {'opt': [('a', 'b', u'v\xe1l\u0169\xe8')]})
        self.assertEqual(ttk.tclobjs_to_py({'x': ['y z']}), {'x': ['y z']})

    def test_nosplit(self):
        self.assertEqual(ttk.tclobjs_to_py({'text': 'some text'}), {'text': 'some text'})


tests_nogui = (InternalFunctionsTest, TclObjsToPyTest)
if __name__ == '__main__':
    from test.test_support import run_unittest
    run_unittest(*tests_nogui)
