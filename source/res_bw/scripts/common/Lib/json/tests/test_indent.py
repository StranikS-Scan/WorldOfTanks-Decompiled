# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/json/tests/test_indent.py
# Compiled at: 2010-08-25 17:58:21
from unittest import TestCase
import json
import textwrap

class TestIndent(TestCase):

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
        d1 = json.dumps(h)
        d2 = json.dumps(h, indent=2, sort_keys=True, separators=(',', ': '))
        h1 = json.loads(d1)
        h2 = json.loads(d2)
        self.assertEquals(h1, h)
        self.assertEquals(h2, h)
        self.assertEquals(d2, expect)
