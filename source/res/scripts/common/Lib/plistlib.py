# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plistlib.py
__all__ = ['readPlist',
 'writePlist',
 'readPlistFromString',
 'writePlistToString',
 'readPlistFromResource',
 'writePlistToResource',
 'Plist',
 'Data',
 'Dict']
import binascii
import datetime
from cStringIO import StringIO
import re
import warnings

def readPlist(pathOrFile):
    didOpen = 0
    if isinstance(pathOrFile, (str, unicode)):
        pathOrFile = open(pathOrFile)
        didOpen = 1
    p = PlistParser()
    rootObject = p.parse(pathOrFile)
    if didOpen:
        pathOrFile.close()
    return rootObject


def writePlist(rootObject, pathOrFile):
    didOpen = 0
    if isinstance(pathOrFile, (str, unicode)):
        pathOrFile = open(pathOrFile, 'w')
        didOpen = 1
    writer = PlistWriter(pathOrFile)
    writer.writeln('<plist version="1.0">')
    writer.writeValue(rootObject)
    writer.writeln('</plist>')
    if didOpen:
        pathOrFile.close()


def readPlistFromString(data):
    return readPlist(StringIO(data))


def writePlistToString(rootObject):
    f = StringIO()
    writePlist(rootObject, f)
    return f.getvalue()


def readPlistFromResource(path, restype='plst', resid=0):
    warnings.warnpy3k('In 3.x, readPlistFromResource is removed.', stacklevel=2)
    from Carbon.File import FSRef, FSGetResourceForkName
    from Carbon.Files import fsRdPerm
    from Carbon import Res
    fsRef = FSRef(path)
    resNum = Res.FSOpenResourceFile(fsRef, FSGetResourceForkName(), fsRdPerm)
    Res.UseResFile(resNum)
    plistData = Res.Get1Resource(restype, resid).data
    Res.CloseResFile(resNum)
    return readPlistFromString(plistData)


def writePlistToResource(rootObject, path, restype='plst', resid=0):
    warnings.warnpy3k('In 3.x, writePlistToResource is removed.', stacklevel=2)
    from Carbon.File import FSRef, FSGetResourceForkName
    from Carbon.Files import fsRdWrPerm
    from Carbon import Res
    plistData = writePlistToString(rootObject)
    fsRef = FSRef(path)
    resNum = Res.FSOpenResourceFile(fsRef, FSGetResourceForkName(), fsRdWrPerm)
    Res.UseResFile(resNum)
    try:
        Res.Get1Resource(restype, resid).RemoveResource()
    except Res.Error:
        pass

    res = Res.Resource(plistData)
    res.AddResource(restype, resid, '')
    res.WriteResource()
    Res.CloseResFile(resNum)


class DumbXMLWriter:

    def __init__(self, file, indentLevel=0, indent='\t'):
        self.file = file
        self.stack = []
        self.indentLevel = indentLevel
        self.indent = indent

    def beginElement(self, element):
        self.stack.append(element)
        self.writeln('<%s>' % element)
        self.indentLevel += 1

    def endElement(self, element):
        self.indentLevel -= 1
        self.writeln('</%s>' % element)

    def simpleElement(self, element, value=None):
        if value is not None:
            value = _escapeAndEncode(value)
            self.writeln('<%s>%s</%s>' % (element, value, element))
        else:
            self.writeln('<%s/>' % element)
        return

    def writeln(self, line):
        if line:
            self.file.write(self.indentLevel * self.indent + line + '\n')
        else:
            self.file.write('\n')


_dateParser = re.compile('(?P<year>\\d\\d\\d\\d)(?:-(?P<month>\\d\\d)(?:-(?P<day>\\d\\d)(?:T(?P<hour>\\d\\d)(?::(?P<minute>\\d\\d)(?::(?P<second>\\d\\d))?)?)?)?)?Z')

def _dateFromString(s):
    order = ('year', 'month', 'day', 'hour', 'minute', 'second')
    gd = _dateParser.match(s).groupdict()
    lst = []
    for key in order:
        val = gd[key]
        if val is None:
            break
        lst.append(int(val))

    return datetime.datetime(*lst)


def _dateToString(d):
    return '%04d-%02d-%02dT%02d:%02d:%02dZ' % (d.year,
     d.month,
     d.day,
     d.hour,
     d.minute,
     d.second)


_controlCharPat = re.compile('[\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x0b\\x0c\\x0e\\x0f\\x10\\x11\\x12\\x13\\x14\\x15\\x16\\x17\\x18\\x19\\x1a\\x1b\\x1c\\x1d\\x1e\\x1f]')

def _escapeAndEncode(text):
    m = _controlCharPat.search(text)
    if m is not None:
        raise ValueError("strings can't contains control characters; use plistlib.Data instead")
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text.encode('utf-8')


PLISTHEADER = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'

