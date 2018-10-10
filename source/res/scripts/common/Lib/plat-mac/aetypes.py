# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/aetypes.py
from warnings import warnpy3k
warnpy3k('In 3.x, the aetypes module is removed.', stacklevel=2)
from Carbon.AppleEvents import *
import struct
from types import *
import string

def pack(*args, **kwargs):
    from aepack import pack
    return pack(*args, **kwargs)


def nice(s):
    if type(s) is StringType:
        return repr(s)
    else:
        return str(s)


class Unknown:

    def __init__(self, type, data):
        self.type = type
        self.data = data

    def __repr__(self):
        return 'Unknown(%r, %r)' % (self.type, self.data)

    def __aepack__(self):
        return pack(self.data, self.type)


class Enum:

    def __init__(self, enum):
        self.enum = '%-4.4s' % str(enum)

    def __repr__(self):
        return 'Enum(%r)' % (self.enum,)

    def __str__(self):
        return string.strip(self.enum)

    def __aepack__(self):
        return pack(self.enum, typeEnumeration)


def IsEnum(x):
    return isinstance(x, Enum)


def mkenum(enum):
    return enum if IsEnum(enum) else Enum(enum)


class InsertionLoc:

    def __init__(self, of, pos):
        self.of = of
        self.pos = pos

    def __repr__(self):
        return 'InsertionLoc(%r, %r)' % (self.of, self.pos)

    def __aepack__(self):
        rec = {'kobj': self.of,
         'kpos': self.pos}
        return pack(rec, forcetype='insl')


def beginning(of):
    return InsertionLoc(of, Enum('bgng'))


def end(of):
    return InsertionLoc(of, Enum('end '))


class Boolean:

    def __init__(self, bool):
        self.bool = not not bool

    def __repr__(self):
        return 'Boolean(%r)' % (self.bool,)

    def __str__(self):
        if self.bool:
            return 'True'
        else:
            return 'False'

    def __aepack__(self):
        return pack(struct.pack('b', self.bool), 'bool')


def IsBoolean(x):
    return isinstance(x, Boolean)


def mkboolean(bool):
    return bool if IsBoolean(bool) else Boolean(bool)


class Type:

    def __init__(self, type):
        self.type = '%-4.4s' % str(type)

    def __repr__(self):
        return 'Type(%r)' % (self.type,)

    def __str__(self):
        return string.strip(self.type)

    def __aepack__(self):
        return pack(self.type, typeType)


def IsType(x):
    return isinstance(x, Type)


def mktype(type):
    return type if IsType(type) else Type(type)


class Keyword:

    def __init__(self, keyword):
        self.keyword = '%-4.4s' % str(keyword)

    def __repr__(self):
        return 'Keyword(%r)' % repr(self.keyword)

    def __str__(self):
        return string.strip(self.keyword)

    def __aepack__(self):
        return pack(self.keyword, typeKeyword)


def IsKeyword(x):
    return isinstance(x, Keyword)


class Range:

    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __repr__(self):
        return 'Range(%r, %r)' % (self.start, self.stop)

    def __str__(self):
        return '%s thru %s' % (nice(self.start), nice(self.stop))

    def __aepack__(self):
        return pack({'star': self.start,
         'stop': self.stop}, 'rang')


def IsRange(x):
    return isinstance(x, Range)


class Comparison:

    def __init__(self, obj1, relo, obj2):
        self.obj1 = obj1
        self.relo = '%-4.4s' % str(relo)
        self.obj2 = obj2

    def __repr__(self):
        return 'Comparison(%r, %r, %r)' % (self.obj1, self.relo, self.obj2)

    def __str__(self):
        return '%s %s %s' % (nice(self.obj1), string.strip(self.relo), nice(self.obj2))

    def __aepack__(self):
        return pack({'obj1': self.obj1,
         'relo': mkenum(self.relo),
         'obj2': self.obj2}, 'cmpd')


def IsComparison(x):
    return isinstance(x, Comparison)


class NComparison(Comparison):

    def __init__(self, obj1, obj2):
        Comparison.__init__(obj1, self.relo, obj2)


class Ordinal:

    def __init__(self, abso):
        self.abso = '%-4.4s' % str(abso)

    def __repr__(self):
        return 'Ordinal(%r)' % (self.abso,)

    def __str__(self):
        return '%s' % string.strip(self.abso)

    def __aepack__(self):
        return pack(self.abso, 'abso')


