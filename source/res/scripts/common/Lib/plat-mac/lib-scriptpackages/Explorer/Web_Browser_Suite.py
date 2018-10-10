# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Explorer/Web_Browser_Suite.py
import aetools
import MacOS
_code = 'WWW!'

class Web_Browser_Suite_Events:

    def Activate(self, _object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'ACTV'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def CloseAllWindows(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'CLSA'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_CloseWindow = {'ID': 'WIND',
     'Title': 'TITL'}

    def CloseWindow(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'CLOS'
        aetools.keysubst(_arguments, self._argmap_CloseWindow)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def GetWindowInfo(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'WNFO'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def ListWindows(self, _no_object=None, _attributes={}, **_arguments):
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

    _argmap_OpenURL = {'to': 'INTO',
     'toWindow': 'WIND',
     'Flags': 'FLGS',
     'FormData': 'POST',
     'MIME_Type': 'MIME'}

    def OpenURL(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'OURL'
        aetools.keysubst(_arguments, self._argmap_OpenURL)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_ParseAnchor = {'withURL': 'RELA'}

    def ParseAnchor(self, _object, _attributes={}, **_arguments):
        _code = 'WWW!'
        _subcode = 'PRSA'
        aetools.keysubst(_arguments, self._argmap_ParseAnchor)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_ShowFile = {'MIME_Type': 'MIME',
     'Window_Identifier': 'WIND',
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


_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {}
