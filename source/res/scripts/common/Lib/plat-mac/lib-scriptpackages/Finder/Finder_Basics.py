# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Finder/Finder_Basics.py
import aetools
import MacOS
_code = 'fndr'

class Finder_Basics_Events:

    def copy(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'misc'
        _subcode = 'copy'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_sort = {'by': 'by  '}

    def sort(self, _object, _attributes={}, **_arguments):
        _code = 'DATA'
        _subcode = 'SORT'
        aetools.keysubst(_arguments, self._argmap_sort)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


class application(aetools.ComponentItem):
    want = 'capp'


class _Prop_Finder_preferences(aetools.NProperty):
    which = 'pfrp'
    want = 'cprf'


Finder_preferences = _Prop_Finder_preferences()

class _Prop_clipboard(aetools.NProperty):
    which = 'pcli'
    want = 'obj '


clipboard = _Prop_clipboard()

class _Prop_desktop(aetools.NProperty):
    which = 'desk'
    want = 'cdsk'


desktop = _Prop_desktop()

class _Prop_frontmost(aetools.NProperty):
    which = 'pisf'
    want = 'bool'


frontmost = _Prop_frontmost()

class _Prop_home(aetools.NProperty):
    which = 'home'
    want = 'cfol'


home = _Prop_home()

class _Prop_insertion_location(aetools.NProperty):
    which = 'pins'
    want = 'obj '


insertion_location = _Prop_insertion_location()

class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'itxt'


name = _Prop_name()

class _Prop_product_version(aetools.NProperty):
    which = 'ver2'
    want = 'utxt'


product_version = _Prop_product_version()

class _Prop_selection(aetools.NProperty):
    which = 'sele'
    want = 'obj '


selection = _Prop_selection()

class _Prop_startup_disk(aetools.NProperty):
    which = 'sdsk'
    want = 'cdis'


startup_disk = _Prop_startup_disk()

class _Prop_trash(aetools.NProperty):
    which = 'trsh'
    want = 'ctrs'


trash = _Prop_trash()

class _Prop_version(aetools.NProperty):
    which = 'vers'
    want = 'utxt'


version = _Prop_version()

class _Prop_visible(aetools.NProperty):
    which = 'pvis'
    want = 'bool'


visible = _Prop_visible()
application._superclassnames = []
import Files
import Window_classes
import Containers_and_folders
import Finder_items
application._privpropdict = {'Finder_preferences': _Prop_Finder_preferences,
 'clipboard': _Prop_clipboard,
 'desktop': _Prop_desktop,
 'frontmost': _Prop_frontmost,
 'home': _Prop_home,
 'insertion_location': _Prop_insertion_location,
 'name': _Prop_name,
 'product_version': _Prop_product_version,
 'selection': _Prop_selection,
 'startup_disk': _Prop_startup_disk,
 'trash': _Prop_trash,
 'version': _Prop_version,
 'visible': _Prop_visible}
application._privelemdict = {'Finder_window': Window_classes.Finder_window,
 'alias_file': Files.alias_file,
 'application_file': Files.application_file,
 'clipping': Files.clipping,
 'clipping_window': Window_classes.clipping_window,
 'container': Containers_and_folders.container,
 'disk': Containers_and_folders.disk,
 'document_file': Files.document_file,
 'file': Files.file,
 'folder': Containers_and_folders.folder,
 'internet_location_file': Files.internet_location_file,
 'item': Finder_items.item,
 'package': Files.package,
 'window': Window_classes.window}
_classdeclarations = {'capp': application}
_propdeclarations = {'desk': _Prop_desktop,
 'home': _Prop_home,
 'pcli': _Prop_clipboard,
 'pfrp': _Prop_Finder_preferences,
 'pins': _Prop_insertion_location,
 'pisf': _Prop_frontmost,
 'pnam': _Prop_name,
 'pvis': _Prop_visible,
 'sdsk': _Prop_startup_disk,
 'sele': _Prop_selection,
 'trsh': _Prop_trash,
 'ver2': _Prop_product_version,
 'vers': _Prop_version}
_compdeclarations = {}
_enumdeclarations = {}
