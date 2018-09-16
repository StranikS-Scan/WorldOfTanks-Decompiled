# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Finder/Files.py
import aetools
import MacOS
_code = 'fndr'

class Files_Events:
    pass


class alias_file(aetools.ComponentItem):
    want = 'alia'


class _Prop__3c_Inheritance_3e_(aetools.NProperty):
    which = 'c@#^'
    want = 'file'


class _Prop_original_item(aetools.NProperty):
    which = 'orig'
    want = 'obj '


alias_files = alias_file

class application_file(aetools.ComponentItem):
    want = 'appf'


class _Prop_accepts_high_level_events(aetools.NProperty):
    which = 'isab'
    want = 'bool'


class _Prop_has_scripting_terminology(aetools.NProperty):
    which = 'hscr'
    want = 'bool'


class _Prop_minimum_size(aetools.NProperty):
    which = 'mprt'
    want = 'long'


class _Prop_opens_in_Classic(aetools.NProperty):
    which = 'Clsc'
    want = 'bool'


class _Prop_preferred_size(aetools.NProperty):
    which = 'appt'
    want = 'long'


class _Prop_suggested_size(aetools.NProperty):
    which = 'sprt'
    want = 'long'


application_files = application_file

class clipping(aetools.ComponentItem):
    want = 'clpf'


class _Prop_clipping_window(aetools.NProperty):
    which = 'lwnd'
    want = 'obj '


clippings = clipping

class document_file(aetools.ComponentItem):
    want = 'docf'


document_files = document_file

class file(aetools.ComponentItem):
    want = 'file'


class _Prop_creator_type(aetools.NProperty):
    which = 'fcrt'
    want = 'type'


class _Prop_file_type(aetools.NProperty):
    which = 'asty'
    want = 'type'


class _Prop_product_version(aetools.NProperty):
    which = 'ver2'
    want = 'utxt'


class _Prop_stationery(aetools.NProperty):
    which = 'pspd'
    want = 'bool'


class _Prop_version(aetools.NProperty):
    which = 'vers'
    want = 'utxt'


files = file

class internet_location_file(aetools.ComponentItem):
    want = 'inlf'


class _Prop_location(aetools.NProperty):
    which = 'iloc'
    want = 'utxt'


internet_location_files = internet_location_file

class package(aetools.ComponentItem):
    want = 'pack'


packages = package
alias_file._superclassnames = ['file']
alias_file._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'original_item': _Prop_original_item}
alias_file._privelemdict = {}
application_file._superclassnames = ['file']
application_file._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'accepts_high_level_events': _Prop_accepts_high_level_events,
 'has_scripting_terminology': _Prop_has_scripting_terminology,
 'minimum_size': _Prop_minimum_size,
 'opens_in_Classic': _Prop_opens_in_Classic,
 'preferred_size': _Prop_preferred_size,
 'suggested_size': _Prop_suggested_size}
application_file._privelemdict = {}
clipping._superclassnames = ['file']
clipping._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'clipping_window': _Prop_clipping_window}
clipping._privelemdict = {}
document_file._superclassnames = ['file']
document_file._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_}
document_file._privelemdict = {}
import Finder_items
file._superclassnames = ['item']
file._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'creator_type': _Prop_creator_type,
 'file_type': _Prop_file_type,
 'product_version': _Prop_product_version,
 'stationery': _Prop_stationery,
 'version': _Prop_version}
file._privelemdict = {}
internet_location_file._superclassnames = ['file']
internet_location_file._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'location': _Prop_location}
internet_location_file._privelemdict = {}
package._superclassnames = ['item']
package._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_}
package._privelemdict = {}
_classdeclarations = {'alia': alias_file,
 'appf': application_file,
 'clpf': clipping,
 'docf': document_file,
 'file': file,
 'inlf': internet_location_file,
 'pack': package}
_propdeclarations = {'Clsc': _Prop_opens_in_Classic,
 'appt': _Prop_preferred_size,
 'asty': _Prop_file_type,
 'c@#^': _Prop__3c_Inheritance_3e_,
 'fcrt': _Prop_creator_type,
 'hscr': _Prop_has_scripting_terminology,
 'iloc': _Prop_location,
 'isab': _Prop_accepts_high_level_events,
 'lwnd': _Prop_clipping_window,
 'mprt': _Prop_minimum_size,
 'orig': _Prop_original_item,
 'pspd': _Prop_stationery,
 'sprt': _Prop_suggested_size,
 'ver2': _Prop_product_version,
 'vers': _Prop_version}
_compdeclarations = {}
_enumdeclarations = {}