def IsOrdinal(x):
    return isinstance(x, Ordinal)


class NOrdinal(Ordinal):

    def __init__(self):
        Ordinal.__init__(self, self.abso)


class Logical:

    def __init__(self, logc, term):
        self.logc = '%-4.4s' % str(logc)
        self.term = term

    def __repr__(self):
        return 'Logical(%r, %r)' % (self.logc, self.term)

    def __str__(self):
        if type(self.term) == ListType and len(self.term) == 2:
            return '%s %s %s' % (nice(self.term[0]), string.strip(self.logc), nice(self.term[1]))
        else:
            return '%s(%s)' % (string.strip(self.logc), nice(self.term))

    def __aepack__(self):
        return pack({'logc': mkenum(self.logc),
         'term': self.term}, 'logi')


def IsLogical(x):
    return isinstance(x, Logical)


class StyledText:

    def __init__(self, style, text):
        self.style = style
        self.text = text

    def __repr__(self):
        return 'StyledText(%r, %r)' % (self.style, self.text)

    def __str__(self):
        return self.text

    def __aepack__(self):
        return pack({'ksty': self.style,
         'ktxt': self.text}, 'STXT')


def IsStyledText(x):
    return isinstance(x, StyledText)


class AEText:

    def __init__(self, script, style, text):
        self.script = script
        self.style = style
        self.text = text

    def __repr__(self):
        return 'AEText(%r, %r, %r)' % (self.script, self.style, self.text)

    def __str__(self):
        return self.text

    def __aepack__(self):
        return pack({keyAEScriptTag: self.script,
         keyAEStyles: self.style,
         keyAEText: self.text}, typeAEText)


def IsAEText(x):
    return isinstance(x, AEText)


class IntlText:

    def __init__(self, script, language, text):
        self.script = script
        self.language = language
        self.text = text

    def __repr__(self):
        return 'IntlText(%r, %r, %r)' % (self.script, self.language, self.text)

    def __str__(self):
        return self.text

    def __aepack__(self):
        return pack(struct.pack('hh', self.script, self.language) + self.text, typeIntlText)


def IsIntlText(x):
    return isinstance(x, IntlText)


class IntlWritingCode:

    def __init__(self, script, language):
        self.script = script
        self.language = language

    def __repr__(self):
        return 'IntlWritingCode(%r, %r)' % (self.script, self.language)

    def __str__(self):
        return 'script system %d, language %d' % (self.script, self.language)

    def __aepack__(self):
        return pack(struct.pack('hh', self.script, self.language), typeIntlWritingCode)


def IsIntlWritingCode(x):
    return isinstance(x, IntlWritingCode)


class QDPoint:

    def __init__(self, v, h):
        self.v = v
        self.h = h

    def __repr__(self):
        return 'QDPoint(%r, %r)' % (self.v, self.h)

    def __str__(self):
        return '(%d, %d)' % (self.v, self.h)

    def __aepack__(self):
        return pack(struct.pack('hh', self.v, self.h), typeQDPoint)


def IsQDPoint(x):
    return isinstance(x, QDPoint)


class QDRectangle:

    def __init__(self, v0, h0, v1, h1):
        self.v0 = v0
        self.h0 = h0
        self.v1 = v1
        self.h1 = h1

    def __repr__(self):
        return 'QDRectangle(%r, %r, %r, %r)' % (self.v0,
         self.h0,
         self.v1,
         self.h1)

    def __str__(self):
        return '(%d, %d)-(%d, %d)' % (self.v0,
         self.h0,
         self.v1,
         self.h1)

    def __aepack__(self):
        return pack(struct.pack('hhhh', self.v0, self.h0, self.v1, self.h1), typeQDRectangle)


def IsQDRectangle(x):
    return isinstance(x, QDRectangle)


class RGBColor:

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return 'RGBColor(%r, %r, %r)' % (self.r, self.g, self.b)

    def __str__(self):
        return '0x%x red, 0x%x green, 0x%x blue' % (self.r, self.g, self.b)

    def __aepack__(self):
        return pack(struct.pack('hhh', self.r, self.g, self.b), typeRGBColor)


def IsRGBColor(x):
    return isinstance(x, RGBColor)


