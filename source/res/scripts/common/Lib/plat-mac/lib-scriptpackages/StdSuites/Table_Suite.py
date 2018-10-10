# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/StdSuites/Table_Suite.py
import aetools
import MacOS
_code = 'tbls'

class Table_Suite_Events:
    pass


class cell(aetools.ComponentItem):
    want = 'ccel'


class _Prop_formula(aetools.NProperty):
    which = 'pfor'
    want = 'ctxt'


class _Prop_protection(aetools.NProperty):
    which = 'ppro'
    want = 'prtn'


cells = cell

class column(aetools.ComponentItem):
    want = 'ccol'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'itxt'


columns = column

class rows(aetools.ComponentItem):
    want = 'crow'


row = rows

class tables(aetools.ComponentItem):
    want = 'ctbl'


table = tables
cell._superclassnames = []
cell._privpropdict = {'formula': _Prop_formula,
 'protection': _Prop_protection}
cell._privelemdict = {}
column._superclassnames = []
column._privpropdict = {'name': _Prop_name}
column._privelemdict = {}
rows._superclassnames = []
rows._privpropdict = {}
rows._privelemdict = {}
tables._superclassnames = []
tables._privpropdict = {}
tables._privelemdict = {}
_Enum_prtn = {'read_only': 'nmod',
 'formulas_protected': 'fpro',
 'read_2f_write': 'modf'}
_classdeclarations = {'ccel': cell,
 'ccol': column,
 'crow': rows,
 'ctbl': tables}
_propdeclarations = {'pfor': _Prop_formula,
 'pnam': _Prop_name,
 'ppro': _Prop_protection}
_compdeclarations = {}
_enumdeclarations = {'prtn': _Enum_prtn}
