# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_asserts.py
from ..fixer_base import BaseFix
from ..fixer_util import Name
NAMES = dict(assert_='assertTrue', assertEquals='assertEqual', assertNotEquals='assertNotEqual', assertAlmostEquals='assertAlmostEqual', assertNotAlmostEquals='assertNotAlmostEqual', assertRegexpMatches='assertRegex', assertRaisesRegexp='assertRaisesRegex', failUnlessEqual='assertEqual', failIfEqual='assertNotEqual', failUnlessAlmostEqual='assertAlmostEqual', failIfAlmostEqual='assertNotAlmostEqual', failUnless='assertTrue', failUnlessRaises='assertRaises', failIf='assertFalse')

class FixAsserts(BaseFix):
    PATTERN = "\n              power< any+ trailer< '.' meth=(%s)> any* >\n              " % '|'.join(map(repr, NAMES))

    def transform(self, node, results):
        name = results['meth'][0]
        name.replace(Name(NAMES[str(name)], prefix=name.prefix))
