# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/StdSuites/Standard_Suite.py
import aetools
import MacOS
_code = 'core'
from _builtinSuites.builtin_Suite import *

class Standard_Suite_Events(builtin_Suite_Events):
    _argmap_class_info = {'in_': 'wrcd'}

    def class_info(self, _object=None, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'qobj'
        aetools.keysubst(_arguments, self._argmap_class_info)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

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

    _argmap_event_info = {'in_': 'wrcd'}

    def event_info(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'gtei'
        aetools.keysubst(_arguments, self._argmap_event_info)
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

    def handleBreakpoint(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'brak'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_make = {'new': 'kocl',
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

    _argmap_quit = {'saving': 'savo'}

    def quit(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'quit'
        aetools.keysubst(_arguments, self._argmap_quit)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        aetools.enumsubst(_arguments, 'savo', _Enum_savo)
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def reopen(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'aevt'
        _subcode = 'rapp'
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

    _argmap_suite_info = {'in_': 'wrcd'}

    def suite_info(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'gtsi'
        aetools.keysubst(_arguments, self._argmap_suite_info)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


class alias(aetools.ComponentItem):
    want = 'alis'


class _Prop_POSIX_path(aetools.NProperty):
    which = 'psxp'
    want = 'TEXT'


aliases = alias

class application(aetools.ComponentItem):
    want = 'capp'


class _Prop_clipboard(aetools.NProperty):
    which = 'pcli'
    want = '****'


clipboard = _Prop_clipboard()

class _Prop_frontmost(aetools.NProperty):
    which = 'pisf'
    want = 'bool'


frontmost = _Prop_frontmost()

class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'itxt'


name = _Prop_name()

class _Prop_selection(aetools.NProperty):
    which = 'sele'
    want = 'csel'


selection = _Prop_selection()

class _Prop_version(aetools.NProperty):
    which = 'vers'
    want = 'vers'


version = _Prop_version()
applications = application

class insertion_points(aetools.ComponentItem):
    want = 'cins'


insertion_point = insertion_points

class selection_2d_object(aetools.ComponentItem):
    want = 'csel'


class _Prop_contents(aetools.NProperty):
    which = 'pcnt'
    want = '****'


class window(aetools.ComponentItem):
    want = 'cwin'


class _Prop_bounds(aetools.NProperty):
    which = 'pbnd'
    want = 'qdrt'


class _Prop_closeable(aetools.NProperty):
    which = 'hclb'
    want = 'bool'


class _Prop_floating(aetools.NProperty):
    which = 'isfl'
    want = 'bool'


class _Prop_index(aetools.NProperty):
    which = 'pidx'
    want = 'long'


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


documents = document

class file(aetools.ComponentItem):
    want = 'file'


files = file
alias._superclassnames = []
alias._privpropdict = {'POSIX_path': _Prop_POSIX_path}
alias._privelemdict = {}
application._superclassnames = []
application._privpropdict = {'clipboard': _Prop_clipboard,
 'frontmost': _Prop_frontmost,
 'name': _Prop_name,
 'selection': _Prop_selection,
 'version': _Prop_version}
application._privelemdict = {}
insertion_points._superclassnames = []
insertion_points._privpropdict = {}
insertion_points._privelemdict = {}
selection_2d_object._superclassnames = []
selection_2d_object._privpropdict = {'contents': _Prop_contents}
selection_2d_object._privelemdict = {}
window._superclassnames = []
window._privpropdict = {'bounds': _Prop_bounds,
 'closeable': _Prop_closeable,
 'floating': _Prop_floating,
 'index': _Prop_index,
 'modal': _Prop_modal,
 'resizable': _Prop_resizable,
 'titled': _Prop_titled,
 'visible': _Prop_visible,
 'zoomable': _Prop_zoomable,
 'zoomed': _Prop_zoomed}
window._privelemdict = {}
document._superclassnames = []
document._privpropdict = {'modified': _Prop_modified}
document._privelemdict = {}
file._superclassnames = []
file._privpropdict = {'POSIX_path': _Prop_POSIX_path}
file._privelemdict = {}

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


_Enum_kfrm = {'index': 'indx',
 'named': 'name',
 'id': 'ID  '}
_Enum_savo = {'yes': 'yes ',
 'no': 'no  ',
 'ask': 'ask '}
_Enum_styl = {'plain': 'plan',
 'bold': 'bold',
 'italic': 'ital',
 'outline': 'outl',
 'shadow': 'shad',
 'underline': 'undl',
 'superscript': 'spsc',
 'subscript': 'sbsc',
 'strikethrough': 'strk',
 'small_caps': 'smcp',
 'all_caps': 'alcp',
 'all_lowercase': 'lowc',
 'condensed': 'cond',
 'expanded': 'pexp',
 'hidden': 'hidn'}
_classdeclarations = {'alis': alias,
 'capp': application,
 'cins': insertion_points,
 'csel': selection_2d_object,
 'cwin': window,
 'docu': document,
 'file': file}
_propdeclarations = {'hclb': _Prop_closeable,
 'imod': _Prop_modified,
 'isfl': _Prop_floating,
 'iszm': _Prop_zoomable,
 'pbnd': _Prop_bounds,
 'pcli': _Prop_clipboard,
 'pcnt': _Prop_contents,
 'pidx': _Prop_index,
 'pisf': _Prop_frontmost,
 'pmod': _Prop_modal,
 'pnam': _Prop_name,
 'prsz': _Prop_resizable,
 'psxp': _Prop_POSIX_path,
 'ptit': _Prop_titled,
 'pvis': _Prop_visible,
 'pzum': _Prop_zoomed,
 'sele': _Prop_selection,
 'vers': _Prop_version}
_compdeclarations = {'<   ': _3c_,
 '<=  ': _b2_,
 '=   ': _3d_,
 '>   ': _3e_,
 '>=  ': _b3_,
 'bgwt': starts_with,
 'cont': contains,
 'ends': ends_with}
_enumdeclarations = {'kfrm': _Enum_kfrm,
 'savo': _Enum_savo,
 'styl': _Enum_styl}
