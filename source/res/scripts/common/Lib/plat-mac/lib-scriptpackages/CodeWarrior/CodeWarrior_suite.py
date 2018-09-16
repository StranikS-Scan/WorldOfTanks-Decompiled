# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/CodeWarrior/CodeWarrior_suite.py
import aetools
import MacOS
_code = 'CWIE'

class CodeWarrior_suite_Events:
    _argmap_add = {'new': 'kocl',
     'with_data': 'data',
     'to_targets': 'TTGT',
     'to_group': 'TGRP'}

    def add(self, _object, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'ADDF'
        aetools.keysubst(_arguments, self._argmap_add)
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def build(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'MAKE'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def check(self, _object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'CHEK'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def compile_file(self, _object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'COMP'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def disassemble_file(self, _object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'DASM'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    _argmap_export = {'in_': 'kfil'}

    def export(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'EXPT'
        aetools.keysubst(_arguments, self._argmap_export)
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def remove_object_code(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'RMOB'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def remove_target_files(self, _object, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'RMFL'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def run_target(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'RUN '
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def touch_file(self, _object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'TOCH'
        if _arguments:
            raise TypeError, 'No optional args expected'
        _arguments['----'] = _object
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None

    def update(self, _no_object=None, _attributes={}, **_arguments):
        _code = 'CWIE'
        _subcode = 'UP2D'
        if _arguments:
            raise TypeError, 'No optional args expected'
        if _no_object is not None:
            raise TypeError, 'No direct arg expected'
        _reply, _arguments, _attributes = self.send(_code, _subcode, _arguments, _attributes)
        if _arguments.get('errn', 0):
            raise aetools.Error, aetools.decodeerror(_arguments)
        return _arguments['----'] if _arguments.has_key('----') else None


class single_class_browser(aetools.ComponentItem):
    want = '1BRW'


class _Prop_inherits(aetools.NProperty):
    which = 'c@#^'
    want = 'TXTD'


single_class_browsers = single_class_browser

class single_class_hierarchy(aetools.ComponentItem):
    want = '1HIR'


single_class_hierarchies = single_class_hierarchy

class class_browser(aetools.ComponentItem):
    want = 'BROW'


class_browsers = class_browser

class file_compare_document(aetools.ComponentItem):
    want = 'COMP'


file_compare_documents = file_compare_document

class catalog_document(aetools.ComponentItem):
    want = 'CTLG'


catalog_documents = catalog_document

class editor_document(aetools.ComponentItem):
    want = 'EDIT'


editor_documents = editor_document

class class_hierarchy(aetools.ComponentItem):
    want = 'HIER'


class_hierarchies = class_hierarchy

class project_inspector(aetools.ComponentItem):
    want = 'INSP'


project_inspectors = project_inspector

class message_document(aetools.ComponentItem):
    want = 'MSSG'


message_documents = message_document

class build_progress_document(aetools.ComponentItem):
    want = 'PRGS'


build_progress_documents = build_progress_document

class project_document(aetools.ComponentItem):
    want = 'PRJD'


class _Prop_current_target(aetools.NProperty):
    which = 'CURT'
    want = 'TRGT'


project_documents = project_document

class subtarget(aetools.ComponentItem):
    want = 'SBTG'


class _Prop_link_against_output(aetools.NProperty):
    which = 'LNKO'
    want = 'bool'


class _Prop_target(aetools.NProperty):
    which = 'TrgT'
    want = 'TRGT'


subtargets = subtarget

class target_file(aetools.ComponentItem):
    want = 'SRCF'


class _Prop_code_size(aetools.NProperty):
    which = 'CSZE'
    want = 'long'


class _Prop_compiled_date(aetools.NProperty):
    which = 'CMPD'
    want = 'ldt '


class _Prop_data_size(aetools.NProperty):
    which = 'DSZE'
    want = 'long'


class _Prop_debug(aetools.NProperty):
    which = 'DBUG'
    want = 'bool'


class _Prop_dependents(aetools.NProperty):
    which = 'DPND'
    want = 'list'


class _Prop_id(aetools.NProperty):
    which = 'ID  '
    want = 'long'


class _Prop_init_before(aetools.NProperty):
    which = 'INIT'
    want = 'bool'


class _Prop_link_index(aetools.NProperty):
    which = 'LIDX'
    want = 'long'


class _Prop_linked(aetools.NProperty):
    which = 'LINK'
    want = 'bool'


class _Prop_location(aetools.NProperty):
    which = 'FILE'
    want = 'fss '


class _Prop_merge_output(aetools.NProperty):
    which = 'MRGE'
    want = 'bool'


class _Prop_modified_date(aetools.NProperty):
    which = 'MODD'
    want = 'ldt '


class _Prop_path(aetools.NProperty):
    which = 'Path'
    want = 'itxt'


class _Prop_prerequisites(aetools.NProperty):
    which = 'PRER'
    want = 'list'


class _Prop_type(aetools.NProperty):
    which = 'FTYP'
    want = 'FTYP'


class _Prop_weak_link(aetools.NProperty):
    which = 'WEAK'
    want = 'bool'


target_files = target_file

class symbol_browser(aetools.ComponentItem):
    want = 'SYMB'


symbol_browsers = symbol_browser

class ToolServer_worksheet(aetools.ComponentItem):
    want = 'TOOL'


ToolServer_worksheets = ToolServer_worksheet

class target(aetools.ComponentItem):
    want = 'TRGT'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'itxt'


class _Prop_project_document(aetools.NProperty):
    which = 'PrjD'
    want = 'PRJD'


targets = target

class text_document(aetools.ComponentItem):
    want = 'TXTD'


class _Prop_modified(aetools.NProperty):
    which = 'imod'
    want = 'bool'


class _Prop_selection(aetools.NProperty):
    which = 'sele'
    want = 'csel'


text_documents = text_document
single_class_browser._superclassnames = ['text_document']
single_class_browser._privpropdict = {'inherits': _Prop_inherits}
single_class_browser._privelemdict = {}
import Standard_Suite
single_class_hierarchy._superclassnames = ['document']
single_class_hierarchy._privpropdict = {'inherits': _Prop_inherits}
single_class_hierarchy._privelemdict = {}
class_browser._superclassnames = ['text_document']
class_browser._privpropdict = {'inherits': _Prop_inherits}
class_browser._privelemdict = {}
file_compare_document._superclassnames = ['text_document']
file_compare_document._privpropdict = {'inherits': _Prop_inherits}
file_compare_document._privelemdict = {}
catalog_document._superclassnames = ['text_document']
catalog_document._privpropdict = {'inherits': _Prop_inherits}
catalog_document._privelemdict = {}
editor_document._superclassnames = ['text_document']
editor_document._privpropdict = {'inherits': _Prop_inherits}
editor_document._privelemdict = {}
class_hierarchy._superclassnames = ['document']
class_hierarchy._privpropdict = {'inherits': _Prop_inherits}
class_hierarchy._privelemdict = {}
project_inspector._superclassnames = ['document']
project_inspector._privpropdict = {'inherits': _Prop_inherits}
project_inspector._privelemdict = {}
message_document._superclassnames = ['text_document']
message_document._privpropdict = {'inherits': _Prop_inherits}
message_document._privelemdict = {}
build_progress_document._superclassnames = ['document']
build_progress_document._privpropdict = {'inherits': _Prop_inherits}
build_progress_document._privelemdict = {}
project_document._superclassnames = ['document']
project_document._privpropdict = {'current_target': _Prop_current_target,
 'inherits': _Prop_inherits}
project_document._privelemdict = {'target': target}
subtarget._superclassnames = ['target']
subtarget._privpropdict = {'inherits': _Prop_inherits,
 'link_against_output': _Prop_link_against_output,
 'target': _Prop_target}
subtarget._privelemdict = {}
target_file._superclassnames = []
target_file._privpropdict = {'code_size': _Prop_code_size,
 'compiled_date': _Prop_compiled_date,
 'data_size': _Prop_data_size,
 'debug': _Prop_debug,
 'dependents': _Prop_dependents,
 'id': _Prop_id,
 'init_before': _Prop_init_before,
 'link_index': _Prop_link_index,
 'linked': _Prop_linked,
 'location': _Prop_location,
 'merge_output': _Prop_merge_output,
 'modified_date': _Prop_modified_date,
 'path': _Prop_path,
 'prerequisites': _Prop_prerequisites,
 'type': _Prop_type,
 'weak_link': _Prop_weak_link}
target_file._privelemdict = {}
symbol_browser._superclassnames = ['text_document']
symbol_browser._privpropdict = {'inherits': _Prop_inherits}
symbol_browser._privelemdict = {}
ToolServer_worksheet._superclassnames = ['text_document']
ToolServer_worksheet._privpropdict = {'inherits': _Prop_inherits}
ToolServer_worksheet._privelemdict = {}
target._superclassnames = []
target._privpropdict = {'name': _Prop_name,
 'project_document': _Prop_project_document}
target._privelemdict = {'subtarget': subtarget,
 'target_file': target_file}
text_document._superclassnames = ['document']
text_document._privpropdict = {'inherits': _Prop_inherits,
 'modified': _Prop_modified,
 'selection': _Prop_selection}
text_document._privelemdict = {'character': Standard_Suite.character,
 'insertion_point': Standard_Suite.insertion_point,
 'line': Standard_Suite.line,
 'text': Standard_Suite.text}
_Enum_DKND = {'project': 'PRJD',
 'editor_document': 'EDIT',
 'message': 'MSSG',
 'file_compare': 'COMP',
 'catalog_document': 'CTLG',
 'class_browser': 'BROW',
 'single_class_browser': '1BRW',
 'symbol_browser': 'SYMB',
 'class_hierarchy': 'HIER',
 'single_class_hierarchy': '1HIR',
 'project_inspector': 'INSP',
 'ToolServer_worksheet': 'TOOL',
 'build_progress_document': 'PRGS'}
_Enum_FTYP = {'library_file': 'LIBF',
 'project_file': 'PRJF',
 'resource_file': 'RESF',
 'text_file': 'TXTF',
 'unknown_file': 'UNKN'}
_Enum_Inte = {'never_interact': 'eNvr',
 'interact_with_self': 'eInS',
 'interact_with_local': 'eInL',
 'interact_with_all': 'eInA'}
_Enum_PERM = {'read_write': 'RdWr',
 'read_only': 'Read',
 'checked_out_read_write': 'CkRW',
 'checked_out_read_only': 'CkRO',
 'checked_out_read_modify': 'CkRM',
 'locked': 'Lock',
 'none': 'LNNO'}
_classdeclarations = {'1BRW': single_class_browser,
 '1HIR': single_class_hierarchy,
 'BROW': class_browser,
 'COMP': file_compare_document,
 'CTLG': catalog_document,
 'EDIT': editor_document,
 'HIER': class_hierarchy,
 'INSP': project_inspector,
 'MSSG': message_document,
 'PRGS': build_progress_document,
 'PRJD': project_document,
 'SBTG': subtarget,
 'SRCF': target_file,
 'SYMB': symbol_browser,
 'TOOL': ToolServer_worksheet,
 'TRGT': target,
 'TXTD': text_document}
_propdeclarations = {'CMPD': _Prop_compiled_date,
 'CSZE': _Prop_code_size,
 'CURT': _Prop_current_target,
 'DBUG': _Prop_debug,
 'DPND': _Prop_dependents,
 'DSZE': _Prop_data_size,
 'FILE': _Prop_location,
 'FTYP': _Prop_type,
 'ID  ': _Prop_id,
 'INIT': _Prop_init_before,
 'LIDX': _Prop_link_index,
 'LINK': _Prop_linked,
 'LNKO': _Prop_link_against_output,
 'MODD': _Prop_modified_date,
 'MRGE': _Prop_merge_output,
 'PRER': _Prop_prerequisites,
 'Path': _Prop_path,
 'PrjD': _Prop_project_document,
 'TrgT': _Prop_target,
 'WEAK': _Prop_weak_link,
 'c@#^': _Prop_inherits,
 'imod': _Prop_modified,
 'pnam': _Prop_name,
 'sele': _Prop_selection}
_compdeclarations = {}
_enumdeclarations = {'DKND': _Enum_DKND,
 'FTYP': _Enum_FTYP,
 'Inte': _Enum_Inte,
 'PERM': _Enum_PERM}
