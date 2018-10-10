# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/SystemEvents/Disk_Folder_File_Suite.py
import aetools
import MacOS
_code = 'cdis'

class Disk_Folder_File_Suite_Events:
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

class disk(aetools.ComponentItem):
    want = 'cdis'


class _Prop_POSIX_path(aetools.NProperty):
    which = 'posx'
    want = 'utxt'


class _Prop_capacity(aetools.NProperty):
    which = 'capa'
    want = 'magn'


class _Prop_ejectable(aetools.NProperty):
    which = 'isej'
    want = 'bool'


class _Prop_format(aetools.NProperty):
    which = 'dfmt'
    want = 'edfm'


class _Prop_free_space(aetools.NProperty):
    which = 'frsp'
    want = 'magn'


class _Prop_ignore_privileges(aetools.NProperty):
    which = 'igpr'
    want = 'bool'


class _Prop_local_volume(aetools.NProperty):
    which = 'isrv'
    want = 'bool'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'utxt'


class _Prop_path(aetools.NProperty):
    which = 'ppth'
    want = 'utxt'


class _Prop_startup(aetools.NProperty):
    which = 'istd'
    want = 'bool'


class _Prop_volume(aetools.NProperty):
    which = 'volu'
    want = 'utxt'


disks = disk

class folder(aetools.ComponentItem):
    want = 'cfol'


folders = folder

class item(aetools.ComponentItem):
    want = 'cobj'


class _Prop_busy_status(aetools.NProperty):
    which = 'busy'
    want = 'bool'


class _Prop_creation_date(aetools.NProperty):
    which = 'ascd'
    want = '****'


class _Prop_modification_date(aetools.NProperty):
    which = 'asmo'
    want = '****'


class _Prop_name_extension(aetools.NProperty):
    which = 'extn'
    want = 'utxt'


class _Prop_package_folder(aetools.NProperty):
    which = 'pkgf'
    want = 'bool'


class _Prop_url(aetools.NProperty):
    which = 'url '
    want = 'utxt'


class _Prop_visible(aetools.NProperty):
    which = 'visi'
    want = 'bool'


items = item

class file(aetools.ComponentItem):
    want = 'file'


class _Prop_creator_type(aetools.NProperty):
    which = 'fcrt'
    want = 'utxt'


class _Prop_file_type(aetools.NProperty):
    which = 'asty'
    want = 'utxt'


class _Prop_physical_size(aetools.NProperty):
    which = 'phys'
    want = 'magn'


class _Prop_product_version(aetools.NProperty):
    which = 'ver2'
    want = 'utxt'


class _Prop_size(aetools.NProperty):
    which = 'ptsz'
    want = 'magn'


class _Prop_stationery(aetools.NProperty):
    which = 'pspd'
    want = 'bool'


class _Prop_version(aetools.NProperty):
    which = 'vers'
    want = 'utxt'


files = file
application._superclassnames = []
import Standard_Suite
import Folder_Actions_Suite
import Login_Items_Suite
import Processes_Suite
application._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'folder_actions_enabled': _Prop_folder_actions_enabled,
 'properties': _Prop_properties}
application._privelemdict = {'application_process': Processes_Suite.application_process,
 'desk_accessory_process': Processes_Suite.desk_accessory_process,
 'disk': disk,
 'document': Standard_Suite.document,
 'file': file,
 'folder': folder,
 'folder_action': Folder_Actions_Suite.folder_action,
 'item': item,
 'login_item': Login_Items_Suite.login_item,
 'process': Processes_Suite.process,
 'window': Standard_Suite.window}
disk._superclassnames = ['item']
disk._privpropdict = {'POSIX_path': _Prop_POSIX_path,
 '_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'capacity': _Prop_capacity,
 'ejectable': _Prop_ejectable,
 'format': _Prop_format,
 'free_space': _Prop_free_space,
 'ignore_privileges': _Prop_ignore_privileges,
 'local_volume': _Prop_local_volume,
 'name': _Prop_name,
 'path': _Prop_path,
 'properties': _Prop_properties,
 'startup': _Prop_startup,
 'volume': _Prop_volume}
