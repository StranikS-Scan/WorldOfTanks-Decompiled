# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Netscape/Standard_URL_suite.py
import aetools
import MacOS
_code = 'GURL'

class Standard_URL_suite_Events:
    _argmap_GetURL = {'to': 'dest',
     'inside': 'HWIN',
     'from_': 'refe'}

    def GetURL(self, _object, _attributes={}, **_arguments):
        _code = 'GURL'
        _subcode = 'GURL'
        aetools.keysubst(_arguments, self._argmap_GetURL)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {}
