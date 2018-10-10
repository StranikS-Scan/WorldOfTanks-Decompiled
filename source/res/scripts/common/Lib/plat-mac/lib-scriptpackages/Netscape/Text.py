# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Netscape/Text.py
import aetools
import MacOS
_code = 'TEXT'
from StdSuites.Text_Suite import *

class Text_Events(Text_Suite_Events):
    pass


class text(aetools.ComponentItem):
    want = 'ctxt'


class _Prop_beginning(aetools.NProperty):
    which = 'bgng'
    want = 'obj '


class _Prop_end(aetools.NProperty):
    which = 'end '
    want = 'obj '


class _Prop_infront(aetools.NProperty):
    which = 'pBef'
    want = 'obj '


class _Prop_justbehind(aetools.NProperty):
    which = 'pAft'
    want = 'obj '


class _Prop_updateLevel(aetools.NProperty):
    which = 'pUpL'
    want = 'long'


class styleset(aetools.ComponentItem):
    want = 'stys'


class _Prop_color(aetools.NProperty):
    which = 'colr'
    want = 'RGB '


class _Prop_font(aetools.NProperty):
    which = 'font'
    want = 'TEXT'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'TEXT'


class _Prop_size(aetools.NProperty):
    which = 'ptsz'
    want = 'long'


class _Prop_style(aetools.NProperty):
    which = 'txst'
    want = 'tsty'


class _Prop_writing_code(aetools.NProperty):
    which = 'psct'
    want = 'tsty'


stylesets = styleset
text._superclassnames = []
text._privpropdict = {'beginning': _Prop_beginning,
 'end': _Prop_end,
 'infront': _Prop_infront,
 'justbehind': _Prop_justbehind,
 'updateLevel': _Prop_updateLevel}
text._privelemdict = {'styleset': styleset}
styleset._superclassnames = []
styleset._privpropdict = {'color': _Prop_color,
 'font': _Prop_font,
 'name': _Prop_name,
 'size': _Prop_size,
 'style': _Prop_style,
 'writing_code': _Prop_writing_code}
styleset._privelemdict = {}
_classdeclarations = {'ctxt': text,
 'stys': styleset}
_propdeclarations = {'bgng': _Prop_beginning,
 'colr': _Prop_color,
 'end ': _Prop_end,
 'font': _Prop_font,
 'pAft': _Prop_justbehind,
 'pBef': _Prop_infront,
 'pUpL': _Prop_updateLevel,
 'pnam': _Prop_name,
 'psct': _Prop_writing_code,
 'ptsz': _Prop_size,
 'txst': _Prop_style}
_compdeclarations = {}
_enumdeclarations = {}
