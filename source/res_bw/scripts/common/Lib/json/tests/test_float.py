# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/json/tests/test_float.py
# Compiled at: 2010-08-25 17:58:21
import math
from unittest import TestCase
import json

class TestFloat(TestCase):

    def test_floats(self):
        for num in [1617161771.765,
         math.pi,
         math.pi ** 100,
         math.pi ** (-100)]:
            self.assertEquals(float(json.dumps(num)), num)
