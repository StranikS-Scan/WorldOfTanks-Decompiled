# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/aepack.py
"""Tools for use in AppleEvent clients and servers:
conversion between AE types and python types

pack(x) converts a Python object to an AEDesc object
unpack(desc) does the reverse
coerce(x, wanted_sample) coerces a python object to another python object
"""
from warnings import warnpy3k
warnpy3k('In 3.x, the aepack module is removed.', stacklevel=2)
import struct
import types
from types import *
from Carbon import AE
from Carbon.AppleEvents import *
import MacOS
import Carbon.File
import aetypes
from aetypes import mkenum, ObjectSpecifier
unpacker_coercions = {typeComp: typeFloat,
 typeColorTable: typeAEList,
 typeDrawingArea: typeAERecord,
 typeFixed: typeFloat,
 typeExtended: typeFloat,
 typePixelMap: typeAERecord,
 typeRotation: typeAERecord,
 typeStyledText: typeAERecord,
 typeTextStyles: typeAERecord}
AEDescType = AE.AEDescType
try:
    FSSType = Carbon.File.FSSpecType
except AttributeError:

    class FSSType:
        pass


FSRefType = Carbon.File.FSRefType
AliasType = Carbon.File.AliasType

def packkey(ae, key, value):
    if hasattr(key, 'which'):
        keystr = key.which
    elif hasattr(key, 'want'):
        keystr = key.want
    else:
        keystr = key
    ae.AEPutParamDesc(keystr, pack(value))


def pack(x, forcetype=None):
    """Pack a python object into an AE descriptor"""
    if forcetype:
        if type(x) is StringType:
            return AE.AECreateDesc(forcetype, x)
        else:
            return pack(x).AECoerceDesc(forcetype)
    if x is None:
        return AE.AECreateDesc('null', '')
    elif isinstance(x, AEDescType):
        return x
    elif isinstance(x, FSSType):
        return AE.AECreateDesc('fss ', x.data)
    elif isinstance(x, FSRefType):
        return AE.AECreateDesc('fsrf', x.data)
    elif isinstance(x, AliasType):
        return AE.AECreateDesc('alis', x.data)
    elif isinstance(x, IntType):
        return AE.AECreateDesc('long', struct.pack('l', x))
    elif isinstance(x, FloatType):
        return AE.AECreateDesc('doub', struct.pack('d', x))
    elif isinstance(x, StringType):
        return AE.AECreateDesc('TEXT', x)
    elif isinstance(x, UnicodeType):
        data = x.encode('utf16')
        if data[:2] == '\xfe\xff':
            data = data[2:]
        return AE.AECreateDesc('utxt', data)
    elif isinstance(x, ListType):
        list = AE.AECreateList('', 0)
        for item in x:
            list.AEPutDesc(0, pack(item))

        return list
    elif isinstance(x, DictionaryType):
        record = AE.AECreateList('', 1)
        for key, value in x.items():
            packkey(record, key, value)

        return record
    elif type(x) == types.ClassType and issubclass(x, ObjectSpecifier):
        return AE.AECreateDesc('type', x.want)
    elif hasattr(x, '__aepack__'):
        return x.__aepack__()
    elif hasattr(x, 'which'):
        return AE.AECreateDesc('TEXT', x.which)
    else:
        return AE.AECreateDesc('TEXT', x.want) if hasattr(x, 'want') else AE.AECreateDesc('TEXT', repr(x))


def unpack(desc, formodulename=''):
    """Unpack an AE descriptor to a python object"""
    t = desc.type
    if t in unpacker_coercions:
        desc = desc.AECoerceDesc(unpacker_coercions[t])
        t = desc.type
    if t == typeAEList:
        l = []
        for i in range(desc.AECountItems()):
            keyword, item = desc.AEGetNthDesc(i + 1, '****')
            l.append(unpack(item, formodulename))

        return l
    elif t == typeAERecord:
        d = {}
        for i in range(desc.AECountItems()):
            keyword, item = desc.AEGetNthDesc(i + 1, '****')
            d[keyword] = unpack(item, formodulename)

        return d
    elif t == typeAEText:
        record = desc.AECoerceDesc('reco')
        return mkaetext(unpack(record, formodulename))
    elif t == typeAlias:
        return Carbon.File.Alias(rawdata=desc.data)
    elif t == typeBoolean:
        return struct.unpack('b', desc.data)[0]
    elif t == typeChar:
        return desc.data
    elif t == typeUnicodeText:
        return unicode(desc.data, 'utf16')
    elif t == typeEnumeration:
        return mkenum(desc.data)
    elif t == typeFalse:
        return 0
    elif t == typeFloat:
        data = desc.data
        return struct.unpack('d', data)[0]
    elif t == typeFSS:
        return Carbon.File.FSSpec(rawdata=desc.data)
    elif t == typeFSRef:
        return Carbon.File.FSRef(rawdata=desc.data)
    elif t == typeInsertionLoc:
        record = desc.AECoerceDesc('reco')
        return mkinsertionloc(unpack(record, formodulename))
    elif t == typeIntlText:
        script, language = struct.unpack('hh', desc.data[:4])
        return aetypes.IntlText(script, language, desc.data[4:])
    elif t == typeIntlWritingCode:
        script, language = struct.unpack('hh', desc.data)
        return aetypes.IntlWritingCode(script, language)
    elif t == typeKeyword:
        return mkkeyword(desc.data)
    elif t == typeLongInteger:
        return struct.unpack('l', desc.data)[0]
    elif t == typeLongDateTime:
        a, b = struct.unpack('lL', desc.data)
        return (long(a) << 32) + b
    elif t == typeNull:
        return None
    elif t == typeMagnitude:
        v = struct.unpack('l', desc.data)
        if v < 0:
            v = 4294967296L + v
        return v
    elif t == typeObjectSpecifier:
        record = desc.AECoerceDesc('reco')
        if formodulename:
            return mkobjectfrommodule(unpack(record, formodulename), formodulename)
        return mkobject(unpack(record, formodulename))
    elif t == typeQDPoint:
        v, h = struct.unpack('hh', desc.data)
        return aetypes.QDPoint(v, h)
    elif t == typeQDRectangle:
        v0, h0, v1, h1 = struct.unpack('hhhh', desc.data)
        return aetypes.QDRectangle(v0, h0, v1, h1)
    elif t == typeRGBColor:
        r, g, b = struct.unpack('hhh', desc.data)
        return aetypes.RGBColor(r, g, b)
    elif t == typeShortFloat:
        return struct.unpack('f', desc.data)[0]
    elif t == typeShortInteger:
        return struct.unpack('h', desc.data)[0]
    elif t == typeTargetID:
        return mktargetid(desc.data)
    elif t == typeTrue:
        return 1
    elif t == typeType:
        return mktype(desc.data, formodulename)
    elif t == 'rang':
        record = desc.AECoerceDesc('reco')
        return mkrange(unpack(record, formodulename))
    elif t == 'cmpd':
        record = desc.AECoerceDesc('reco')
        return mkcomparison(unpack(record, formodulename))
    elif t == 'logi':
        record = desc.AECoerceDesc('reco')
        return mklogical(unpack(record, formodulename))
    else:
        return mkunknown(desc.type, desc.data)