class PlistWriter(DumbXMLWriter):

    def __init__(self, file, indentLevel=0, indent='\t', writeHeader=1):
        if writeHeader:
            file.write(PLISTHEADER)
        DumbXMLWriter.__init__(self, file, indentLevel, indent)

    def writeValue(self, value):
        if isinstance(value, (str, unicode)):
            self.simpleElement('string', value)
        elif isinstance(value, bool):
            if value:
                self.simpleElement('true')
            else:
                self.simpleElement('false')
        elif isinstance(value, (int, long)):
            self.simpleElement('integer', '%d' % value)
        elif isinstance(value, float):
            self.simpleElement('real', repr(value))
        elif isinstance(value, dict):
            self.writeDict(value)
        elif isinstance(value, Data):
            self.writeData(value)
        elif isinstance(value, datetime.datetime):
            self.simpleElement('date', _dateToString(value))
        elif isinstance(value, (tuple, list)):
            self.writeArray(value)
        else:
            raise TypeError('unsuported type: %s' % type(value))

    def writeData(self, data):
        self.beginElement('data')
        self.indentLevel -= 1
        maxlinelength = max(16, 76 - len(self.indent.replace('\t', '        ') * self.indentLevel))
        for line in data.asBase64(maxlinelength).split('\n'):
            if line:
                self.writeln(line)

        self.indentLevel += 1
        self.endElement('data')

    def writeDict(self, d):
        self.beginElement('dict')
        items = d.items()
        items.sort()
        for key, value in items:
            if not isinstance(key, (str, unicode)):
                raise TypeError('keys must be strings')
            self.simpleElement('key', key)
            self.writeValue(value)

        self.endElement('dict')

    def writeArray(self, array):
        self.beginElement('array')
        for value in array:
            self.writeValue(value)

        self.endElement('array')


class _InternalDict(dict):

    def __getattr__(self, attr):
        try:
            value = self[attr]
        except KeyError:
            raise AttributeError, attr

        from warnings import warn
        warn('Attribute access from plist dicts is deprecated, use d[key] notation instead', PendingDeprecationWarning, 2)
        return value

    def __setattr__(self, attr, value):
        from warnings import warn
        warn('Attribute access from plist dicts is deprecated, use d[key] notation instead', PendingDeprecationWarning, 2)
        self[attr] = value

    def __delattr__(self, attr):
        try:
            del self[attr]
        except KeyError:
            raise AttributeError, attr

        from warnings import warn
        warn('Attribute access from plist dicts is deprecated, use d[key] notation instead', PendingDeprecationWarning, 2)


class Dict(_InternalDict):

    def __init__(self, **kwargs):
        from warnings import warn
        warn('The plistlib.Dict class is deprecated, use builtin dict instead', PendingDeprecationWarning, 2)
        super(Dict, self).__init__(**kwargs)


class Plist(_InternalDict):

    def __init__(self, **kwargs):
        from warnings import warn
        warn('The Plist class is deprecated, use the readPlist() and writePlist() functions instead', PendingDeprecationWarning, 2)
        super(Plist, self).__init__(**kwargs)

    def fromFile(cls, pathOrFile):
        rootObject = readPlist(pathOrFile)
        plist = cls()
        plist.update(rootObject)
        return plist

    fromFile = classmethod(fromFile)

    def write(self, pathOrFile):
        writePlist(self, pathOrFile)


def _encodeBase64(s, maxlinelength=76):
    maxbinsize = maxlinelength // 4 * 3
    pieces = []
    for i in range(0, len(s), maxbinsize):
        chunk = s[i:i + maxbinsize]
        pieces.append(binascii.b2a_base64(chunk))

    return ''.join(pieces)


class Data:

    def __init__(self, data):
        self.data = data

    def fromBase64(cls, data):
        return cls(binascii.a2b_base64(data))

    fromBase64 = classmethod(fromBase64)

    def asBase64(self, maxlinelength=76):
        return _encodeBase64(self.data, maxlinelength)

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return cmp(self.data, other.data)
        elif isinstance(other, str):
            return cmp(self.data, other)
        else:
            return cmp(id(self), id(other))

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self.data))


class PlistParser:

    def __init__(self):
        self.stack = []
        self.currentKey = None
        self.root = None
        return

    def parse(self, fileobj):
        from xml.parsers.expat import ParserCreate
        parser = ParserCreate()
        parser.StartElementHandler = self.handleBeginElement
        parser.EndElementHandler = self.handleEndElement
        parser.CharacterDataHandler = self.handleData
        parser.ParseFile(fileobj)
        return self.root

    def handleBeginElement(self, element, attrs):
        self.data = []
        handler = getattr(self, 'begin_' + element, None)
        if handler is not None:
            handler(attrs)
        return

    def handleEndElement(self, element):
        handler = getattr(self, 'end_' + element, None)
        if handler is not None:
            handler()
        return

    def handleData(self, data):
        self.data.append(data)

    def addObject(self, value):
        if self.currentKey is not None:
            self.stack[-1][self.currentKey] = value
            self.currentKey = None
        elif not self.stack:
            self.root = value
        else:
            self.stack[-1].append(value)
        return

    def getData(self):
        data = ''.join(self.data)
        try:
            data = data.encode('ascii')
        except UnicodeError:
            pass

        self.data = []
        return data

    def begin_dict(self, attrs):
        d = _InternalDict()
        self.addObject(d)
        self.stack.append(d)

    def end_dict(self):
        self.stack.pop()

    def end_key(self):
        self.currentKey = self.getData()

    def begin_array(self, attrs):
        a = []
        self.addObject(a)
        self.stack.append(a)

    def end_array(self):
        self.stack.pop()

    def end_true(self):
        self.addObject(True)

    def end_false(self):
        self.addObject(False)

    def end_integer(self):
        self.addObject(int(self.getData()))

    def end_real(self):
        self.addObject(float(self.getData()))

    def end_string(self):
        self.addObject(self.getData())

    def end_data(self):
        self.addObject(Data.fromBase64(self.getData()))

    def end_date(self):
        self.addObject(_dateFromString(self.getData()))
