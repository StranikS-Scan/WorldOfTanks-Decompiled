# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/json/tests/test_dump.py
# Compiled at: 2010-08-25 17:58:21
from unittest import TestCase
from cStringIO import StringIO
import json

class TestDump(TestCase):

    def test_dump(self):
        sio = StringIO()
        json.dump({}, sio)
        self.assertEquals(sio.getvalue(), '{}')

    def test_dumps(self):
        self.assertEquals(json.dumps({}), '{}')
