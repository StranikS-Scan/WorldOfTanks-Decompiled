# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/json/tests/test_default.py
# Compiled at: 2010-08-25 17:58:21
from unittest import TestCase
import json

class TestDefault(TestCase):

    def test_default(self):
        self.assertEquals(json.dumps(type, default=repr), json.dumps(repr(type)))
