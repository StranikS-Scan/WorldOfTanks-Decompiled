# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/SystemEvents/Login_Items_Suite.py
import aetools
import MacOS
_code = 'logi'

class Login_Items_Suite_Events:
    pass


class login_item(aetools.ComponentItem):
    want = 'logi'


class _Prop__3c_Inheritance_3e_(aetools.NProperty):
    which = 'c@#^'
    want = 'cobj'


class _Prop_hidden(aetools.NProperty):
    which = 'hidn'
    want = 'bool'


class _Prop_kind(aetools.NProperty):
    which = 'kind'
    want = 'utxt'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'utxt'


class _Prop_path(aetools.NProperty):
    which = 'ppth'
    want = 'utxt'


login_items = login_item
import Standard_Suite
login_item._superclassnames = ['item']
login_item._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'hidden': _Prop_hidden,
 'kind': _Prop_kind,
 'name': _Prop_name,
 'path': _Prop_path}
login_item._privelemdict = {}
_classdeclarations = {'logi': login_item}
_propdeclarations = {'c@#^': _Prop__3c_Inheritance_3e_,
 'hidn': _Prop_hidden,
 'kind': _Prop_kind,
 'pnam': _Prop_name,
 'ppth': _Prop_path}
_compdeclarations = {}
_enumdeclarations = {}
