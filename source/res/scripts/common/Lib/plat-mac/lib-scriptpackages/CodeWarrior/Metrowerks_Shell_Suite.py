# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/CodeWarrior/Metrowerks_Shell_Suite.py
import aetools
import MacOS
_code = 'MMPR'

class Metrowerks_Shell_Suite_Events():
    _argmap_Add_Files = {'To_Segment': 'Segm'}

    def Add_Files(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'AddF'
        aetools.keysubst(_arguments, self._argmap_Add_Files)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Check_Syntax = {'ExternalEditor': 'Errs'}

    def Check_Syntax(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'Chek'
        aetools.keysubst(_arguments, self._argmap_Check_Syntax)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Close_Project(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'ClsP'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Close_Window = {'Saving': 'savo'}

    def Close_Window(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'ClsW'
        aetools.keysubst(_arguments, self._argmap_Close_Window)
        _arguments['----'] = _object
        aetools.enumsubst(_arguments, 'savo', _Enum_savo)
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Compile = {'ExternalEditor': 'Errs'}

    def Compile(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'Comp'
        aetools.keysubst(_arguments, self._argmap_Compile)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Create_Project = {'from_stationery': 'Tmpl'}

    def Create_Project(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'NewP'
        aetools.keysubst(_arguments, self._argmap_Create_Project)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Get_Definition(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'GDef'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Get_Open_Documents(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'GDoc'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Get_Preferences = {'of': 'PRec',
     'from_panel': 'PNam'}

    def Get_Preferences(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'Gref'
        aetools.keysubst(_arguments, self._argmap_Get_Preferences)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Get_Project_File = {'Segment': 'Segm'}

    def Get_Project_File(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'GFil'
        aetools.keysubst(_arguments, self._argmap_Get_Project_File)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Get_Project_Specifier(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'GetP'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Get_Segments(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'GSeg'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Get_member_function_names(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'MbFN'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Get_nonsimple_classes(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'NsCl'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Goto_Function(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'GoFn'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Goto_Line(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'GoLn'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Is_In_Project(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'FInP'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Make_Project = {'ExternalEditor': 'Errs'}

    def Make_Project(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'Make'
        aetools.keysubst(_arguments, self._argmap_Make_Project)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Open_browser(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'Brow'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Precompile = {'Saving_As': 'Targ',
     'ExternalEditor': 'Errs'}

    def Precompile(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'PreC'
        aetools.keysubst(_arguments, self._argmap_Precompile)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Preprocess = {'ExternalEditor': 'Errs'}

    def Preprocess(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'PreP'
        aetools.keysubst(_arguments, self._argmap_Preprocess)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Remove_Binaries(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'RemB'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Remove_Files(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'RemF'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Reset_File_Paths(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'ReFP'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Run_Project = {'ExternalEditor': 'Errs',
     'SourceDebugger': 'DeBg'}

    def Run_Project(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'RunP'
        aetools.keysubst(_arguments, self._argmap_Run_Project)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Save_Error_Window_As(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'SvMs'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Set_Current_Target(self, _object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'STrg'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Set_Default_Project(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'SDfP'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Set_Modification_Date = {'to': 'MDat'}

    def Set_Modification_Date(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'SMod'
        aetools.keysubst(_arguments, self._argmap_Set_Modification_Date)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Set_Preferences = {'of_panel': 'PNam',
     'to': 'PRec'}

    def Set_Preferences(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'Pref'
        aetools.keysubst(_arguments, self._argmap_Set_Preferences)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Set_Project_File = {'to': 'SrcS'}

    def Set_Project_File(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'SFil'
        aetools.keysubst(_arguments, self._argmap_Set_Project_File)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Set_Segment = {'to': 'Segm'}

    def Set_Segment(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'SSeg'
        aetools.keysubst(_arguments, self._argmap_Set_Segment)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def Touch(self, _object, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'Toch'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_Update_Project = {'ExternalEditor': 'Errs'}

    def Update_Project(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'MMPR'
        _subcode = 'UpdP'
        aetools.keysubst(_arguments, self._argmap_Update_Project)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


class Browser_Coloring(aetools.ComponentItem):
    want = 'BRKW'


class _Prop_Browser_Keywords(aetools.NProperty):
    which = 'BW00'
    want = 'bool'


class _Prop_Classes_Color(aetools.NProperty):
    which = 'BW01'
    want = 'cRGB'


class _Prop_Constants_Color(aetools.NProperty):
    which = 'BW02'
    want = 'cRGB'


class _Prop_Enums_Color(aetools.NProperty):
    which = 'BW03'
    want = 'cRGB'


class _Prop_Functions_Color(aetools.NProperty):
    which = 'BW04'
    want = 'cRGB'


class _Prop_Globals_Color(aetools.NProperty):
    which = 'BW05'
    want = 'cRGB'


class _Prop_Macros_Color(aetools.NProperty):
    which = 'BW06'
    want = 'cRGB'


class _Prop_Template_Commands_in_Menu(aetools.NProperty):
    which = 'BW10'
    want = 'bool'


class _Prop_Templates_Color(aetools.NProperty):
    which = 'BW07'
    want = 'cRGB'


class _Prop_Typedefs_Color(aetools.NProperty):
    which = 'BW08'
    want = 'cRGB'


class Build_Settings(aetools.ComponentItem):
    want = 'BSTG'


class _Prop_Build_Before_Running(aetools.NProperty):
    which = 'BX04'
    want = 'BXbr'


class _Prop_Compiler_Thread_Stack_Size(aetools.NProperty):
    which = 'BX06'
    want = 'long'


class _Prop_Completion_Sound(aetools.NProperty):
    which = 'BX01'
    want = 'bool'


class _Prop_Failure_Sound(aetools.NProperty):
    which = 'BX03'
    want = 'TEXT'


class _Prop_Include_Cache_Size(aetools.NProperty):
    which = 'BX05'
    want = 'long'


class _Prop_Save_Before_Building(aetools.NProperty):
    which = 'BX07'
    want = 'bool'


class _Prop_Success_Sound(aetools.NProperty):
    which = 'BX02'
    want = 'TEXT'


class base_class(aetools.ComponentItem):
    want = 'BsCl'


class _Prop_access(aetools.NProperty):
    which = 'Acce'
    want = 'Acce'


class _Prop_class_(aetools.NProperty):
    which = 'Clas'
    want = 'obj '


class _Prop_virtual(aetools.NProperty):
    which = 'Virt'
    want = 'bool'


base_classes = base_class

class Custom_Keywords(aetools.ComponentItem):
    want = 'CUKW'


class _Prop_Custom_Color_1(aetools.NProperty):
    which = 'GH05'
    want = 'cRGB'


class _Prop_Custom_Color_2(aetools.NProperty):
    which = 'GH06'
    want = 'cRGB'


class _Prop_Custom_Color_3(aetools.NProperty):
    which = 'GH07'
    want = 'cRGB'


class _Prop_Custom_Color_4(aetools.NProperty):
    which = 'GH08'
    want = 'cRGB'


class browser_catalog(aetools.ComponentItem):
    want = 'Cata'


class class_(aetools.ComponentItem):
    want = 'Clas'


class _Prop_all_subclasses(aetools.NProperty):
    which = 'SubA'
    want = 'Clas'


class _Prop_declaration_end_offset(aetools.NProperty):
    which = 'DcEn'
    want = 'long'


class _Prop_declaration_file(aetools.NProperty):
    which = 'DcFl'
    want = 'fss '


class _Prop_declaration_start_offset(aetools.NProperty):
    which = 'DcSt'
    want = 'long'


class _Prop_language(aetools.NProperty):
    which = 'Lang'
    want = 'Lang'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'TEXT'


class _Prop_subclasses(aetools.NProperty):
    which = 'SubC'
    want = 'Clas'


classes = class_

class Debugger_Display(aetools.ComponentItem):
    want = 'DbDS'


class _Prop_Default_Array_Size(aetools.NProperty):
    which = 'Db08'
    want = 'shor'


class _Prop_Show_As_Decimal(aetools.NProperty):
    which = 'Db10'
    want = 'bool'


class _Prop_Show_Locals(aetools.NProperty):
    which = 'Db09'
    want = 'bool'


class _Prop_Show_Variable_Types(aetools.NProperty):
    which = 'Db01'
    want = 'bool'


class _Prop_Sort_By_Method(aetools.NProperty):
    which = 'Db02'
    want = 'bool'


class _Prop_Threads_in_Window(aetools.NProperty):
    which = 'Db04'
    want = 'bool'


class _Prop_Use_RTTI(aetools.NProperty):
    which = 'Db03'
    want = 'bool'


class _Prop_Variable_Changed_Hilite(aetools.NProperty):
    which = 'Db07'
    want = 'cRGB'


class _Prop_Variable_Hints(aetools.NProperty):
    which = 'Db05'
    want = 'bool'


class _Prop_Watchpoint_Hilite(aetools.NProperty):
    which = 'Db06'
    want = 'cRGB'


class Debugger_Global(aetools.ComponentItem):
    want = 'DbGL'


class _Prop_Auto_Target_Libraries(aetools.NProperty):
    which = 'Dg11'
    want = 'bool'


class _Prop_Cache_Edited_Files(aetools.NProperty):
    which = 'Dg12'
    want = 'bool'


class _Prop_Confirm_Kill(aetools.NProperty):
    which = 'Dg04'
    want = 'bool'


class _Prop_Dont_Step_in_Runtime(aetools.NProperty):
    which = 'Dg07'
    want = 'bool'


class _Prop_File_Cache_Duration(aetools.NProperty):
    which = 'Dg13'
    want = 'shor'


class _Prop_Ignore_Mod_Dates(aetools.NProperty):
    which = 'Dg01'
    want = 'bool'


class _Prop_Launch_Apps_on_Open(aetools.NProperty):
    which = 'Dg03'
    want = 'bool'


class _Prop_Open_All_Classes(aetools.NProperty):
    which = 'Dg02'
    want = 'bool'


class _Prop_Select_Stack_Crawl(aetools.NProperty):
    which = 'Dg06'
    want = 'bool'


class _Prop_Stop_at_Main(aetools.NProperty):
    which = 'Dg05'
    want = 'bool'


class Debugger_Target(aetools.ComponentItem):
    want = 'DbTG'


class _Prop_Cache_symbolics(aetools.NProperty):
    which = 'Dt15'
    want = 'bool'


class _Prop_Data_Update_Interval(aetools.NProperty):
    which = 'Dt09'
    want = 'long'


class _Prop_Log_System_Messages(aetools.NProperty):
    which = 'Dt02'
    want = 'bool'


class _Prop_Relocated_Executable_Path(aetools.NProperty):
    which = 'Dt10'
    want = 'RlPt'


class _Prop_Stop_at_temp_breakpoint(aetools.NProperty):
    which = 'Dt13'
    want = 'bool'


class _Prop_Temp_Breakpoint_Type(aetools.NProperty):
    which = 'Dt16'
    want = 'TmpB'


class _Prop_Temp_breakpoint_names(aetools.NProperty):
    which = 'Dt14'
    want = 'ctxt'


class _Prop_Update_Data_While_Running(aetools.NProperty):
    which = 'Dt08'
    want = 'bool'


class Debugger_Windowing(aetools.ComponentItem):
    want = 'DbWN'


class _Prop_Debugging_Start_Action(aetools.NProperty):
    which = 'Dw01'
    want = 'DbSA'


class _Prop_Do_Nothing_To_Projects(aetools.NProperty):
    which = 'Dw02'
    want = 'bool'


class data_member(aetools.ComponentItem):
    want = 'DtMb'


class _Prop_static(aetools.NProperty):
    which = 'Stat'
    want = 'bool'


data_members = data_member

class Editor(aetools.ComponentItem):
    want = 'EDTR'


class _Prop_Background_Color(aetools.NProperty):
    which = 'ED13'
    want = 'cRGB'


class _Prop_Balance(aetools.NProperty):
    which = 'ED03'
    want = 'bool'


class _Prop_Context_Popup_Delay(aetools.NProperty):
    which = 'ED14'
    want = 'long'


class _Prop_Default_Text_File_Format(aetools.NProperty):
    which = 'ED17'
    want = 'TxtF'


class _Prop_Dynamic_Scroll(aetools.NProperty):
    which = 'ED02'
    want = 'bool'


class _Prop_Flash_Delay(aetools.NProperty):
    which = 'ED01'
    want = 'long'


class _Prop_Left_Margin_Line_Select(aetools.NProperty):
    which = 'ED16'
    want = 'bool'


class _Prop_Main_Text_Color(aetools.NProperty):
    which = 'ED12'
    want = 'cRGB'


class _Prop_Relaxed_C_Popup_Parsing(aetools.NProperty):
    which = 'ED15'
    want = 'bool'


class _Prop_Remember_Font(aetools.NProperty):
    which = 'ED08'
    want = 'bool'


class _Prop_Remember_Selection(aetools.NProperty):
    which = 'ED09'
    want = 'bool'


class _Prop_Remember_Window(aetools.NProperty):
    which = 'ED10'
    want = 'bool'


class _Prop_Sort_Function_Popup(aetools.NProperty):
    which = 'ED06'
    want = 'bool'


class _Prop_Use_Drag__26__Drop_Editing(aetools.NProperty):
    which = 'ED04'
    want = 'bool'


class _Prop_Use_Multiple_Undo(aetools.NProperty):
    which = 'ED07'
    want = 'bool'


class Environment_Variable(aetools.ComponentItem):
    want = 'EnvV'


class _Prop_value(aetools.NProperty):
    which = 'Valu'
    want = 'TEXT'


class Error_Information(aetools.ComponentItem):
    want = 'ErrM'


class _Prop_disk_file(aetools.NProperty):
    which = 'file'
    want = 'fss '


class _Prop_lineNumber(aetools.NProperty):
    which = 'ErrL'
    want = 'long'


class _Prop_message(aetools.NProperty):
    which = 'ErrS'
    want = 'TEXT'


class _Prop_messageKind(aetools.NProperty):
    which = 'ErrT'
    want = 'ErrT'


class Function_Information(aetools.ComponentItem):
    want = 'FDef'


class File_Mappings(aetools.ComponentItem):
    want = 'FLMP'


class _Prop_Mappings(aetools.NProperty):
    which = 'FMps'
    want = 'FMap'


class File_Mapping(aetools.ComponentItem):
    want = 'FMap'


class _Prop_Compiler(aetools.NProperty):
    which = 'TA07'
    want = 'TEXT'


class _Prop_Extension(aetools.NProperty):
    which = 'TA02'
    want = 'TEXT'


class _Prop_File_Type(aetools.NProperty):
    which = 'PR04'
    want = 'TEXT'


class _Prop_Ignored_by_Make(aetools.NProperty):
    which = 'TA06'
    want = 'bool'


class _Prop_Launchable(aetools.NProperty):
    which = 'TA05'
    want = 'bool'


class _Prop_Precompiled(aetools.NProperty):
    which = 'TA03'
    want = 'bool'


class _Prop_Resource_File(aetools.NProperty):
    which = 'TA04'
    want = 'bool'


class Global_Source_Trees(aetools.ComponentItem):
    want = 'GSTs'


class _Prop_Source_Trees(aetools.NProperty):
    which = 'ST01'
    want = 'SrcT'


class Extras(aetools.ComponentItem):
    want = 'GXTR'


class _Prop_Automatic_Toolbar_Help(aetools.NProperty):
    which = 'EX19'
    want = 'bool'


class _Prop_External_Reference(aetools.NProperty):
    which = 'EX08'
    want = 'RefP'


class _Prop_Full_Screen_Zoom(aetools.NProperty):
    which = 'EX07'
    want = 'bool'


class _Prop_Recent_Editor_Count(aetools.NProperty):
    which = 'EX16'
    want = 'shor'


class _Prop_Recent_Project_Count(aetools.NProperty):
    which = 'EX17'
    want = 'shor'


class _Prop_Use_Editor_Extensions(aetools.NProperty):
    which = 'EX10'
    want = 'bool'


class _Prop_Use_External_Editor(aetools.NProperty):
    which = 'EX11'
    want = 'bool'


class _Prop_Use_Script_Menu(aetools.NProperty):
    which = 'EX12'
    want = 'bool'


class _Prop_Use_ToolServer_Menu(aetools.NProperty):
    which = 'EX18'
    want = 'bool'


class Build_Extras(aetools.ComponentItem):
    want = 'LXTR'


class _Prop_Browser_Active(aetools.NProperty):
    which = 'EX09'
    want = 'bool'


class _Prop_Cache_Subproject_Data(aetools.NProperty):
    which = 'EX31'
    want = 'bool'


class _Prop_Dump_Browser_Info(aetools.NProperty):
    which = 'EX30'
    want = 'bool'


class _Prop_Modification_Date_Caching(aetools.NProperty):
    which = 'EX04'
    want = 'bool'


class member_function(aetools.ComponentItem):
    want = 'MbFn'


class _Prop_implementation_end_offset(aetools.NProperty):
    which = 'DfEn'
    want = 'long'


class _Prop_implementation_file(aetools.NProperty):
    which = 'DfFl'
    want = 'fss '


class _Prop_implementation_start_offset(aetools.NProperty):
    which = 'DfSt'
    want = 'long'


member_functions = member_function

class Access_Paths(aetools.ComponentItem):
    want = 'PATH'


class _Prop_Always_Full_Search(aetools.NProperty):
    which = 'PA02'
    want = 'bool'


class _Prop_Convert_Paths(aetools.NProperty):
    which = 'PA04'
    want = 'bool'


class _Prop_Require_Framework_Includes(aetools.NProperty):
    which = 'PA05'
    want = 'bool'


class _Prop_System_Paths(aetools.NProperty):
    which = 'PA03'
    want = 'PInf'


class _Prop_User_Paths(aetools.NProperty):
    which = 'PA01'
    want = 'PInf'


class Path_Information(aetools.ComponentItem):
    want = 'PInf'


class _Prop_format(aetools.NProperty):
    which = 'Frmt'
    want = 'PthF'


class _Prop_framework(aetools.NProperty):
    which = 'Frmw'
    want = 'bool'


class _Prop_host_flags(aetools.NProperty):
    which = 'HstF'
    want = 'long'


class _Prop_origin(aetools.NProperty):
    which = 'Orig'
    want = 'PPrm'


class _Prop_recursive(aetools.NProperty):
    which = 'Recu'
    want = 'bool'


class _Prop_root(aetools.NProperty):
    which = 'Root'
    want = 'TEXT'


class Plugin_Settings(aetools.ComponentItem):
    want = 'PSTG'


class _Prop_Disable_Third_Party_COM_Plugins(aetools.NProperty):
    which = 'PX02'
    want = 'bool'


class _Prop_Plugin_Diagnostics_Level(aetools.NProperty):
    which = 'PX01'
    want = 'PXdg'


class Runtime_Settings(aetools.ComponentItem):
    want = 'RSTG'


class _Prop_Command_Line_Arguments(aetools.NProperty):
    which = 'RS02'
    want = 'TEXT'


class _Prop_Environment_Variables(aetools.NProperty):
    which = 'RS04'
    want = 'EnvV'


class _Prop_Host_Application(aetools.NProperty):
    which = 'RS01'
    want = 'RlPt'


class _Prop_Working_Directory(aetools.NProperty):
    which = 'RS03'
    want = 'TEXT'


class Relative_Path(aetools.ComponentItem):
    want = 'RlPt'


class Shielded_Folder(aetools.ComponentItem):
    want = 'SFit'


class _Prop_Expression_To_Match(aetools.NProperty):
    which = 'SF01'
    want = 'TEXT'


class _Prop_Skip_Find_And_Compare_Operations(aetools.NProperty):
    which = 'SF03'
    want = 'bool'


class _Prop_Skip_Project_Operations(aetools.NProperty):
    which = 'SF02'
    want = 'bool'


class Shielded_Folders(aetools.ComponentItem):
    want = 'SHFL'


class _Prop_Shielded_Items(aetools.NProperty):
    which = 'SFis'
    want = 'SFit'


class Syntax_Coloring(aetools.ComponentItem):
    want = 'SNTX'


class _Prop_Comment_Color(aetools.NProperty):
    which = 'GH02'
    want = 'cRGB'


class _Prop_Keyword_Color(aetools.NProperty):
    which = 'GH03'
    want = 'cRGB'


class _Prop_String_Color(aetools.NProperty):
    which = 'GH04'
    want = 'cRGB'


class _Prop_Syntax_Coloring(aetools.NProperty):
    which = 'GH01'
    want = 'bool'


class Segment(aetools.ComponentItem):
    want = 'Seg '


class _Prop_filecount(aetools.NProperty):
    which = 'NumF'
    want = 'shor'


class _Prop_seg_2d_locked(aetools.NProperty):
    which = 'PLck'
    want = 'bool'


class _Prop_seg_2d_preloaded(aetools.NProperty):
    which = 'Prel'
    want = 'bool'


class _Prop_seg_2d_protected(aetools.NProperty):
    which = 'Prot'
    want = 'bool'


class _Prop_seg_2d_purgeable(aetools.NProperty):
    which = 'Purg'
    want = 'bool'


class _Prop_seg_2d_system_heap(aetools.NProperty):
    which = 'SysH'
    want = 'bool'


class ProjectFile(aetools.ComponentItem):
    want = 'SrcF'


class _Prop_codesize(aetools.NProperty):
    which = 'CSiz'
    want = 'long'


class _Prop_datasize(aetools.NProperty):
    which = 'DSiz'
    want = 'long'


class _Prop_filetype(aetools.NProperty):
    which = 'SrcT'
    want = 'SrcT'


class _Prop_includes(aetools.NProperty):
    which = 'IncF'
    want = 'fss '


class _Prop_initialize_before(aetools.NProperty):
    which = 'Bfor'
    want = 'bool'


class _Prop_symbols(aetools.NProperty):
    which = 'SymG'
    want = 'bool'


class _Prop_up_to_date(aetools.NProperty):
    which = 'UpTD'
    want = 'bool'


class _Prop_weak_link(aetools.NProperty):
    which = 'Weak'
    want = 'bool'


class Source_Tree(aetools.ComponentItem):
    want = 'SrcT'


class _Prop_path(aetools.NProperty):
    which = 'Path'
    want = 'TEXT'


class _Prop_path_kind(aetools.NProperty):
    which = 'Kind'
    want = 'STKd'


class Target_Settings(aetools.ComponentItem):
    want = 'TARG'


class _Prop_Linker(aetools.NProperty):
    which = 'TA01'
    want = 'TEXT'


class _Prop_Output_Directory_Location(aetools.NProperty):
    which = 'TA16'
    want = 'RlPt'


class _Prop_Output_Directory_Origin(aetools.NProperty):
    which = 'TA12'
    want = 'PPrm'


class _Prop_Output_Directory_Path(aetools.NProperty):
    which = 'TA11'
    want = 'TEXT'


class _Prop_Post_Linker(aetools.NProperty):
    which = 'TA09'
    want = 'TEXT'


class _Prop_Pre_Linker(aetools.NProperty):
    which = 'TA13'
    want = 'TEXT'


class _Prop_Target_Name(aetools.NProperty):
    which = 'TA10'
    want = 'TEXT'


class _Prop_Use_Relative_Paths(aetools.NProperty):
    which = 'TA15'
    want = 'bool'


class Target_Source_Trees(aetools.ComponentItem):
    want = 'TSTs'


class VCS_Setup(aetools.ComponentItem):
    want = 'VCSs'


class _Prop_Always_Prompt(aetools.NProperty):
    which = 'VC07'
    want = 'bool'


class _Prop_Auto_Connect(aetools.NProperty):
    which = 'VC05'
    want = 'bool'


class _Prop_Connection_Method(aetools.NProperty):
    which = 'VC02'
    want = 'TEXT'


class _Prop_Database_Path(aetools.NProperty):
    which = 'VC09'
    want = 'RlPt'


class _Prop_Local_Path(aetools.NProperty):
    which = 'VC10'
    want = 'RlPt'


class _Prop_Mount_Volume(aetools.NProperty):
    which = 'VC08'
    want = 'bool'


class _Prop_Password(aetools.NProperty):
    which = 'VC04'
    want = 'TEXT'


class _Prop_Store_Password(aetools.NProperty):
    which = 'VC06'
    want = 'bool'


class _Prop_Use_Global_Settings(aetools.NProperty):
    which = 'VC11'
    want = 'bool'


class _Prop_Username(aetools.NProperty):
    which = 'VC03'
    want = 'TEXT'


class _Prop_VCS_Active(aetools.NProperty):
    which = 'VC01'
    want = 'bool'


class Font(aetools.ComponentItem):
    want = 'mFNT'


class _Prop_Auto_Indent(aetools.NProperty):
    which = 'FN01'
    want = 'bool'


class _Prop_Tab_Indents_Selection(aetools.NProperty):
    which = 'FN03'
    want = 'bool'


class _Prop_Tab_Inserts_Spaces(aetools.NProperty):
    which = 'FN04'
    want = 'bool'


class _Prop_Tab_Size(aetools.NProperty):
    which = 'FN02'
    want = 'shor'


class _Prop_Text_Font(aetools.NProperty):
    which = 'ptxf'
    want = 'TEXT'


class _Prop_Text_Size(aetools.NProperty):
    which = 'ptps'
    want = 'shor'


Browser_Coloring._superclassnames = []
Browser_Coloring._privpropdict = {'Browser_Keywords': _Prop_Browser_Keywords,
 'Classes_Color': _Prop_Classes_Color,
 'Constants_Color': _Prop_Constants_Color,
 'Enums_Color': _Prop_Enums_Color,
 'Functions_Color': _Prop_Functions_Color,
 'Globals_Color': _Prop_Globals_Color,
 'Macros_Color': _Prop_Macros_Color,
 'Template_Commands_in_Menu': _Prop_Template_Commands_in_Menu,
 'Templates_Color': _Prop_Templates_Color,
 'Typedefs_Color': _Prop_Typedefs_Color}
Browser_Coloring._privelemdict = {}
Build_Settings._superclassnames = []
Build_Settings._privpropdict = {'Build_Before_Running': _Prop_Build_Before_Running,
 'Compiler_Thread_Stack_Size': _Prop_Compiler_Thread_Stack_Size,
 'Completion_Sound': _Prop_Completion_Sound,
 'Failure_Sound': _Prop_Failure_Sound,
 'Include_Cache_Size': _Prop_Include_Cache_Size,
 'Save_Before_Building': _Prop_Save_Before_Building,
 'Success_Sound': _Prop_Success_Sound}
Build_Settings._privelemdict = {}
base_class._superclassnames = []
base_class._privpropdict = {'access': _Prop_access,
 'class_': _Prop_class_,
 'virtual': _Prop_virtual}
base_class._privelemdict = {}
Custom_Keywords._superclassnames = []
Custom_Keywords._privpropdict = {'Custom_Color_1': _Prop_Custom_Color_1,
 'Custom_Color_2': _Prop_Custom_Color_2,
 'Custom_Color_3': _Prop_Custom_Color_3,
 'Custom_Color_4': _Prop_Custom_Color_4}
Custom_Keywords._privelemdict = {}
browser_catalog._superclassnames = []
browser_catalog._privpropdict = {}
browser_catalog._privelemdict = {'class_': class_}
class_._superclassnames = []
class_._privpropdict = {'all_subclasses': _Prop_all_subclasses,
 'declaration_end_offset': _Prop_declaration_end_offset,
 'declaration_file': _Prop_declaration_file,
 'declaration_start_offset': _Prop_declaration_start_offset,
 'language': _Prop_language,
 'name': _Prop_name,
 'subclasses': _Prop_subclasses}
class_._privelemdict = {'base_class': base_class,
 'data_member': data_member,
 'member_function': member_function}
Debugger_Display._superclassnames = []
Debugger_Display._privpropdict = {'Default_Array_Size': _Prop_Default_Array_Size,
 'Show_As_Decimal': _Prop_Show_As_Decimal,
 'Show_Locals': _Prop_Show_Locals,
 'Show_Variable_Types': _Prop_Show_Variable_Types,
 'Sort_By_Method': _Prop_Sort_By_Method,
 'Threads_in_Window': _Prop_Threads_in_Window,
 'Use_RTTI': _Prop_Use_RTTI,
 'Variable_Changed_Hilite': _Prop_Variable_Changed_Hilite,
 'Variable_Hints': _Prop_Variable_Hints,
 'Watchpoint_Hilite': _Prop_Watchpoint_Hilite}
Debugger_Display._privelemdict = {}
Debugger_Global._superclassnames = []
Debugger_Global._privpropdict = {'Auto_Target_Libraries': _Prop_Auto_Target_Libraries,
 'Cache_Edited_Files': _Prop_Cache_Edited_Files,
 'Confirm_Kill': _Prop_Confirm_Kill,
 'Dont_Step_in_Runtime': _Prop_Dont_Step_in_Runtime,
 'File_Cache_Duration': _Prop_File_Cache_Duration,
 'Ignore_Mod_Dates': _Prop_Ignore_Mod_Dates,
 'Launch_Apps_on_Open': _Prop_Launch_Apps_on_Open,
 'Open_All_Classes': _Prop_Open_All_Classes,
 'Select_Stack_Crawl': _Prop_Select_Stack_Crawl,
 'Stop_at_Main': _Prop_Stop_at_Main}
Debugger_Global._privelemdict = {}
Debugger_Target._superclassnames = []
Debugger_Target._privpropdict = {'Auto_Target_Libraries': _Prop_Auto_Target_Libraries,
 'Cache_symbolics': _Prop_Cache_symbolics,
 'Data_Update_Interval': _Prop_Data_Update_Interval,
 'Log_System_Messages': _Prop_Log_System_Messages,
 'Relocated_Executable_Path': _Prop_Relocated_Executable_Path,
 'Stop_at_temp_breakpoint': _Prop_Stop_at_temp_breakpoint,
 'Temp_Breakpoint_Type': _Prop_Temp_Breakpoint_Type,
 'Temp_breakpoint_names': _Prop_Temp_breakpoint_names,
 'Update_Data_While_Running': _Prop_Update_Data_While_Running}
Debugger_Target._privelemdict = {}
Debugger_Windowing._superclassnames = []
Debugger_Windowing._privpropdict = {'Debugging_Start_Action': _Prop_Debugging_Start_Action,
 'Do_Nothing_To_Projects': _Prop_Do_Nothing_To_Projects}
Debugger_Windowing._privelemdict = {}
data_member._superclassnames = []
data_member._privpropdict = {'access': _Prop_access,
 'declaration_end_offset': _Prop_declaration_end_offset,
 'declaration_start_offset': _Prop_declaration_start_offset,
 'name': _Prop_name,
 'static': _Prop_static}
data_member._privelemdict = {}
Editor._superclassnames = []
Editor._privpropdict = {'Background_Color': _Prop_Background_Color,
 'Balance': _Prop_Balance,
 'Context_Popup_Delay': _Prop_Context_Popup_Delay,
 'Default_Text_File_Format': _Prop_Default_Text_File_Format,
 'Dynamic_Scroll': _Prop_Dynamic_Scroll,
 'Flash_Delay': _Prop_Flash_Delay,
 'Left_Margin_Line_Select': _Prop_Left_Margin_Line_Select,
 'Main_Text_Color': _Prop_Main_Text_Color,
 'Relaxed_C_Popup_Parsing': _Prop_Relaxed_C_Popup_Parsing,
 'Remember_Font': _Prop_Remember_Font,
 'Remember_Selection': _Prop_Remember_Selection,
 'Remember_Window': _Prop_Remember_Window,
 'Sort_Function_Popup': _Prop_Sort_Function_Popup,
 'Use_Drag__26__Drop_Editing': _Prop_Use_Drag__26__Drop_Editing,
 'Use_Multiple_Undo': _Prop_Use_Multiple_Undo}
Editor._privelemdict = {}
Environment_Variable._superclassnames = []
Environment_Variable._privpropdict = {'name': _Prop_name,
 'value': _Prop_value}
Environment_Variable._privelemdict = {}
Error_Information._superclassnames = []
Error_Information._privpropdict = {'disk_file': _Prop_disk_file,
 'lineNumber': _Prop_lineNumber,
 'message': _Prop_message,
 'messageKind': _Prop_messageKind}
Error_Information._privelemdict = {}
Function_Information._superclassnames = []
Function_Information._privpropdict = {'disk_file': _Prop_disk_file,
 'lineNumber': _Prop_lineNumber}
Function_Information._privelemdict = {}
File_Mappings._superclassnames = []
File_Mappings._privpropdict = {'Mappings': _Prop_Mappings}
File_Mappings._privelemdict = {}
File_Mapping._superclassnames = []
File_Mapping._privpropdict = {'Compiler': _Prop_Compiler,
 'Extension': _Prop_Extension,
 'File_Type': _Prop_File_Type,
 'Ignored_by_Make': _Prop_Ignored_by_Make,
 'Launchable': _Prop_Launchable,
 'Precompiled': _Prop_Precompiled,
 'Resource_File': _Prop_Resource_File}
File_Mapping._privelemdict = {}
Global_Source_Trees._superclassnames = []
Global_Source_Trees._privpropdict = {'Source_Trees': _Prop_Source_Trees}
Global_Source_Trees._privelemdict = {}
Extras._superclassnames = []
Extras._privpropdict = {'Automatic_Toolbar_Help': _Prop_Automatic_Toolbar_Help,
 'External_Reference': _Prop_External_Reference,
 'Full_Screen_Zoom': _Prop_Full_Screen_Zoom,
 'Recent_Editor_Count': _Prop_Recent_Editor_Count,
 'Recent_Project_Count': _Prop_Recent_Project_Count,
 'Use_Editor_Extensions': _Prop_Use_Editor_Extensions,
 'Use_External_Editor': _Prop_Use_External_Editor,
 'Use_Script_Menu': _Prop_Use_Script_Menu,
 'Use_ToolServer_Menu': _Prop_Use_ToolServer_Menu}
Extras._privelemdict = {}
Build_Extras._superclassnames = []
Build_Extras._privpropdict = {'Browser_Active': _Prop_Browser_Active,
 'Cache_Subproject_Data': _Prop_Cache_Subproject_Data,
 'Dump_Browser_Info': _Prop_Dump_Browser_Info,
 'Modification_Date_Caching': _Prop_Modification_Date_Caching}
Build_Extras._privelemdict = {}
member_function._superclassnames = []
member_function._privpropdict = {'access': _Prop_access,
 'declaration_end_offset': _Prop_declaration_end_offset,
 'declaration_file': _Prop_declaration_file,
 'declaration_start_offset': _Prop_declaration_start_offset,
 'implementation_end_offset': _Prop_implementation_end_offset,
 'implementation_file': _Prop_implementation_file,
 'implementation_start_offset': _Prop_implementation_start_offset,
 'name': _Prop_name,
 'static': _Prop_static,
 'virtual': _Prop_virtual}
member_function._privelemdict = {}
Access_Paths._superclassnames = []
Access_Paths._privpropdict = {'Always_Full_Search': _Prop_Always_Full_Search,
 'Convert_Paths': _Prop_Convert_Paths,
 'Require_Framework_Includes': _Prop_Require_Framework_Includes,
 'System_Paths': _Prop_System_Paths,
 'User_Paths': _Prop_User_Paths}
Access_Paths._privelemdict = {}
Path_Information._superclassnames = []
Path_Information._privpropdict = {'format': _Prop_format,
 'framework': _Prop_framework,
 'host_flags': _Prop_host_flags,
 'name': _Prop_name,
 'origin': _Prop_origin,
 'recursive': _Prop_recursive,
 'root': _Prop_root}
Path_Information._privelemdict = {}
Plugin_Settings._superclassnames = []
Plugin_Settings._privpropdict = {'Disable_Third_Party_COM_Plugins': _Prop_Disable_Third_Party_COM_Plugins,
 'Plugin_Diagnostics_Level': _Prop_Plugin_Diagnostics_Level}
Plugin_Settings._privelemdict = {}
Runtime_Settings._superclassnames = []
Runtime_Settings._privpropdict = {'Command_Line_Arguments': _Prop_Command_Line_Arguments,
 'Environment_Variables': _Prop_Environment_Variables,
 'Host_Application': _Prop_Host_Application,
 'Working_Directory': _Prop_Working_Directory}
Runtime_Settings._privelemdict = {}
Relative_Path._superclassnames = []
Relative_Path._privpropdict = {'format': _Prop_format,
 'name': _Prop_name,
 'origin': _Prop_origin,
 'root': _Prop_root}
Relative_Path._privelemdict = {}
Shielded_Folder._superclassnames = []
Shielded_Folder._privpropdict = {'Expression_To_Match': _Prop_Expression_To_Match,
 'Skip_Find_And_Compare_Operations': _Prop_Skip_Find_And_Compare_Operations,
 'Skip_Project_Operations': _Prop_Skip_Project_Operations}
Shielded_Folder._privelemdict = {}
Shielded_Folders._superclassnames = []
Shielded_Folders._privpropdict = {'Shielded_Items': _Prop_Shielded_Items}
Shielded_Folders._privelemdict = {}
Syntax_Coloring._superclassnames = []
Syntax_Coloring._privpropdict = {'Comment_Color': _Prop_Comment_Color,
 'Custom_Color_1': _Prop_Custom_Color_1,
 'Custom_Color_2': _Prop_Custom_Color_2,
 'Custom_Color_3': _Prop_Custom_Color_3,
 'Custom_Color_4': _Prop_Custom_Color_4,
 'Keyword_Color': _Prop_Keyword_Color,
 'String_Color': _Prop_String_Color,
 'Syntax_Coloring': _Prop_Syntax_Coloring}
Syntax_Coloring._privelemdict = {}
Segment._superclassnames = []
Segment._privpropdict = {'filecount': _Prop_filecount,
 'name': _Prop_name,
 'seg_2d_locked': _Prop_seg_2d_locked,
 'seg_2d_preloaded': _Prop_seg_2d_preloaded,
 'seg_2d_protected': _Prop_seg_2d_protected,
 'seg_2d_purgeable': _Prop_seg_2d_purgeable,
 'seg_2d_system_heap': _Prop_seg_2d_system_heap}
Segment._privelemdict = {}
ProjectFile._superclassnames = []
ProjectFile._privpropdict = {'codesize': _Prop_codesize,
 'datasize': _Prop_datasize,
 'disk_file': _Prop_disk_file,
 'filetype': _Prop_filetype,
 'includes': _Prop_includes,
 'initialize_before': _Prop_initialize_before,
 'name': _Prop_name,
 'symbols': _Prop_symbols,
 'up_to_date': _Prop_up_to_date,
 'weak_link': _Prop_weak_link}
ProjectFile._privelemdict = {}
Source_Tree._superclassnames = []
Source_Tree._privpropdict = {'format': _Prop_format,
 'name': _Prop_name,
 'path': _Prop_path,
 'path_kind': _Prop_path_kind}
Source_Tree._privelemdict = {}
Target_Settings._superclassnames = []
Target_Settings._privpropdict = {'Linker': _Prop_Linker,
 'Output_Directory_Location': _Prop_Output_Directory_Location,
 'Output_Directory_Origin': _Prop_Output_Directory_Origin,
 'Output_Directory_Path': _Prop_Output_Directory_Path,
 'Post_Linker': _Prop_Post_Linker,
 'Pre_Linker': _Prop_Pre_Linker,
 'Target_Name': _Prop_Target_Name,
 'Use_Relative_Paths': _Prop_Use_Relative_Paths}
Target_Settings._privelemdict = {}
Target_Source_Trees._superclassnames = []
Target_Source_Trees._privpropdict = {'Source_Trees': _Prop_Source_Trees}
Target_Source_Trees._privelemdict = {}
VCS_Setup._superclassnames = []
VCS_Setup._privpropdict = {'Always_Prompt': _Prop_Always_Prompt,
 'Auto_Connect': _Prop_Auto_Connect,
 'Connection_Method': _Prop_Connection_Method,
 'Database_Path': _Prop_Database_Path,
 'Local_Path': _Prop_Local_Path,
 'Mount_Volume': _Prop_Mount_Volume,
 'Password': _Prop_Password,
 'Store_Password': _Prop_Store_Password,
 'Use_Global_Settings': _Prop_Use_Global_Settings,
 'Username': _Prop_Username,
 'VCS_Active': _Prop_VCS_Active}
VCS_Setup._privelemdict = {}
Font._superclassnames = []
Font._privpropdict = {'Auto_Indent': _Prop_Auto_Indent,
 'Tab_Indents_Selection': _Prop_Tab_Indents_Selection,
 'Tab_Inserts_Spaces': _Prop_Tab_Inserts_Spaces,
 'Tab_Size': _Prop_Tab_Size,
 'Text_Font': _Prop_Text_Font,
 'Text_Size': _Prop_Text_Size}
Font._privelemdict = {}
_Enum_Acce = {'public': 'Publ',
 'protected': 'Prot',
 'private': 'Priv'}
_Enum_BXbr = {'Always_Build': 'BXb1',
 'Ask_Build': 'BXb2',
 'Never_Build': 'BXb3'}
_Enum_DbSA = {'No_Action': 'DSA1',
 'Hide_Windows': 'DSA2',
 'Collapse_Windows': 'DSA3',
 'Close_Windows': 'DSA4'}
_Enum_DgBL = {'Always': 'DgB0',
 'Never': 'DgB1',
 'Ask': 'DgB2'}
_Enum_ErrT = {'information': 'ErIn',
 'compiler_warning': 'ErCW',
 'compiler_error': 'ErCE',
 'definition': 'ErDf',
 'linker_warning': 'ErLW',
 'linker_error': 'ErLE',
 'find_result': 'ErFn',
 'generic_error': 'ErGn'}
_Enum_Inte = {'never_interact': 'eNvr',
 'interact_with_self': 'eInS',
 'interact_with_local': 'eInL',
 'interact_with_all': 'eInA'}
_Enum_Lang = {'C': 'LC  ',
 'C_2b__2b_': 'LC++',
 'Pascal': 'LP  ',
 'Object_Pascal': 'LP++',
 'Java': 'LJav',
 'Assembler': 'LAsm',
 'Unknown': 'L?  '}
_Enum_PPrm = {'absolute': 'Abso',
 'project_relative': 'PRel',
 'shell_relative': 'SRel',
 'system_relative': 'YRel',
 'root_relative': 'RRel'}
_Enum_PXdg = {'Diagnose_None': 'PXd1',
 'Diagnose_Errors': 'PXd2',
 'Diagnose_All': 'PXd3'}
_Enum_PthF = {'Generic_Path': 'PFGn',
 'MacOS_Path': 'PFMc',
 'Windows_Path': 'PFWn',
 'Unix_Path': 'PFUx'}
_Enum_RefP = {'Think_Reference': 'DanR',
 'QuickView': 'ALTV'}
_Enum_STKd = {'Absolute_Path': 'STK0',
 'Registry_Key': 'STK1',
 'Environment_Variable': 'STK2'}
_Enum_SrcT = {'source': 'FTxt',
 'unknown': 'FUnk'}
_Enum_TmpB = {'User_Specified': 'Usrs',
 'Default': 'Dflt'}
_Enum_TxtF = {'MacOS': 'TxF0',
 'DOS': 'TxF1',
 'Unix': 'TxF2'}
_Enum_savo = {'yes': 'yes ',
 'no': 'no  ',
 'ask': 'ask '}
_classdeclarations = {'BRKW': Browser_Coloring,
 'BSTG': Build_Settings,
 'BsCl': base_class,
 'CUKW': Custom_Keywords,
 'Cata': browser_catalog,
 'Clas': class_,
 'DbDS': Debugger_Display,
 'DbGL': Debugger_Global,
 'DbTG': Debugger_Target,
 'DbWN': Debugger_Windowing,
 'DtMb': data_member,
 'EDTR': Editor,
 'EnvV': Environment_Variable,
 'ErrM': Error_Information,
 'FDef': Function_Information,
 'FLMP': File_Mappings,
 'FMap': File_Mapping,
 'GSTs': Global_Source_Trees,
 'GXTR': Extras,
 'LXTR': Build_Extras,
 'MbFn': member_function,
 'PATH': Access_Paths,
 'PInf': Path_Information,
 'PSTG': Plugin_Settings,
 'RSTG': Runtime_Settings,
 'RlPt': Relative_Path,
 'SFit': Shielded_Folder,
 'SHFL': Shielded_Folders,
 'SNTX': Syntax_Coloring,
 'Seg ': Segment,
 'SrcF': ProjectFile,
 'SrcT': Source_Tree,
 'TARG': Target_Settings,
 'TSTs': Target_Source_Trees,
 'VCSs': VCS_Setup,
 'mFNT': Font}
_propdeclarations = {'Acce': _Prop_access,
 'BW00': _Prop_Browser_Keywords,
 'BW01': _Prop_Classes_Color,
 'BW02': _Prop_Constants_Color,
 'BW03': _Prop_Enums_Color,
 'BW04': _Prop_Functions_Color,
 'BW05': _Prop_Globals_Color,
 'BW06': _Prop_Macros_Color,
 'BW07': _Prop_Templates_Color,
 'BW08': _Prop_Typedefs_Color,
 'BW10': _Prop_Template_Commands_in_Menu,
 'BX01': _Prop_Completion_Sound,
 'BX02': _Prop_Success_Sound,
 'BX03': _Prop_Failure_Sound,
 'BX04': _Prop_Build_Before_Running,
 'BX05': _Prop_Include_Cache_Size,
 'BX06': _Prop_Compiler_Thread_Stack_Size,
 'BX07': _Prop_Save_Before_Building,
 'Bfor': _Prop_initialize_before,
 'CSiz': _Prop_codesize,
 'Clas': _Prop_class_,
 'DSiz': _Prop_datasize,
 'Db01': _Prop_Show_Variable_Types,
 'Db02': _Prop_Sort_By_Method,
 'Db03': _Prop_Use_RTTI,
 'Db04': _Prop_Threads_in_Window,
 'Db05': _Prop_Variable_Hints,
 'Db06': _Prop_Watchpoint_Hilite,
 'Db07': _Prop_Variable_Changed_Hilite,
 'Db08': _Prop_Default_Array_Size,
 'Db09': _Prop_Show_Locals,
 'Db10': _Prop_Show_As_Decimal,
 'DcEn': _Prop_declaration_end_offset,
 'DcFl': _Prop_declaration_file,
 'DcSt': _Prop_declaration_start_offset,
 'DfEn': _Prop_implementation_end_offset,
 'DfFl': _Prop_implementation_file,
 'DfSt': _Prop_implementation_start_offset,
 'Dg01': _Prop_Ignore_Mod_Dates,
 'Dg02': _Prop_Open_All_Classes,
 'Dg03': _Prop_Launch_Apps_on_Open,
 'Dg04': _Prop_Confirm_Kill,
 'Dg05': _Prop_Stop_at_Main,
 'Dg06': _Prop_Select_Stack_Crawl,
 'Dg07': _Prop_Dont_Step_in_Runtime,
 'Dg11': _Prop_Auto_Target_Libraries,
 'Dg12': _Prop_Cache_Edited_Files,
 'Dg13': _Prop_File_Cache_Duration,
 'Dt02': _Prop_Log_System_Messages,
 'Dt08': _Prop_Update_Data_While_Running,
 'Dt09': _Prop_Data_Update_Interval,
 'Dt10': _Prop_Relocated_Executable_Path,
 'Dt13': _Prop_Stop_at_temp_breakpoint,
 'Dt14': _Prop_Temp_breakpoint_names,
 'Dt15': _Prop_Cache_symbolics,
 'Dt16': _Prop_Temp_Breakpoint_Type,
 'Dw01': _Prop_Debugging_Start_Action,
 'Dw02': _Prop_Do_Nothing_To_Projects,
 'ED01': _Prop_Flash_Delay,
 'ED02': _Prop_Dynamic_Scroll,
 'ED03': _Prop_Balance,
 'ED04': _Prop_Use_Drag__26__Drop_Editing,
 'ED06': _Prop_Sort_Function_Popup,
 'ED07': _Prop_Use_Multiple_Undo,
 'ED08': _Prop_Remember_Font,
 'ED09': _Prop_Remember_Selection,
 'ED10': _Prop_Remember_Window,
 'ED12': _Prop_Main_Text_Color,
 'ED13': _Prop_Background_Color,
 'ED14': _Prop_Context_Popup_Delay,
 'ED15': _Prop_Relaxed_C_Popup_Parsing,
 'ED16': _Prop_Left_Margin_Line_Select,
 'ED17': _Prop_Default_Text_File_Format,
 'EX04': _Prop_Modification_Date_Caching,
 'EX07': _Prop_Full_Screen_Zoom,
 'EX08': _Prop_External_Reference,
 'EX09': _Prop_Browser_Active,
 'EX10': _Prop_Use_Editor_Extensions,
 'EX11': _Prop_Use_External_Editor,
 'EX12': _Prop_Use_Script_Menu,
 'EX16': _Prop_Recent_Editor_Count,
 'EX17': _Prop_Recent_Project_Count,
 'EX18': _Prop_Use_ToolServer_Menu,
 'EX19': _Prop_Automatic_Toolbar_Help,
 'EX30': _Prop_Dump_Browser_Info,
 'EX31': _Prop_Cache_Subproject_Data,
 'ErrL': _Prop_lineNumber,
 'ErrS': _Prop_message,
 'ErrT': _Prop_messageKind,
 'FMps': _Prop_Mappings,
 'FN01': _Prop_Auto_Indent,
 'FN02': _Prop_Tab_Size,
 'FN03': _Prop_Tab_Indents_Selection,
 'FN04': _Prop_Tab_Inserts_Spaces,
 'Frmt': _Prop_format,
 'Frmw': _Prop_framework,
 'GH01': _Prop_Syntax_Coloring,
 'GH02': _Prop_Comment_Color,
 'GH03': _Prop_Keyword_Color,
 'GH04': _Prop_String_Color,
 'GH05': _Prop_Custom_Color_1,
 'GH06': _Prop_Custom_Color_2,
 'GH07': _Prop_Custom_Color_3,
 'GH08': _Prop_Custom_Color_4,
 'HstF': _Prop_host_flags,
 'IncF': _Prop_includes,
 'Kind': _Prop_path_kind,
 'Lang': _Prop_language,
 'NumF': _Prop_filecount,
 'Orig': _Prop_origin,
 'PA01': _Prop_User_Paths,
 'PA02': _Prop_Always_Full_Search,
 'PA03': _Prop_System_Paths,
 'PA04': _Prop_Convert_Paths,
 'PA05': _Prop_Require_Framework_Includes,
 'PLck': _Prop_seg_2d_locked,
 'PR04': _Prop_File_Type,
 'PX01': _Prop_Plugin_Diagnostics_Level,
 'PX02': _Prop_Disable_Third_Party_COM_Plugins,
 'Path': _Prop_path,
 'Prel': _Prop_seg_2d_preloaded,
 'Prot': _Prop_seg_2d_protected,
 'Purg': _Prop_seg_2d_purgeable,
 'RS01': _Prop_Host_Application,
 'RS02': _Prop_Command_Line_Arguments,
 'RS03': _Prop_Working_Directory,
 'RS04': _Prop_Environment_Variables,
 'Recu': _Prop_recursive,
 'Root': _Prop_root,
 'SF01': _Prop_Expression_To_Match,
 'SF02': _Prop_Skip_Project_Operations,
 'SF03': _Prop_Skip_Find_And_Compare_Operations,
 'SFis': _Prop_Shielded_Items,
 'ST01': _Prop_Source_Trees,
 'SrcT': _Prop_filetype,
 'Stat': _Prop_static,
 'SubA': _Prop_all_subclasses,
 'SubC': _Prop_subclasses,
 'SymG': _Prop_symbols,
 'SysH': _Prop_seg_2d_system_heap,
 'TA01': _Prop_Linker,
 'TA02': _Prop_Extension,
 'TA03': _Prop_Precompiled,
 'TA04': _Prop_Resource_File,
 'TA05': _Prop_Launchable,
 'TA06': _Prop_Ignored_by_Make,
 'TA07': _Prop_Compiler,
 'TA09': _Prop_Post_Linker,
 'TA10': _Prop_Target_Name,
 'TA11': _Prop_Output_Directory_Path,
 'TA12': _Prop_Output_Directory_Origin,
 'TA13': _Prop_Pre_Linker,
 'TA15': _Prop_Use_Relative_Paths,
 'TA16': _Prop_Output_Directory_Location,
 'UpTD': _Prop_up_to_date,
 'VC01': _Prop_VCS_Active,
 'VC02': _Prop_Connection_Method,
 'VC03': _Prop_Username,
 'VC04': _Prop_Password,
 'VC05': _Prop_Auto_Connect,
 'VC06': _Prop_Store_Password,
 'VC07': _Prop_Always_Prompt,
 'VC08': _Prop_Mount_Volume,
 'VC09': _Prop_Database_Path,
 'VC10': _Prop_Local_Path,
 'VC11': _Prop_Use_Global_Settings,
 'Valu': _Prop_value,
 'Virt': _Prop_virtual,
 'Weak': _Prop_weak_link,
 'file': _Prop_disk_file,
 'pnam': _Prop_name,
 'ptps': _Prop_Text_Size,
 'ptxf': _Prop_Text_Font}
_compdeclarations = {}
_enumdeclarations = {'Acce': _Enum_Acce,
 'BXbr': _Enum_BXbr,
 'DbSA': _Enum_DbSA,
 'DgBL': _Enum_DgBL,
 'ErrT': _Enum_ErrT,
 'Inte': _Enum_Inte,
 'Lang': _Enum_Lang,
 'PPrm': _Enum_PPrm,
 'PXdg': _Enum_PXdg,
 'PthF': _Enum_PthF,
 'RefP': _Enum_RefP,
 'STKd': _Enum_STKd,
 'SrcT': _Enum_SrcT,
 'TmpB': _Enum_TmpB,
 'TxtF': _Enum_TxtF,
 'savo': _Enum_savo}