disk._privelemdict = {'file': file,
 'folder': folder,
 'item': item}
folder._superclassnames = ['item']
folder._privpropdict = {'POSIX_path': _Prop_POSIX_path,
 '_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'name': _Prop_name,
 'path': _Prop_path,
 'properties': _Prop_properties,
 'volume': _Prop_volume}
folder._privelemdict = {'file': file,
 'file': file,
 'folder': folder,
 'folder': folder,
 'item': item,
 'item': item}
item._superclassnames = []
item._privpropdict = {'POSIX_path': _Prop_POSIX_path,
 '_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'busy_status': _Prop_busy_status,
 'creation_date': _Prop_creation_date,
 'modification_date': _Prop_modification_date,
 'name': _Prop_name,
 'name_extension': _Prop_name_extension,
 'package_folder': _Prop_package_folder,
 'path': _Prop_path,
 'properties': _Prop_properties,
 'url': _Prop_url,
 'visible': _Prop_visible,
 'volume': _Prop_volume}
item._privelemdict = {'file': file,
 'folder': folder,
 'item': item}
file._superclassnames = ['item']
file._privpropdict = {'POSIX_path': _Prop_POSIX_path,
 '_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'creator_type': _Prop_creator_type,
 'file_type': _Prop_file_type,
 'name': _Prop_name,
 'path': _Prop_path,
 'physical_size': _Prop_physical_size,
 'product_version': _Prop_product_version,
 'properties': _Prop_properties,
 'size': _Prop_size,
 'stationery': _Prop_stationery,
 'version': _Prop_version,
 'volume': _Prop_volume}
file._privelemdict = {'file': file,
 'folder': folder,
 'item': item}
_Enum_edfm = {'MS_2d_DOS_format': 'dfms',
 'Apple_Photo_format': 'dfph',
 'ISO_9660_format': 'df96',
 'QuickTake_format': 'dfqt',
 'AppleShare_format': 'dfas',
 'High_Sierra_format': 'dfhs',
 'Mac_OS_Extended_format': 'dfh+',
 'UDF_format': 'dfud',
 'unknown_format': 'df??',
 'audio_format': 'dfau',
 'Mac_OS_format': 'dfhf',
 'UFS_format': 'dfuf',
 'NFS_format': 'dfnf',
 'ProDOS_format': 'dfpr',
 'WebDAV_format': 'dfwd'}
_classdeclarations = {'capp': application,
 'cdis': disk,
 'cfol': folder,
 'cobj': item,
 'file': file}
_propdeclarations = {'ascd': _Prop_creation_date,
 'asmo': _Prop_modification_date,
 'asty': _Prop_file_type,
 'busy': _Prop_busy_status,
 'c@#^': _Prop__3c_Inheritance_3e_,
 'capa': _Prop_capacity,
 'dfmt': _Prop_format,
 'extn': _Prop_name_extension,
 'faen': _Prop_folder_actions_enabled,
 'fcrt': _Prop_creator_type,
 'frsp': _Prop_free_space,
 'igpr': _Prop_ignore_privileges,
 'isej': _Prop_ejectable,
 'isrv': _Prop_local_volume,
 'istd': _Prop_startup,
 'pALL': _Prop_properties,
 'phys': _Prop_physical_size,
 'pkgf': _Prop_package_folder,
 'pnam': _Prop_name,
 'posx': _Prop_POSIX_path,
 'ppth': _Prop_path,
 'pspd': _Prop_stationery,
 'ptsz': _Prop_size,
 'url ': _Prop_url,
 'ver2': _Prop_product_version,
 'vers': _Prop_version,
 'visi': _Prop_visible,
 'volu': _Prop_volume}
_compdeclarations = {}
_enumdeclarations = {'edfm': _Enum_edfm}
