# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/StdSuites/QuickDraw_Graphics_Suppleme.py
import aetools
import MacOS
_code = 'qdsp'

class QuickDraw_Graphics_Suppleme_Events:
    pass


class drawing_area(aetools.ComponentItem):
    want = 'cdrw'


class _Prop_rotation(aetools.NProperty):
    which = 'prot'
    want = 'trot'


class _Prop_scale(aetools.NProperty):
    which = 'pscl'
    want = 'fixd'


class _Prop_translation(aetools.NProperty):
    which = 'ptrs'
    want = 'QDpt'


drawing_areas = drawing_area

class graphic_groups(aetools.ComponentItem):
    want = 'cpic'


graphic_group = graphic_groups
drawing_area._superclassnames = []
drawing_area._privpropdict = {'rotation': _Prop_rotation,
 'scale': _Prop_scale,
 'translation': _Prop_translation}
drawing_area._privelemdict = {}
graphic_groups._superclassnames = []
graphic_groups._privpropdict = {}
graphic_groups._privelemdict = {}
_classdeclarations = {'cdrw': drawing_area,
 'cpic': graphic_groups}
_propdeclarations = {'prot': _Prop_rotation,
 'pscl': _Prop_scale,
 'ptrs': _Prop_translation}
_compdeclarations = {}
_enumdeclarations = {}
