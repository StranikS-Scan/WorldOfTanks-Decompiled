# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/CodeWarrior/Standard_Suite.py
import aetools
import MacOS
_code = 'CoRe'
from StdSuites.Standard_Suite import *

class Standard_Suite_Events(Standard_Suite_Events):
    _argmap_close = {'saving': 'savo',
     'saving_in': 'kfil'}

    def close(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'clos'
        aetools.keysubst(_arguments, self._argmap_close)
        _arguments['----'] = _object
        aetools.enumsubst(_arguments, 'savo', _Enum_savo)
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

    _argmap_make = {'new': 'kocl',
     'as': 'rtyp',
     'at': 'insh',
     'with_data': 'data',
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

    def select(self, _object=None, _attributes={}, **_arguments):
        _code = 'misc'
        _subcode = 'slct'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_set = {'to': 'data'}

    def set(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'setd'
        aetools.keysubst(_arguments, self._argmap_set)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


class application(aetools.ComponentItem):
    want = 'capp'


class _Prop_user_interaction(aetools.NProperty):
    which = 'inte'
    want = 'Inte'


user_interaction = _Prop_user_interaction()

class character(aetools.ComponentItem):
    want = 'cha '


class _Prop_length(aetools.NProperty):
    which = 'pLen'
    want = 'long'


class _Prop_offset(aetools.NProperty):
    which = 'pOff'
    want = 'long'


class insertion_point(aetools.ComponentItem):
    want = 'cins'


class line(aetools.ComponentItem):
    want = 'clin'


class _Prop_index(aetools.NProperty):
    which = 'pidx'
    want = 'long'


lines = line

class selection_2d_object(aetools.ComponentItem):
    want = 'csel'


class _Prop_contents(aetools.NProperty):
    which = 'pcnt'
    want = 'type'


class text(aetools.ComponentItem):
    want = 'ctxt'


class window(aetools.ComponentItem):
    want = 'cwin'


class _Prop_bounds(aetools.NProperty):
    which = 'pbnd'
    want = 'qdrt'


class _Prop_document(aetools.NProperty):
    which = 'docu'
    want = 'docu'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'itxt'


class _Prop_position(aetools.NProperty):
    which = 'ppos'
    want = 'QDpt'


class _Prop_visible(aetools.NProperty):
    which = 'pvis'
    want = 'bool'


class _Prop_zoomed(aetools.NProperty):
    which = 'pzum'
    want = 'bool'


windows = window

class document(aetools.ComponentItem):
    want = 'docu'


class _Prop_file_permissions(aetools.NProperty):
    which = 'PERM'
    want = 'PERM'


class _Prop_kind(aetools.NProperty):
    which = 'DKND'
    want = 'DKND'


class _Prop_location(aetools.NProperty):
    which = 'FILE'
    want = 'fss '


class _Prop_window(aetools.NProperty):
    which = 'cwin'
    want = 'cwin'


documents = document

class files(aetools.ComponentItem):
    want = 'file'


file = files
application._superclassnames = []
application._privpropdict = {'user_interaction': _Prop_user_interaction}
application._privelemdict = {'document': document,
 'window': window}
character._superclassnames = []
character._privpropdict = {'length': _Prop_length,
 'offset': _Prop_offset}
character._privelemdict = {}
insertion_point._superclassnames = []
insertion_point._privpropdict = {'length': _Prop_length,
 'offset': _Prop_offset}
insertion_point._privelemdict = {}
line._superclassnames = []
line._privpropdict = {'index': _Prop_index,
 'length': _Prop_length,
 'offset': _Prop_offset}
line._privelemdict = {'character': character}
selection_2d_object._superclassnames = []
selection_2d_object._privpropdict = {'contents': _Prop_contents,
 'length': _Prop_length,
 'offset': _Prop_offset}
selection_2d_object._privelemdict = {'character': character,
 'line': line,
 'text': text}
text._superclassnames = []
text._privpropdict = {'length': _Prop_length,
 'offset': _Prop_offset}
text._privelemdict = {'character': character,
 'insertion_point': insertion_point,
 'line': line,
 'text': text}
window._superclassnames = []
window._privpropdict = {'bounds': _Prop_bounds,
 'document': _Prop_document,
 'index': _Prop_index,
 'name': _Prop_name,
 'position': _Prop_position,
 'visible': _Prop_visible,
 'zoomed': _Prop_zoomed}
window._privelemdict = {}
document._superclassnames = []
document._privpropdict = {'file_permissions': _Prop_file_permissions,
 'index': _Prop_index,
 'kind': _Prop_kind,
 'location': _Prop_location,
 'name': _Prop_name,
 'window': _Prop_window}
document._privelemdict = {}
files._superclassnames = []
files._privpropdict = {}
files._privelemdict = {}
_classdeclarations = {'capp': application,
 'cha ': character,
 'cins': insertion_point,
 'clin': line,
 'csel': selection_2d_object,
 'ctxt': text,
 'cwin': window,
 'docu': document,
 'file': files}
_propdeclarations = {'DKND': _Prop_kind,
 'FILE': _Prop_location,
 'PERM': _Prop_file_permissions,
 'cwin': _Prop_window,
 'docu': _Prop_document,
 'inte': _Prop_user_interaction,
 'pLen': _Prop_length,
 'pOff': _Prop_offset,
 'pbnd': _Prop_bounds,
 'pcnt': _Prop_contents,
 'pidx': _Prop_index,
 'pnam': _Prop_name,
 'ppos': _Prop_position,
 'pvis': _Prop_visible,
 'pzum': _Prop_zoomed}
_compdeclarations = {}
_enumdeclarations = {}
