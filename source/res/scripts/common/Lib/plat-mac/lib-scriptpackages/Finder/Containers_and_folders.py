# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Finder/Containers_and_folders.py
import aetools
import MacOS
_code = 'fndr'

class Containers_and_folders_Events:
    pass


class disk(aetools.ComponentItem):
    want = 'cdis'


class _Prop__3c_Inheritance_3e_(aetools.NProperty):
    which = 'c@#^'
    want = 'ctnr'


class _Prop_capacity(aetools.NProperty):
    which = 'capa'
    want = 'comp'


class _Prop_ejectable(aetools.NProperty):
    which = 'isej'
    want = 'bool'


class _Prop_format(aetools.NProperty):
    which = 'dfmt'
    want = 'edfm'


class _Prop_free_space(aetools.NProperty):
    which = 'frsp'
    want = 'comp'


class _Prop_ignore_privileges(aetools.NProperty):
    which = 'igpr'
    want = 'bool'


class _Prop_local_volume(aetools.NProperty):
    which = 'isrv'
    want = 'bool'


class _Prop_startup(aetools.NProperty):
    which = 'istd'
    want = 'bool'


disks = disk

class desktop_2d_object(aetools.ComponentItem):
    want = 'cdsk'


class folder(aetools.ComponentItem):
    want = 'cfol'


folders = folder

class container(aetools.ComponentItem):
    want = 'ctnr'


class _Prop_completely_expanded(aetools.NProperty):
    which = 'pexc'
    want = 'bool'


class _Prop_container_window(aetools.NProperty):
    which = 'cwnd'
    want = 'obj '


class _Prop_entire_contents(aetools.NProperty):
    which = 'ects'
    want = 'obj '


class _Prop_expandable(aetools.NProperty):
    which = 'pexa'
    want = 'bool'


class _Prop_expanded(aetools.NProperty):
    which = 'pexp'
    want = 'bool'


containers = container

class trash_2d_object(aetools.ComponentItem):
    want = 'ctrs'


class _Prop_warns_before_emptying(aetools.NProperty):
    which = 'warn'
    want = 'bool'


disk._superclassnames = ['container']
import Files
import Finder_items
disk._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'capacity': _Prop_capacity,
 'ejectable': _Prop_ejectable,
 'format': _Prop_format,
 'free_space': _Prop_free_space,
 'ignore_privileges': _Prop_ignore_privileges,
 'local_volume': _Prop_local_volume,
 'startup': _Prop_startup}
disk._privelemdict = {'alias_file': Files.alias_file,
 'application_file': Files.application_file,
 'clipping': Files.clipping,
 'container': container,
 'document_file': Files.document_file,
 'file': Files.file,
 'folder': folder,
 'internet_location_file': Files.internet_location_file,
 'item': Finder_items.item,
 'package': Files.package}
desktop_2d_object._superclassnames = ['container']
desktop_2d_object._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_}
desktop_2d_object._privelemdict = {'alias_file': Files.alias_file,
 'application_file': Files.application_file,
 'clipping': Files.clipping,
 'container': container,
 'disk': disk,
 'document_file': Files.document_file,
 'file': Files.file,
 'folder': folder,
 'internet_location_file': Files.internet_location_file,
 'item': Finder_items.item,
 'package': Files.package}
folder._superclassnames = ['container']
folder._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_}
folder._privelemdict = {'alias_file': Files.alias_file,
 'application_file': Files.application_file,
 'clipping': Files.clipping,
 'container': container,
 'document_file': Files.document_file,
 'file': Files.file,
 'folder': folder,
 'internet_location_file': Files.internet_location_file,
 'item': Finder_items.item,
 'package': Files.package}
container._superclassnames = ['item']
container._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'completely_expanded': _Prop_completely_expanded,
 'container_window': _Prop_container_window,
 'entire_contents': _Prop_entire_contents,
 'expandable': _Prop_expandable,
 'expanded': _Prop_expanded}
container._privelemdict = {'alias_file': Files.alias_file,
 'application_file': Files.application_file,
 'clipping': Files.clipping,
 'container': container,
 'document_file': Files.document_file,
 'file': Files.file,
 'folder': folder,
 'internet_location_file': Files.internet_location_file,
 'item': Finder_items.item,
 'package': Files.package}
trash_2d_object._superclassnames = ['container']
trash_2d_object._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'warns_before_emptying': _Prop_warns_before_emptying}
trash_2d_object._privelemdict = {'alias_file': Files.alias_file,
 'application_file': Files.application_file,
 'clipping': Files.clipping,
 'container': container,
 'document_file': Files.document_file,
 'file': Files.file,
 'folder': folder,
 'internet_location_file': Files.internet_location_file,
 'item': Finder_items.item,
 'package': Files.package}
_classdeclarations = {'cdis': disk,
 'cdsk': desktop_2d_object,
 'cfol': folder,
 'ctnr': container,
 'ctrs': trash_2d_object}
_propdeclarations = {'c@#^': _Prop__3c_Inheritance_3e_,
 'capa': _Prop_capacity,
 'cwnd': _Prop_container_window,
 'dfmt': _Prop_format,
 'ects': _Prop_entire_contents,
 'frsp': _Prop_free_space,
 'igpr': _Prop_ignore_privileges,
 'isej': _Prop_ejectable,
 'isrv': _Prop_local_volume,
 'istd': _Prop_startup,
 'pexa': _Prop_expandable,
 'pexc': _Prop_completely_expanded,
 'pexp': _Prop_expanded,
 'warn': _Prop_warns_before_emptying}
_compdeclarations = {}
_enumdeclarations = {}
