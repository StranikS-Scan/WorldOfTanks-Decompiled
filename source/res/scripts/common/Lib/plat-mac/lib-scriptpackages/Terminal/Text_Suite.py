# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Terminal/Text_Suite.py
import aetools
import MacOS
_code = '????'

class Text_Suite_Events:
    pass


class attachment(aetools.ComponentItem):
    want = 'atts'


class _Prop__3c_Inheritance_3e_(aetools.NProperty):
    which = 'c@#^'
    want = 'ctxt'


class _Prop_file_name(aetools.NProperty):
    which = 'atfn'
    want = 'utxt'


class attribute_run(aetools.ComponentItem):
    want = 'catr'


class _Prop_color(aetools.NProperty):
    which = 'colr'
    want = 'colr'


class _Prop_font(aetools.NProperty):
    which = 'font'
    want = 'utxt'


class _Prop_size(aetools.NProperty):
    which = 'ptsz'
    want = 'long'


attribute_runs = attribute_run

class character(aetools.ComponentItem):
    want = 'cha '


characters = character

class paragraph(aetools.ComponentItem):
    want = 'cpar'


paragraphs = paragraph

class text(aetools.ComponentItem):
    want = 'ctxt'


class word(aetools.ComponentItem):
    want = 'cwor'


words = word
attachment._superclassnames = ['text']
attachment._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'file_name': _Prop_file_name}
attachment._privelemdict = {'attribute_run': attribute_run,
 'character': character,
 'paragraph': paragraph,
 'word': word}
import Standard_Suite
attribute_run._superclassnames = ['item']
attribute_run._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'color': _Prop_color,
 'font': _Prop_font,
 'size': _Prop_size}
attribute_run._privelemdict = {'attribute_run': attribute_run,
 'character': character,
 'paragraph': paragraph,
 'word': word}
character._superclassnames = ['item']
character._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'color': _Prop_color,
 'font': _Prop_font,
 'size': _Prop_size}
character._privelemdict = {'attribute_run': attribute_run,
 'character': character,
 'paragraph': paragraph,
 'word': word}
paragraph._superclassnames = ['item']
paragraph._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'color': _Prop_color,
 'font': _Prop_font,
 'size': _Prop_size}
paragraph._privelemdict = {'attribute_run': attribute_run,
 'character': character,
 'paragraph': paragraph,
 'word': word}
text._superclassnames = ['item']
text._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'color': _Prop_color,
 'font': _Prop_font,
 'size': _Prop_size}
text._privelemdict = {'attribute_run': attribute_run,
 'character': character,
 'paragraph': paragraph,
 'word': word}
word._superclassnames = ['item']
word._privpropdict = {'_3c_Inheritance_3e_': _Prop__3c_Inheritance_3e_,
 'color': _Prop_color,
 'font': _Prop_font,
 'size': _Prop_size}
word._privelemdict = {'attribute_run': attribute_run,
 'character': character,
 'paragraph': paragraph,
 'word': word}
_classdeclarations = {'atts': attachment,
 'catr': attribute_run,
 'cha ': character,
 'cpar': paragraph,
 'ctxt': text,
 'cwor': word}
_propdeclarations = {'atfn': _Prop_file_name,
 'c@#^': _Prop__3c_Inheritance_3e_,
 'colr': _Prop_color,
 'font': _Prop_font,
 'ptsz': _Prop_size}
_compdeclarations = {}
_enumdeclarations = {}
