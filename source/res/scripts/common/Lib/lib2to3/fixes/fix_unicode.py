# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_unicode.py
from ..pgen2 import token
from .. import fixer_base
_mapping = {u'unichr': u'chr',
 u'unicode': u'str'}

class FixUnicode(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "STRING | 'unicode' | 'unichr'"

    def start_tree(self, tree, filename):
        super(FixUnicode, self).start_tree(tree, filename)
        self.unicode_literals = 'unicode_literals' in tree.future_features

    def transform(self, node, results):
        if node.type == token.NAME:
            new = node.clone()
            new.value = _mapping[node.value]
            return new
        if node.type == token.STRING:
            val = node.value
            if not self.unicode_literals and val[0] in u'\'"' and u'\\' in val:
                val = u'\\\\'.join([ v.replace(u'\\u', u'\\\\u').replace(u'\\U', u'\\\\U') for v in val.split(u'\\\\') ])
            if val[0] in u'uU':
                val = val[1:]
            if val == node.value:
                return node
            new = node.clone()
            new.value = val
            return new
