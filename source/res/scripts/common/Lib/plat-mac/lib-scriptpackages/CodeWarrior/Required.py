# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/CodeWarrior/Required.py
import aetools
import MacOS
_code = 'reqd'
from StdSuites.Required_Suite import *

class Required_Events(Required_Suite_Events):
    _argmap_open = {'converting': 'Conv'}

    def open(self, _object, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'odoc'
        aetools.keysubst(_arguments, self._argmap_open)
        _arguments['----'] = _object
        aetools.enumsubst(_arguments, 'Conv', _Enum_Conv)
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


_Enum_Conv = {'yes': 'yes ',
 'no': 'no  '}
_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {'Conv': _Enum_Conv}
