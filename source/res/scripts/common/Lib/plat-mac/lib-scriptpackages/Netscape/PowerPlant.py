# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Netscape/PowerPlant.py
import aetools
import MacOS
_code = 'ppnt'

class PowerPlant_Events:
    _argmap_SwitchTellTarget = {'to': 'data'}

    def SwitchTellTarget(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'ppnt'
        _subcode = 'sttg'
        aetools.keysubst(_arguments, self._argmap_SwitchTellTarget)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_select = {'data': 'data'}

    def select(self, _object, _attributes={}, **_arguments):
        _code = 'misc'
        _subcode = 'slct'
        aetools.keysubst(_arguments, self._argmap_select)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


_Enum_dbac = {'DoNothing': '\x00\x00\x00\x00',
 'PostAlert': '\x00\x00\x00\x01',
 'LowLevelDebugger': '\x00\x00\x00\x02',
 'SourceDebugger': '\x00\x00\x00\x03'}
_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {'dbac': _Enum_dbac}
