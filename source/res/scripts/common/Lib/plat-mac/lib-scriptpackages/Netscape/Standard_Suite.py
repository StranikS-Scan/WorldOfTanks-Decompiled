# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Netscape/Standard_Suite.py
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

    def data_size(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'dsiz'
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


class _Prop_alert_application(aetools.NProperty):
    which = 'ALAP'
    want = 'type'


alert_application = _Prop_alert_application()

class _Prop_kiosk_mode(aetools.NProperty):
    which = 'KOSK'
    want = 'long'


kiosk_mode = _Prop_kiosk_mode()

class window(aetools.ComponentItem):
    want = 'cwin'


class _Prop_URL(aetools.NProperty):
    which = 'curl'
    want = 'TEXT'


class _Prop_bounds(aetools.NProperty):
    which = 'pbnd'
    want = 'qdrt'


class _Prop_busy(aetools.NProperty):
    which = 'busy'
    want = 'long'


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


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'itxt'


class _Prop_position(aetools.NProperty):
    which = 'ppos'
    want = 'QDpt'


class _Prop_resizable(aetools.NProperty):
    which = 'prsz'
    want = 'bool'


class _Prop_titled(aetools.NProperty):
    which = 'ptit'
    want = 'bool'


class _Prop_unique_ID(aetools.NProperty):
    which = 'wiid'
    want = 'long'


class _Prop_visible(aetools.NProperty):
    which = 'pvis'
    want = 'bool'


class _Prop_zoomable(aetools.NProperty):
    which = 'iszm'
    want = 'bool'


class _Prop_zoomed(aetools.NProperty):
    which = 'pzum'
    want = 'bool'


application._superclassnames = []
application._privpropdict = {'alert_application': _Prop_alert_application,
 'kiosk_mode': _Prop_kiosk_mode}
application._privelemdict = {'window': window}
window._superclassnames = []
window._privpropdict = {'URL': _Prop_URL,
 'bounds': _Prop_bounds,
 'busy': _Prop_busy,
 'closeable': _Prop_closeable,
 'floating': _Prop_floating,
 'index': _Prop_index,
 'modal': _Prop_modal,
 'name': _Prop_name,
 'position': _Prop_position,
 'resizable': _Prop_resizable,
 'titled': _Prop_titled,
 'unique_ID': _Prop_unique_ID,
 'visible': _Prop_visible,
 'zoomable': _Prop_zoomable,
 'zoomed': _Prop_zoomed}
window._privelemdict = {}
_classdeclarations = {'capp': application,
 'cwin': window}
_propdeclarations = {'ALAP': _Prop_alert_application,
 'KOSK': _Prop_kiosk_mode,
 'busy': _Prop_busy,
 'curl': _Prop_URL,
 'hclb': _Prop_closeable,
 'isfl': _Prop_floating,
 'iszm': _Prop_zoomable,
 'pbnd': _Prop_bounds,
 'pidx': _Prop_index,
 'pmod': _Prop_modal,
 'pnam': _Prop_name,
 'ppos': _Prop_position,
 'prsz': _Prop_resizable,
 'ptit': _Prop_titled,
 'pvis': _Prop_visible,
 'pzum': _Prop_zoomed,
 'wiid': _Prop_unique_ID}
_compdeclarations = {}
_enumdeclarations = {}
