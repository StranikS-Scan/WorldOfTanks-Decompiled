# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Finder/Standard_Suite.py
import aetools
import MacOS
_code = 'CoRe'
from StdSuites.Standard_Suite import *

class Standard_Suite_Events(Standard_Suite_Events):

    def close(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'clos'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_count = {'each': 'kocl'}

    def count(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'cnte'
        aetools.keysubst(_arguments, self._argmap_count)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_data_size = {'as': 'rtyp'}

    def data_size(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'dsiz'
        aetools.keysubst(_arguments, self._argmap_data_size)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def delete(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'delo'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_duplicate = {'to': 'insh',
     'replacing': 'alrp',
     'routing_suppressed': 'rout'}

    def duplicate(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'clon'
        aetools.keysubst(_arguments, self._argmap_duplicate)
        _arguments['----'] = _object
        aetools.enumsubst(_arguments, 'alrp', _Enum_bool)
        aetools.enumsubst(_arguments, 'rout', _Enum_bool)
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def exists(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'doex'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_make = {'new': 'kocl',
     'at': 'insh',
     'to': 'to  ',
     'with_properties': 'prdt'}

    def make(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'crel'
        aetools.keysubst(_arguments, self._argmap_make)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_move = {'to': 'insh',
     'replacing': 'alrp',
     'positioned_at': 'mvpl',
     'routing_suppressed': 'rout'}

    def move(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'move'
        aetools.keysubst(_arguments, self._argmap_move)
        _arguments['----'] = _object
        aetools.enumsubst(_arguments, 'alrp', _Enum_bool)
        aetools.enumsubst(_arguments, 'mvpl', _Enum_list)
        aetools.enumsubst(_arguments, 'rout', _Enum_bool)
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_open = {'using': 'usin',
     'with_properties': 'prdt'}

    def open(self, _object, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'odoc'
        aetools.keysubst(_arguments, self._argmap_open)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_print_ = {'with_properties': 'prdt'}

    def print_(self, _object, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'pdoc'
        aetools.keysubst(_arguments, self._argmap_print_)
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

    def select(self, _object, _attributes={}, **_arguments):
        _code = 'misc'
        _subcode = 'slct'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


_Enum_list = None
_Enum_bool = None
_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {}
