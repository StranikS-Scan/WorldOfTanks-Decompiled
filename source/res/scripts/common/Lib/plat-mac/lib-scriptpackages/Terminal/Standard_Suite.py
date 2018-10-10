# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Terminal/Standard_Suite.py
import aetools
import MacOS
_code = '????'

class Standard_Suite_Events():
    _argmap_close = {'saving_in': 'kfil',
     'saving': 'savo'}

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
     'with_properties': 'prdt'}

    def duplicate(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'clon'
        aetools.keysubst(_arguments, self._argmap_duplicate)
        _arguments['----'] = _object
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

    def get(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'getd'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_make = {'at': 'insh',
     'new': 'kocl',
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

    _argmap_move = {'to': 'insh'}

    def move(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'move'
        aetools.keysubst(_arguments, self._argmap_move)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def open(self, _object=None, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'odoc'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def print_(self, _object=None, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'pdoc'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_quit = {'saving': 'savo'}

    def quit(self, _object, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'quit'
        aetools.keysubst(_arguments, self._argmap_quit)
        _arguments['----'] = _object
        aetools.enumsubst(_arguments, 'savo', _Enum_savo)
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_save = {'in_': 'kfil',
     'as': 'fltp'}

    def save(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'save'
        aetools.keysubst(_arguments, self._argmap_save)
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


class _Prop__3c_Inheritance_3e_(aetools.NProperty):
    which = 'c@#^'
    want = 'cobj'


_3c_Inheritance_3e_ = _Prop__3c_Inheritance_3e_()

class _Prop_frontmost(aetools.NProperty):
    which = 'pisf'
    want = 'bool'


frontmost = _Prop_frontmost()

class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'utxt'


name = _Prop_name()

class _Prop_version(aetools.NProperty):
    which = 'vers'
    want = 'utxt'


version = _Prop_version()
applications = application

class item(aetools.ComponentItem):
    want = 'cobj'


class _Prop_class_(aetools.NProperty):
    which = 'pcls'
    want = 'type'


class _Prop_properties(aetools.NProperty):
    which = 'pALL'
    want = 'reco'


items = item

class color(aetools.ComponentItem):
    want = 'colr'


colors = color

class window(aetools.ComponentItem):
    want = 'cwin'


class _Prop_bounds(aetools.NProperty):
    which = 'pbnd'
    want = 'qdrt'


class _Prop_closeable(aetools.NProperty):
    which = 'hclb'
    want = 'bool'


class _Prop_document(aetools.NProperty):
    which = 'docu'
    want = 'docu'


class _Prop_floating(aetools.NProperty):
    which = 'isfl'
    want = 'bool'


class _Prop_id(aetools.NProperty):
    which = 'ID  '
    want = 'long'


class _Prop_index(aetools.NProperty):
    which = 'pidx'
    want = 'long'


class _Prop_miniaturizable(aetools.NProperty):
    which = 'ismn'
    want = 'bool'


class _Prop_miniaturized(aetools.NProperty):
    which = 'pmnd'
    want = 'bool'


class _Prop_modal(aetools.NProperty):
    which = 'pmod'
    want = 'bool'


class _Prop_resizable(aetools.NProperty):
    which = 'prsz'
    want = 'bool'


class _Prop_titled(aetools.NProperty):
    which = 'ptit'
    want = 'bool'


class _Prop_visible(aetools.NProperty):
    which = 'pvis'
    want = 'bool'


class _Prop_zoomable(aetools.NProperty):
    which = 'iszm'
    want = 'bool'


class _Prop_zoomed(aetools.NProperty):
    which = 'pzum'
    want = 'bool'


windows = window

class document(aetools.ComponentItem):
    want = 'docu'


class _Prop_modified(aetools.NProperty):
    which = 'imod'
    want = 'bool'


class _Prop_path(aetools.NProperty):
    which = 'ppth'
    want = 'utxt'


documents = document
application._superclassnames = ['item']
application._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'frontmost': _Prop_frontmost,
 'name': _Prop_name,
 'version': _Prop_version}
application._privelemdict = {'document': document,
 'window': window}
item._superclassnames = []
item._privpropdict = {'class_': _Prop_class_,
 'properties': _Prop_properties}
item._privelemdict = {}
color._superclassnames = ['item']
color._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_}
color._privelemdict = {}
window._superclassnames = ['item']
window._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'bounds': _Prop_bounds,
 'closeable': _Prop_closeable,
 'document': _Prop_document,
 'floating': _Prop_floating,
 'id': _Prop_id,
 'index': _Prop_index,
 'miniaturizable': _Prop_miniaturizable,
 'miniaturized': _Prop_miniaturized,
 'modal': _Prop_modal,
 'name': _Prop_name,
 'resizable': _Prop_resizable,
 'titled': _Prop_titled,
 'visible': _Prop_visible,
 'zoomable': _Prop_zoomable,
 'zoomed': _Prop_zoomed}
window._privelemdict = {}
document._superclassnames = ['item']
document._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'modified': _Prop_modified,
 'name': _Prop_name,
 'path': _Prop_path}
document._privelemdict = {}

class _3c_(aetools.NComparison):
    pass


class _3d_(aetools.NComparison):
    pass


class _3e_(aetools.NComparison):
    pass


class contains(aetools.NComparison):
    pass


class ends_with(aetools.NComparison):
    pass


class starts_with(aetools.NComparison):
    pass


class _b2_(aetools.NComparison):
    pass


class _b3_(aetools.NComparison):
    pass


_Enum_savo = {'ask': 'ask ',
 'yes': 'yes ',
 'no': 'no  '}
_classdeclarations = {'capp': application,
 'cobj': item,
 'colr': color,
 'cwin': window,
 'docu': document}
_propdeclarations = {'ID  ': _Prop_id,
 'c@#^': _Prop__3c_Inheritance_3e_,
 'docu': _Prop_document,
 'hclb': _Prop_closeable,
 'imod': _Prop_modified,
 'isfl': _Prop_floating,
 'ismn': _Prop_miniaturizable,
 'iszm': _Prop_zoomable,
 'pALL': _Prop_properties,
 'pbnd': _Prop_bounds,
 'pcls': _Prop_class_,
 'pidx': _Prop_index,
 'pisf': _Prop_frontmost,
 'pmnd': _Prop_miniaturized,
 'pmod': _Prop_modal,
 'pnam': _Prop_name,
 'ppth': _Prop_path,
 'prsz': _Prop_resizable,
 'ptit': _Prop_titled,
 'pvis': _Prop_visible,
 'pzum': _Prop_zoomed,
 'vers': _Prop_version}
_compdeclarations = {'<   ': _3c_,
 '<=  ': _b2_,
 '=   ': _3d_,
 '>   ': _3e_,
 '>=  ': _b3_,
 'bgwt': starts_with,
 'cont': contains,
 'ends': ends_with}
_enumdeclarations = {'savo': _Enum_savo}
