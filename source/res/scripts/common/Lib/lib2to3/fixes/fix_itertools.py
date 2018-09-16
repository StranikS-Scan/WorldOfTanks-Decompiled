# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_itertools.py
from .. import fixer_base
from ..fixer_util import Name

class FixItertools(fixer_base.BaseFix):
    BM_compatible = True
    it_funcs = "('imap'|'ifilter'|'izip'|'izip_longest'|'ifilterfalse')"
    PATTERN = "\n              power< it='itertools'\n                  trailer<\n                     dot='.' func=%(it_funcs)s > trailer< '(' [any] ')' > >\n              |\n              power< func=%(it_funcs)s trailer< '(' [any] ')' > >\n              " % locals()
    run_order = 6

    def transform(self, node, results):
        prefix = None
        func = results['func'][0]
        if 'it' in results and func.value not in (u'ifilterfalse', u'izip_longest'):
            dot, it = results['dot'], results['it']
            prefix = it.prefix
            it.remove()
            dot.remove()
            func.parent.replace(func)
        prefix = prefix or func.prefix
        func.replace(Name(func.value[1:], prefix=prefix))
        return
