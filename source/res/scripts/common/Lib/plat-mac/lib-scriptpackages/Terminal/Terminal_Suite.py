# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Terminal/Terminal_Suite.py
import aetools
import MacOS
_code = 'trmx'

class Terminal_Suite_Events:

    def GetURL(self, _object, _attributes={}, **_arguments):
        _code = 'GURL'
        _subcode = 'GURL'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_do_script = {'in_': 'kfil',
     'with_command': 'cmnd'}

    def do_script(self, _object, _attributes={}, **_arguments):
        _code = 'core'
        _subcode = 'dosc'
        aetools.keysubst(_arguments, self._argmap_do_script)
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

class _Prop_properties(aetools.NProperty):
    which = 'pALL'
    want = '****'


properties = _Prop_properties()
applications = application

class window(aetools.ComponentItem):
    want = 'cwin'


class _Prop_background_color(aetools.NProperty):
    which = 'pbcl'
    want = '****'


class _Prop_bold_text_color(aetools.NProperty):
    which = 'pbtc'
    want = '****'


class _Prop_bounds(aetools.NProperty):
    which = 'pbnd'
    want = '****'


class _Prop_busy(aetools.NProperty):
    which = 'busy'
    want = 'bool'


class _Prop_contents(aetools.NProperty):
    which = 'pcnt'
    want = 'utxt'


class _Prop_cursor_color(aetools.NProperty):
    which = 'pcuc'
    want = '****'


class _Prop_custom_title(aetools.NProperty):
    which = 'titl'
    want = 'utxt'


class _Prop_frame(aetools.NProperty):
    which = 'pfra'
    want = '****'


class _Prop_frontmost(aetools.NProperty):
    which = 'pisf'
    want = 'bool'


class _Prop_history(aetools.NProperty):
    which = 'hist'
    want = 'utxt'


class _Prop_normal_text_color(aetools.NProperty):
    which = 'ptxc'
    want = '****'


class _Prop_number_of_columns(aetools.NProperty):
    which = 'ccol'
    want = 'long'


class _Prop_number_of_rows(aetools.NProperty):
    which = 'crow'
    want = 'long'


class _Prop_origin(aetools.NProperty):
    which = 'pori'
    want = '****'


class _Prop_position(aetools.NProperty):
    which = 'ppos'
    want = '****'


class _Prop_processes(aetools.NProperty):
    which = 'prcs'
    want = 'utxt'


class _Prop_size(aetools.NProperty):
    which = 'psiz'
    want = '****'


class _Prop_title_displays_custom_title(aetools.NProperty):
    which = 'tdct'
    want = 'bool'


class _Prop_title_displays_device_name(aetools.NProperty):
    which = 'tddn'
    want = 'bool'


class _Prop_title_displays_file_name(aetools.NProperty):
    which = 'tdfn'
    want = 'bool'


class _Prop_title_displays_shell_path(aetools.NProperty):
    which = 'tdsp'
    want = 'bool'


class _Prop_title_displays_window_size(aetools.NProperty):
    which = 'tdws'
    want = 'bool'


windows = window
application._superclassnames = []
import Standard_Suite
application._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'properties': _Prop_properties}
application._privelemdict = {'document': Standard_Suite.document,
 'window': window}
window._superclassnames = []
window._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'background_color': _Prop_background_color,
 'bold_text_color': _Prop_bold_text_color,
 'bounds': _Prop_bounds,
 'busy': _Prop_busy,
 'contents': _Prop_contents,
 'cursor_color': _Prop_cursor_color,
 'custom_title': _Prop_custom_title,
 'frame': _Prop_frame,
 'frontmost': _Prop_frontmost,
 'history': _Prop_history,
 'normal_text_color': _Prop_normal_text_color,
 'number_of_columns': _Prop_number_of_columns,
 'number_of_rows': _Prop_number_of_rows,
 'origin': _Prop_origin,
 'position': _Prop_position,
 'processes': _Prop_processes,
 'properties': _Prop_properties,
 'size': _Prop_size,
 'title_displays_custom_title': _Prop_title_displays_custom_title,
 'title_displays_device_name': _Prop_title_displays_device_name,
 'title_displays_file_name': _Prop_title_displays_file_name,
 'title_displays_shell_path': _Prop_title_displays_shell_path,
 'title_displays_window_size': _Prop_title_displays_window_size}
window._privelemdict = {}
_classdeclarations = {'capp': application,
 'cwin': window}
_propdeclarations = {'busy': _Prop_busy,
 'c@#^': _Prop__3c_Inheritance_3e_,
 'ccol': _Prop_number_of_columns,
 'crow': _Prop_number_of_rows,
 'hist': _Prop_history,
 'pALL': _Prop_properties,
 'pbcl': _Prop_background_color,
 'pbnd': _Prop_bounds,
 'pbtc': _Prop_bold_text_color,
 'pcnt': _Prop_contents,
 'pcuc': _Prop_cursor_color,
 'pfra': _Prop_frame,
 'pisf': _Prop_frontmost,
 'pori': _Prop_origin,
 'ppos': _Prop_position,
 'prcs': _Prop_processes,
 'psiz': _Prop_size,
 'ptxc': _Prop_normal_text_color,
 'tdct': _Prop_title_displays_custom_title,
 'tddn': _Prop_title_displays_device_name,
 'tdfn': _Prop_title_displays_file_name,
 'tdsp': _Prop_title_displays_shell_path,
 'tdws': _Prop_title_displays_window_size,
 'titl': _Prop_custom_title}
_compdeclarations = {}
_enumdeclarations = {}