class ObjectSpecifier:

    def __init__(self, want, form, seld, fr=None):
        self.want = want
        self.form = form
        self.seld = seld
        self.fr = fr

    def __repr__(self):
        s = 'ObjectSpecifier(%r, %r, %r' % (self.want, self.form, self.seld)
        if self.fr:
            s = s + ', %r)' % (self.fr,)
        else:
            s = s + ')'
        return s

    def __aepack__(self):
        return pack({'want': mktype(self.want),
         'form': mkenum(self.form),
         'seld': self.seld,
         'from': self.fr}, 'obj ')


def IsObjectSpecifier(x):
    return isinstance(x, ObjectSpecifier)


class Property(ObjectSpecifier):

    def __init__(self, which, fr=None, want='prop'):
        ObjectSpecifier.__init__(self, want, 'prop', mktype(which), fr)

    def __repr__(self):
        if self.fr:
            return 'Property(%r, %r)' % (self.seld.type, self.fr)
        else:
            return 'Property(%r)' % (self.seld.type,)

    def __str__(self):
        if self.fr:
            return 'Property %s of %s' % (str(self.seld), str(self.fr))
        else:
            return 'Property %s' % str(self.seld)


class NProperty(ObjectSpecifier):

    def __init__(self, fr=None):
        self.want = 'prop'
        ObjectSpecifier.__init__(self, self.want, 'prop', mktype(self.which), fr)

    def __repr__(self):
        rv = 'Property(%r' % (self.seld.type,)
        if self.fr:
            rv = rv + ', fr=%r' % (self.fr,)
        if self.want != 'prop':
            rv = rv + ', want=%r' % (self.want,)
        return rv + ')'

    def __str__(self):
        if self.fr:
            return 'Property %s of %s' % (str(self.seld), str(self.fr))
        else:
            return 'Property %s' % str(self.seld)


class SelectableItem(ObjectSpecifier):

    def __init__(self, want, seld, fr=None):
        t = type(seld)
        if t == StringType:
            form = 'name'
        elif IsRange(seld):
            form = 'rang'
        elif IsComparison(seld) or IsLogical(seld):
            form = 'test'
        elif t == TupleType:
            form, seld = seld
        else:
            form = 'indx'
        ObjectSpecifier.__init__(self, want, form, seld, fr)


class ComponentItem(SelectableItem):
    _propdict = {}
    _elemdict = {}

    def __init__(self, which, fr=None):
        SelectableItem.__init__(self, self.want, which, fr)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.seld) if not self.fr else '%s(%r, %r)' % (self.__class__.__name__, self.seld, self.fr)

    def __str__(self):
        seld = self.seld
        if type(seld) == StringType:
            ss = repr(seld)
        else:
            start, stop = IsRange(seld) and seld.start, seld.stop
            if type(start) == InstanceType == type(stop):
                if start.__class__ == self.__class__ == stop.__class__:
                    ss = str(start.seld) + ' thru ' + str(stop.seld)
                else:
                    ss = str(seld)
            else:
                ss = str(seld)
        s = '%s %s' % (self.__class__.__name__, ss)
        if self.fr:
            s = s + ' of %s' % str(self.fr)
        return s

    def __getattr__(self, name):
        if name in self._elemdict:
            cls = self._elemdict[name]
            return DelayedComponentItem(cls, self)
        if name in self._propdict:
            cls = self._propdict[name]
            return cls(self)
        raise AttributeError, name


class DelayedComponentItem:

    def __init__(self, compclass, fr):
        self.compclass = compclass
        self.fr = fr

    def __call__(self, which):
        return self.compclass(which, self.fr)

    def __repr__(self):
        return '%s(???, %r)' % (self.__class__.__name__, self.fr)

    def __str__(self):
        return 'selector for element %s of %s' % (self.__class__.__name__, str(self.fr))


template = "\nclass %s(ComponentItem): want = '%s'\n"
exec template % ('Text', 'text')
exec template % ('Character', 'cha ')
exec template % ('Word', 'cwor')
exec template % ('Line', 'clin')
exec template % ('paragraph', 'cpar')
exec template % ('Window', 'cwin')
exec template % ('Document', 'docu')
exec template % ('File', 'file')
exec template % ('InsertionPoint', 'cins')
