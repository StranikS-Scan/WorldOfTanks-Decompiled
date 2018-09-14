# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/json/tests/test_recursion.py
from json.tests import PyTest, CTest

class JSONTestObject:
    pass


class TestRecursion(object):

    def test_listrecursion(self):
        x = []
        x.append(x)
        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on list recursion")

        x = []
        y = [x]
        x.append(y)
        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on alternating list recursion")

        y = []
        x = [y, y]
        self.dumps(x)

    def test_dictrecursion(self):
        x = {}
        x['test'] = x
        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on dict recursion")

        x = {}
        y = {'a': x,
         'b': x}
        self.dumps(x)

    def test_defaultrecursion(self):

        class RecursiveJSONEncoder(self.json.JSONEncoder):
            recurse = False

            def default(self, o):
                if o is JSONTestObject:
                    if self.recurse:
                        return [JSONTestObject]
                    else:
                        return 'JSONTestObject'
                return pyjson.JSONEncoder.default(o)

        enc = RecursiveJSONEncoder()
        self.assertEqual(enc.encode(JSONTestObject), '"JSONTestObject"')
        enc.recurse = True
        try:
            enc.encode(JSONTestObject)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on default recursion")

    def test_highly_nested_objects_decoding(self):
        with self.assertRaises(RuntimeError):
            self.loads('{"a":' * 100000 + '1' + '}' * 100000)
        with self.assertRaises(RuntimeError):
            self.loads('{"a":' * 100000 + '[1]' + '}' * 100000)
        with self.assertRaises(RuntimeError):
            self.loads('[' * 100000 + '1' + ']' * 100000)
        with self.assertRaises(RuntimeError):
            self.loads(u'{"a":' * 100000 + u'1' + u'}' * 100000)
        with self.assertRaises(RuntimeError):
            self.loads(u'{"a":' * 100000 + u'[1]' + u'}' * 100000)
        with self.assertRaises(RuntimeError):
            self.loads(u'[' * 100000 + u'1' + u']' * 100000)

    def test_highly_nested_objects_encoding(self):
        l, d = [], {}
        for x in xrange(100000):
            l, d = [l], {'k': d}

        with self.assertRaises(RuntimeError):
            self.dumps(l)
        with self.assertRaises(RuntimeError):
            self.dumps(d)

    def test_endless_recursion(self):

        class EndlessJSONEncoder(self.json.JSONEncoder):

            def default(self, o):
                """If check_circular is False, this will keep adding another list."""
                return [o]

        with self.assertRaises(RuntimeError):
            EndlessJSONEncoder(check_circular=False).encode(5j)


class TestPyRecursion(TestRecursion, PyTest):
    pass


class TestCRecursion(TestRecursion, CTest):
    pass
