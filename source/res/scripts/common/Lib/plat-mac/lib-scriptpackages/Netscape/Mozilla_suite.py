# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Netscape/Mozilla_suite.py
import aetools
import MacOS
_code = 'MOSS'

class Mozilla_suite_Events:

    def Get_Import_Data(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'Impt'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Get_Profile_Name(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'upro'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Get_workingURL(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'wurl'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Go = {'direction': 'dire'}

    def Go(self, _object, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'gogo'
        aetools.keysubst(_arguments, self._argmap_Go)
        _arguments['----'] = _object
        aetools.enumsubst(_arguments, 'dire', _Enum_dire)
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Handle_command(self, _object, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'hcmd'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Open_Address_Book(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'addr'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Open_Component(self, _object, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'cpnt'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Open_Profile_Manager(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'prfl'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Open_bookmark(self, _object=None, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'book'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Read_help_file = {'with_index': 'idid',
     'search_text': 'sear'}

    def Read_help_file(self, _object, _attributes={}, **_arguments):
        _code = 'MOSS'
        _subcode = 'help'
        aetools.keysubst(_arguments, self._argmap_Read_help_file)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


_Enum_comp = {'Navigator': 'navg',
 'InBox': 'inbx',
 'Newsgroups': 'colb',
 'Composer': 'cpsr',
 'Conference': 'conf',
 'Calendar': 'cald'}
_Enum_dire = {'again': 'agai',
 'home': 'home',
 'backward': 'prev',
 'forward': 'next'}
_Enum_ncmd = {'Get_new_mail': '\x00\x00\x04W',
 'Send_queued_messages': '\x00\x00\x04X',
 'Read_newsgroups': '\x00\x00\x04\x04',
 'Show_Inbox': '\x00\x00\x04\x05',
 'Show_Bookmarks_window': '\x00\x00\x04\x06',
 'Show_History_window': '\x00\x00\x04\x07',
 'Show_Address_Book_window': '\x00\x00\x04\t'}
_classdeclarations = {}
_propdeclarations = {}
_compdeclarations = {}
_enumdeclarations = {'comp': _Enum_comp,
 'dire': _Enum_dire,
 'ncmd': _Enum_ncmd}
