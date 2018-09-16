# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Finder/Finder_items.py
import aetools
import MacOS
_code = 'fndr'

class Finder_items_Events:

    def add_to_favorites(self, _object, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'ffav'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_clean_up = {'by': 'by  '}

    def clean_up(self, _object, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'fclu'
        aetools.keysubst(_arguments, self._argmap_clean_up)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def eject(self, _object=None, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'ejct'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def empty(self, _object=None, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'empt'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def erase(self, _object, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'fera'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def reveal(self, _object, _attributes={}, **_arguments):
        _code = 'misc'
        _subcode = 'mvis'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_update = {'necessity': 'nec?',
     'registering_applications': 'reg?'}

    def update(self, _object, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'fupd'
        aetools.keysubst(_arguments, self._argmap_update)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


class item(aetools.ComponentItem):
    want = 'cobj'


class _Prop_bounds(aetools.NProperty):
    which = 'pbnd'
    want = 'qdrt'


class _Prop_comment(aetools.NProperty):
    which = 'comt'
    want = 'utxt'


class _Prop_container(aetools.NProperty):
    which = 'ctnr'
    want = 'obj '


class _Prop_creation_date(aetools.NProperty):
    which = 'ascd'
    want = 'ldt '


class _Prop_description(aetools.NProperty):
    which = 'dscr'
    want = 'utxt'


class _Prop_disk(aetools.NProperty):
    which = 'cdis'
    want = 'obj '


class _Prop_displayed_name(aetools.NProperty):
    which = 'dnam'
    want = 'utxt'


class _Prop_everyones_privileges(aetools.NProperty):
    which = 'gstp'
    want = 'priv'


class _Prop_extension_hidden(aetools.NProperty):
    which = 'hidx'
    want = 'bool'


class _Prop_group(aetools.NProperty):
    which = 'sgrp'
    want = 'utxt'


class _Prop_group_privileges(aetools.NProperty):
    which = 'gppr'
    want = 'priv'


class _Prop_icon(aetools.NProperty):
    which = 'iimg'
    want = 'ifam'


class _Prop_index(aetools.NProperty):
    which = 'pidx'
    want = 'long'


class _Prop_information_window(aetools.NProperty):
    which = 'iwnd'
    want = 'obj '


class _Prop_kind(aetools.NProperty):
    which = 'kind'
    want = 'utxt'


class _Prop_label_index(aetools.NProperty):
    which = 'labi'
    want = 'long'


class _Prop_locked(aetools.NProperty):
    which = 'aslk'
    want = 'bool'


class _Prop_modification_date(aetools.NProperty):
    which = 'asmo'
    want = 'ldt '


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'utxt'


class _Prop_name_extension(aetools.NProperty):
    which = 'nmxt'
    want = 'utxt'


class _Prop_owner(aetools.NProperty):
    which = 'sown'
    want = 'utxt'


class _Prop_owner_privileges(aetools.NProperty):
    which = 'ownr'
    want = 'priv'


class _Prop_physical_size(aetools.NProperty):
    which = 'phys'
    want = 'comp'


class _Prop_position(aetools.NProperty):
    which = 'posn'
    want = 'QDpt'


class _Prop_properties(aetools.NProperty):
    which = 'pALL'
    want = 'reco'


class _Prop_size(aetools.NProperty):
    which = 'ptsz'
    want = 'comp'


class _Prop_url(aetools.NProperty):
    which = 'pURL'
    want = 'utxt'


items = item
item._superclassnames = []
item._privpropdict = {'bounds': _Prop_bounds,
 'comment': _Prop_comment,
 'container': _Prop_container,
 'creation_date': _Prop_creation_date,
 'description': _Prop_description,
 'disk': _Prop_disk,
 'displayed_name': _Prop_displayed_name,
 'everyones_privileges': _Prop_everyones_privileges,
 'extension_hidden': _Prop_extension_hidden,
 'group': _Prop_group,
 'group_privileges': _Prop_group_privileges,
 'icon': _Prop_icon,
 'index': _Prop_index,
 'information_window': _Prop_information_window,
 'kind': _Prop_kind,
 'label_index': _Prop_label_index,
 'locked': _Prop_locked,
 'modification_date': _Prop_modification_date,
 'name': _Prop_name,
 'name_extension': _Prop_name_extension,
 'owner': _Prop_owner,
 'owner_privileges': _Prop_owner_privileges,
 'physical_size': _Prop_physical_size,
 'position': _Prop_position,
 'properties': _Prop_properties,
 'size': _Prop_size,
 'url': _Prop_url}
item._privelemdict = {}
_classdeclarations = {'cobj': item}
_propdeclarations = {'ascd': _Prop_creation_date,
 'aslk': _Prop_locked,
 'asmo': _Prop_modification_date,
 'cdis': _Prop_disk,
 'comt': _Prop_comment,
 'ctnr': _Prop_container,
 'dnam': _Prop_displayed_name,
 'dscr': _Prop_description,
 'gppr': _Prop_group_privileges,
 'gstp': _Prop_everyones_privileges,
 'hidx': _Prop_extension_hidden,
 'iimg': _Prop_icon,
 'iwnd': _Prop_information_window,
 'kind': _Prop_kind,
 'labi': _Prop_label_index,
 'nmxt': _Prop_name_extension,
 'ownr': _Prop_owner_privileges,
 'pALL': _Prop_properties,
 'pURL': _Prop_url,
 'pbnd': _Prop_bounds,
 'phys': _Prop_physical_size,
 'pidx': _Prop_index,
 'pnam': _Prop_name,
 'posn': _Prop_position,
 'ptsz': _Prop_size,
 'sgrp': _Prop_group,
 'sown': _Prop_owner}
_compdeclarations = {}
_enumdeclarations = {}
