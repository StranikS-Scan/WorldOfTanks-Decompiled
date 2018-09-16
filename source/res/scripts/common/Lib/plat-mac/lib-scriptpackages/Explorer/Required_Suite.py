# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Explorer/Required_Suite.py
import aetools
import MacOS
_code = 'reqd'
from StdSuites.Required_Suite import *

class Required_Suite_Events(Required_Suite_Events):

    def open(self, _object, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'odoc'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def print_(self, _object, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'pdoc'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def quit(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'quit'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def run(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'oapp'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {}
