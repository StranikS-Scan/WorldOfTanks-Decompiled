# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/SystemEvents/Processes_Suite.py
import aetools
import MacOS
_code = 'prcs'

class Processes_Suite_Events:
    pass


class application(aetools.ComponentItem):
    want = 'capp'


class _Prop__3c_Inheritance_3e_(aetools.NProperty):
    which = 'c@#^'
    want = 'capp'


_3c_Inheritance_3e_ = _Prop__3c_Inheritance_3e_()

class _Prop_folder_actions_enabled(aetools.NProperty):
    which = 'faen'
    want = 'bool'


folder_actions_enabled = _Prop_folder_actions_enabled()

class _Prop_properties(aetools.NProperty):
    which = 'pALL'
    want = '****'


properties = _Prop_properties()
applications = application

class application_process(aetools.ComponentItem):
    want = 'pcap'


class _Prop_application_file(aetools.NProperty):
    which = 'appf'
    want = '****'


application_processes = application_process

class desk_accessory_process(aetools.ComponentItem):
    want = 'pcda'


class _Prop_desk_accessory_file(aetools.NProperty):
    which = 'dafi'
    want = '****'


desk_accessory_processes = desk_accessory_process

class process(aetools.ComponentItem):
    want = 'prcs'


class _Prop_accepts_high_level_events(aetools.NProperty):
    which = 'isab'
    want = 'bool'


class _Prop_accepts_remote_events(aetools.NProperty):
    which = 'revt'
    want = 'bool'


class _Prop_classic(aetools.NProperty):
    which = 'clsc'
    want = 'bool'


class _Prop_creator_type(aetools.NProperty):
    which = 'fcrt'
    want = 'utxt'


class _Prop_file(aetools.NProperty):
    which = 'file'
    want = '****'


class _Prop_file_type(aetools.NProperty):
    which = 'asty'
    want = 'utxt'


class _Prop_frontmost(aetools.NProperty):
    which = 'pisf'
    want = 'bool'


class _Prop_has_scripting_terminology(aetools.NProperty):
    which = 'hscr'
    want = 'bool'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'utxt'


class _Prop_partition_space_used(aetools.NProperty):
    which = 'pusd'
    want = 'magn'


class _Prop_total_partition_size(aetools.NProperty):
    which = 'appt'
    want = 'magn'


class _Prop_visible(aetools.NProperty):
    which = 'pvis'
    want = 'bool'


processes = process
application._superclassnames = []
import Disk_Folder_File_Suite
import Standard_Suite
import Folder_Actions_Suite
import Login_Items_Suite
application._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'folder_actions_enabled': _Prop_folder_actions_enabled,
 'properties': _Prop_properties}
application._privelemdict = {'application_process': application_process,
 'desk_accessory_process': desk_accessory_process,
 'disk': Disk_Folder_File_Suite.disk,
 'document': Standard_Suite.document,
 'file': Disk_Folder_File_Suite.file,
 'folder': Disk_Folder_File_Suite.folder,
 'folder_action': Folder_Actions_Suite.folder_action,
 'item': Disk_Folder_File_Suite.item,
 'login_item': Login_Items_Suite.login_item,
 'process': process,
 'window': Standard_Suite.window}
application_process._superclassnames = ['process']
application_process._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'application_file': _Prop_application_file}
application_process._privelemdict = {}
desk_accessory_process._superclassnames = ['process']
desk_accessory_process._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'desk_accessory_file': _Prop_desk_accessory_file}
desk_accessory_process._privelemdict = {}
process._superclassnames = ['item']
process._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'accepts_high_level_events': _Prop_accepts_high_level_events,
 'accepts_remote_events': _Prop_accepts_remote_events,
 'classic': _Prop_classic,
 'creator_type': _Prop_creator_type,
 'file': _Prop_file,
 'file_type': _Prop_file_type,
 'frontmost': _Prop_frontmost,
 'has_scripting_terminology': _Prop_has_scripting_terminology,
 'name': _Prop_name,
 'partition_space_used': _Prop_partition_space_used,
 'properties': _Prop_properties,
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
 'clsc': _Prop_classic,
 'dafi': _Prop_desk_accessory_file,
 'faen': _Prop_folder_actions_enabled,
 'fcrt': _Prop_creator_type,
 'file': _Prop_file,
 'hscr': _Prop_has_scripting_terminology,
 'isab': _Prop_accepts_high_level_events,
 'pALL': _Prop_properties,
 'pisf': _Prop_frontmost,
 'pnam': _Prop_name,
 'pusd': _Prop_partition_space_used,
 'pvis': _Prop_visible,
 'revt': _Prop_accepts_remote_events}
_compdeclarations = {}
_enumdeclarations = {}
