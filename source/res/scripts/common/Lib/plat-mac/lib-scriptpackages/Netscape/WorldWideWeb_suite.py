# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Netscape/WorldWideWeb_suite.py
import aetools
import MacOS
_code = 'WWW!'

class WorldWideWeb_suite_Events():
    _argmap_OpenURL = {'to': 'INTO',
     'toWindow': 'WIND',
     'flags': 'FLGS',
     'post_data': 'POST',
     'post_type': 'MIME',
     'progressApp': 'PROG'}

    def OpenURL(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'OURL'
        aetools.keysubst(_arguments, self._argmap_OpenURL)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_ShowFile = {'MIME_type': 'MIME',
     'Window_ID': 'WIND',
     'URL': 'URL '}

    def ShowFile(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'SHWF'
        aetools.keysubst(_arguments, self._argmap_ShowFile)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_cancel_progress = {'in_window': 'WIND'}

    def cancel_progress(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'CNCL'
        aetools.keysubst(_arguments, self._argmap_cancel_progress)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def find_URL(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'FURL'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def get_window_info(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'WNFO'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def list_windows(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'LSTW'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_parse_anchor = {'relative_to': 'RELA'}

    def parse_anchor(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'PRSA'
        aetools.keysubst(_arguments, self._argmap_parse_anchor)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def register_URL_echo(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'RGUE'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_register_protocol = {'for_protocol': 'PROT'}

    def register_protocol(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'RGPR'
        aetools.keysubst(_arguments, self._argmap_register_protocol)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_register_viewer = {'MIME_type': 'MIME',
     'with_file_type': 'FTYP'}

    def register_viewer(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'RGVW'
        aetools.keysubst(_arguments, self._argmap_register_viewer)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_register_window_close = {'for_window': 'WIND'}

    def register_window_close(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'RGWC'
        aetools.keysubst(_arguments, self._argmap_register_window_close)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def unregister_URL_echo(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'UNRU'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_unregister_protocol = {'for_protocol': 'PROT'}

    def unregister_protocol(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'UNRP'
        aetools.keysubst(_arguments, self._argmap_unregister_protocol)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_unregister_viewer = {'MIME_type': 'MIME'}

    def unregister_viewer(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'UNRV'
        aetools.keysubst(_arguments, self._argmap_unregister_viewer)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_unregister_window_close = {'for_window': 'WIND'}

    def unregister_window_close(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'UNRC'
        aetools.keysubst(_arguments, self._argmap_unregister_window_close)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def webActivate(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'ACTV'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {}
