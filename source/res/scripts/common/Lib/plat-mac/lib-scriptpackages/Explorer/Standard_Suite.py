# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Explorer/Standard_Suite.py
import aetools
import MacOS
_code = '****'

class Standard_Suite_Events:
    _argmap_get = {'as': 'rtyp'}

    def get(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'getd'
        aetools.keysubst(_arguments, self._argmap_get)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


class application(aetools.ComponentItem):
    want = 'capp'


class _Prop_selected_text(aetools.NProperty):
    which = 'stxt'
    want = 'TEXT'


selected_text = _Prop_selected_text()
application._superclassnames = []
application._privpropdict = {'selected_text': _Prop_selected_text}
application._privelemdict = {}
_classdeclarations = {'capp': application}
_propdeclarations = {'stxt': _Prop_selected_text}
_compdeclarations = {}
_enumdeclarations = {}
