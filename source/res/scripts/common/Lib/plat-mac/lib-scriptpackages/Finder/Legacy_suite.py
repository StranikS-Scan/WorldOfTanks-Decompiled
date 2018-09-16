# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Finder/Legacy_suite.py
import aetools
import MacOS
_code = 'fleg'

class Legacy_suite_Events:

    def restart(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'rest'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def shut_down(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'shut'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def sleep(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'fndr'
        _subcode = 'slep'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


class application(aetools.ComponentItem):
    want = 'capp'


class _Prop_desktop_picture(aetools.NProperty):
    which = 'dpic'
    want = 'file'


desktop_picture = _Prop_desktop_picture()

class application_process(aetools.ComponentItem):
    want = 'pcap'


class _Prop__3c_Inheritance_3e_(aetools.NProperty):
    which = 'c@#^'
    want = 'prcs'


class _Prop_application_file(aetools.NProperty):
    which = 'appf'
    want = 'appf'


application_processes = application_process

class desk_accessory_process(aetools.ComponentItem):
    want = 'pcda'


class _Prop_desk_accessory_file(aetools.NProperty):
    which = 'dafi'
    want = 'obj '


desk_accessory_processes = desk_accessory_process

class process(aetools.ComponentItem):
    want = 'prcs'


class _Prop_accepts_high_level_events(aetools.NProperty):
    which = 'isab'
    want = 'bool'


class _Prop_accepts_remote_events(aetools.NProperty):
    which = 'revt'
    want = 'bool'


class _Prop_creator_type(aetools.NProperty):
    which = 'fcrt'
    want = 'type'


class _Prop_file(aetools.NProperty):
    which = 'file'
    want = 'obj '


class _Prop_file_type(aetools.NProperty):
    which = 'asty'
    want = 'type'


class _Prop_frontmost(aetools.NProperty):
    which = 'pisf'
    want = 'bool'


class _Prop_has_scripting_terminology(aetools.NProperty):
    which = 'hscr'
    want = 'bool'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'itxt'


class _Prop_partition_space_used(aetools.NProperty):
    which = 'pusd'
    want = 'long'


class _Prop_total_partition_size(aetools.NProperty):
    which = 'appt'
    want = 'long'


class _Prop_visible(aetools.NProperty):
    which = 'pvis'
    want = 'bool'


processes = process
application._superclassnames = []
application._privpropdict = {'desktop_picture': _Prop_desktop_picture}
application._privelemdict = {}
application_process._superclassnames = ['process']
application_process._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'application_file': _Prop_application_file}
application_process._privelemdict = {}
desk_accessory_process._superclassnames = ['process']
desk_accessory_process._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'desk_accessory_file': _Prop_desk_accessory_file}
desk_accessory_process._privelemdict = {}
process._superclassnames = []
process._privpropdict = {'accepts_high_level_events': _Prop_accepts_high_level_events,
 'accepts_remote_events': _Prop_accepts_remote_events,
 'creator_type': _Prop_creator_type,
 'file': _Prop_file,
 'file_type': _Prop_file_type,
 'frontmost': _Prop_frontmost,
 'has_scripting_terminology': _Prop_has_scripting_terminology,
 'name': _Prop_name,
 'partition_space_used': _Prop_partition_space_used,
 'total_partition_size': _Prop_total_partition_size,
 'visible': _Prop_visible}
process._privelemdict = {}
_classdeclarations = {'capp': application,
 'pcap': application_process,
 'pcda': desk_accessory_process,
 'prcs': process}
_propdeclarations = {'appf': _Prop_application_file,
 'appt': _Prop_total_partition_size,
 'asty': _Prop_file_type,
 'c@#^': _Prop__3c_Inheritance_3e_,
 'dafi': _Prop_desk_accessory_file,
 'dpic': _Prop_desktop_picture,
 'fcrt': _Prop_creator_type,
 'file': _Prop_file,
 'hscr': _Prop_has_scripting_terminology,
 'isab': _Prop_accepts_high_level_events,
 'pisf': _Prop_frontmost,
 'pnam': _Prop_name,
 'pusd': _Prop_partition_space_used,
 'pvis': _Prop_visible,
 'revt': _Prop_accepts_remote_events}
_compdeclarations = {}
_enumdeclarations = {}