def coerce(data, egdata):
    """Coerce a python object to another type using the AE coercers"""
    pdata = pack(data)
    pegdata = pack(egdata)
    pdata = pdata.AECoerceDesc(pegdata.type)
    return unpack(pdata)


def mktargetid(data):
    sessionID = getlong(data[:4])
    name = mkppcportrec(data[4:76])
    location = mklocationnamerec(data[76:112])
    rcvrName = mkppcportrec(data[112:184])
    return (sessionID,
     name,
     location,
     rcvrName)


def mkppcportrec(rec):
    namescript = getword(rec[:2])
    name = getpstr(rec[2:35])
    portkind = getword(rec[36:38])
    if portkind == 1:
        ctor = rec[38:42]
        type = rec[42:46]
        identity = (ctor, type)
    else:
        identity = getpstr(rec[38:71])
    return (namescript,
     name,
     portkind,
     identity)


def mklocationnamerec(rec):
    kind = getword(rec[:2])
    stuff = rec[2:]
    if kind == 0:
        stuff = None
    if kind == 2:
        stuff = getpstr(stuff)
    return (kind, stuff)


def mkunknown(type, data):
    return aetypes.Unknown(type, data)


def getpstr(s):
    return s[1:1 + ord(s[0])]


def getlong(s):
    return ord(s[0]) << 24 | ord(s[1]) << 16 | ord(s[2]) << 8 | ord(s[3])


def getword(s):
    return ord(s[0]) << 8 | ord(s[1]) << 0


def mkkeyword(keyword):
    return aetypes.Keyword(keyword)


def mkrange(dict):
    return aetypes.Range(dict['star'], dict['stop'])


def mkcomparison(dict):
    return aetypes.Comparison(dict['obj1'], dict['relo'].enum, dict['obj2'])


def mklogical(dict):
    return aetypes.Logical(dict['logc'], dict['term'])


def mkstyledtext(dict):
    return aetypes.StyledText(dict['ksty'], dict['ktxt'])


def mkaetext(dict):
    return aetypes.AEText(dict[keyAEScriptTag], dict[keyAEStyles], dict[keyAEText])


def mkinsertionloc(dict):
    return aetypes.InsertionLoc(dict[keyAEObject], dict[keyAEPosition])


def mkobject(dict):
    want = dict['want'].type
    form = dict['form'].enum
    seld = dict['seld']
    fr = dict['from']
    if form in ('name', 'indx', 'rang', 'test'):
        if want == 'text':
            return aetypes.Text(seld, fr)
        if want == 'cha ':
            return aetypes.Character(seld, fr)
        if want == 'cwor':
            return aetypes.Word(seld, fr)
        if want == 'clin':
            return aetypes.Line(seld, fr)
        if want == 'cpar':
            return aetypes.Paragraph(seld, fr)
        if want == 'cwin':
            return aetypes.Window(seld, fr)
        if want == 'docu':
            return aetypes.Document(seld, fr)
        if want == 'file':
            return aetypes.File(seld, fr)
        if want == 'cins':
            return aetypes.InsertionPoint(seld, fr)
    return aetypes.Property(seld.type, fr) if want == 'prop' and form == 'prop' and aetypes.IsType(seld) else aetypes.ObjectSpecifier(want, form, seld, fr)


def mkobjectfrommodule(dict, modulename):
    if type(dict['want']) == types.ClassType and issubclass(dict['want'], ObjectSpecifier):
        classtype = dict['want']
        dict['want'] = aetypes.mktype(classtype.want)
    want = dict['want'].type
    module = __import__(modulename)
    codenamemapper = module._classdeclarations
    classtype = codenamemapper.get(want, None)
    newobj = mkobject(dict)
    if classtype:
        assert issubclass(classtype, ObjectSpecifier)
        newobj.__class__ = classtype
    return newobj


def mktype(typecode, modulename=None):
    if modulename:
        module = __import__(modulename)
        codenamemapper = module._classdeclarations
        classtype = codenamemapper.get(typecode, None)
        if classtype:
            return classtype
    return aetypes.mktype(typecode)
