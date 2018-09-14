# Embedded file name: scripts/common/Lib/json/tests/test_indent.py
import textwrap
from StringIO import StringIO
from json.tests import PyTest, CTest

class TestIndent(object):

    def test_indent(self):
        h = [['blorpie'],
         ['whoops'],
         [],
         'd-shtaeou',
         'd-nthiouh',
         'i-vhbjkhnth',
         {'nifty': 87},
         {'field': 'yes',
          'morefield': False}]
        expect = textwrap.dedent('        [\n          [\n            "blorpie"\n          ],\n          [\n            "whoops"\n          ],\n          [],\n          "d-shtaeou",\n          "d-nthiouh",\n          "i-vhbjkhnth",\n          {\n            "nifty": 87\n          },\n          {\n            "field": "yes",\n            "morefield": false\n          }\n        ]')
        d1 = self.dumps(h)
        d2 = self.dumps(h, indent=2, sort_keys=True, separators=(',', ': '))
        h1 = self.loads(d1)
        h2 = self.loads(d2)
        self.assertEqual(h1, h)
        self.assertEqual(h2, h)
        self.assertEqual(d2, expect)

    def test_indent0(self):
        h = {3: 1}

        def check(indent, expected):
            d1 = self.dumps(h, indent=indent)
            self.assertEqual(d1, expected)
            sio = StringIO()
            self.json.dump(h, sio, indent=indent)
            self.assertEqual(sio.getvalue(), expected)

        check(0, '{\n"3": 1\n}')
        check(None, '{"3": 1}')
        return


class TestPyIndent(TestIndent, PyTest):
    pass


class TestCIndent(TestIndent, CTest):
    pass
