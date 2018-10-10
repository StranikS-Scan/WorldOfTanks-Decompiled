# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Explorer/Microsoft_Internet_Explorer.py
import aetools
import MacOS
_code = 'MSIE'

class Microsoft_Internet_Explorer_Events:

    def GetSource(self, _object=None, _attributes={}, **_arguments):
        _code = 'MSIE'
        _subcode = 'SORC'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def PrintBrowserWindow(self, _object=None, _attributes={}, **_arguments):
        _code = 'misc'
        _subcode = 'pWND'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_do_script = {'window': 'WIND'}

    def do_script(self, _object, _attributes={}, **_arguments):
        _code = 'misc'
        _subcode = 'dosc'
        aetools.keysubst(_arguments, self._argmap_do_script)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {}
