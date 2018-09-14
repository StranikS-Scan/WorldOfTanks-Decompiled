# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/ic.py
"""IC wrapper module, based on Internet Config 1.3"""
from warnings import warnpy3k
warnpy3k('In 3.x, the ic module is removed.', stacklevel=2)
import icglue
import string
import sys
import os
from Carbon import Res
import Carbon.File
import macostools
error = icglue.error
icPrefNotFoundErr = -666
icPermErr = -667
icPrefDataErr = -668
icInternalErr = -669
icTruncatedErr = -670
icNoMoreWritersErr = -671
icNothingToOverrideErr = -672
icNoURLErr = -673
icConfigNotFoundErr = -674
icConfigInappropriateErr = -675
ICattr_no_change = -1
icNoPerm = 0
icReadOnlyPerm = 1
icReadWritePerm = 2

class ICOpaqueData:
    """An unparseable IC entry"""

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return 'ICOpaqueData(%r)' % (self.data,)


_ICOpaqueDataType = type(ICOpaqueData(''))

def _decode_default(data, key):
    if len(data) == 0:
        return data
    return data[1:] if ord(data[0]) == len(data) - 1 else ICOpaqueData(data)


def _decode_multistr(data, key):
    numstr = ord(data[0]) << 8 | ord(data[1])
    rv = []
    ptr = 2
    for i in range(numstr):
        strlen = ord(data[ptr])
        str = data[ptr + 1:ptr + strlen + 1]
        rv.append(str)
        ptr = ptr + strlen + 1

    return rv


def _decode_fontrecord(data, key):
    size = ord(data[0]) << 8 | ord(data[1])
    face = ord(data[2])
    namelen = ord(data[4])
    return (size, face, data[5:5 + namelen])


def _decode_boolean(data, key):
    return ord(data[0])


def _decode_text(data, key):
    return data


def _decode_charset(data, key):
    return (data[:256], data[256:])


def _decode_appspec(data, key):
    namelen = ord(data[4])
    return (data[0:4], data[5:5 + namelen])


def _code_default(data, key):
    return chr(len(data)) + data


def _code_multistr(data, key):
    numstr = len(data)
    rv = chr(numstr >> 8 & 255) + chr(numstr & 255)
    for i in data:
        rv = rv + _code_default(i)

    return rv


def _code_fontrecord(data, key):
    size, face, name = data
    return chr(size >> 8 & 255) + chr(size & 255) + chr(face & 255) + chr(0) + _code_default(name)


def _code_boolean(data, key):
    print 'XXXX boolean:', repr(data)
    return chr(data)


def _code_text(data, key):
    return data


def _code_charset(data, key):
    return data[0] + data[1]


def _code_appspec(data, key):
    return data[0] + _code_default(data[1])


_decoder_table = {'ArchieAll': (_decode_multistr, _code_multistr),
 'UMichAll': (_decode_multistr, _code_multistr),
 'InfoMacAll': (_decode_multistr, _code_multistr),
 'ListFont': (_decode_fontrecord, _code_fontrecord),
 'ScreenFont': (_decode_fontrecord, _code_fontrecord),
 'PrinterFont': (_decode_fontrecord, _code_fontrecord),
 'Signature': (_decode_text, _code_text),
 'Plan': (_decode_text, _code_text),
 'MailHeaders': (_decode_text, _code_text),
 'NewsHeaders': (_decode_text, _code_text),
 'CharacterSet': (_decode_charset, _code_charset),
 'Helper\xa5': (_decode_appspec, _code_appspec),
 'NewMailFlashIcon': (_decode_boolean, _code_boolean),
 'NewMailDialog': (_decode_boolean, _code_boolean),
 'NewMailPlaySound': (_decode_boolean, _code_boolean),
 'NoProxyDomains': (_decode_multistr, _code_multistr),
 'UseHTTPProxy': (_decode_boolean, _code_boolean),
 'UseGopherProxy': (_decode_boolean, _code_boolean),
 'UseFTPProxy': (_decode_boolean, _code_boolean),
 'UsePassiveFTP': (_decode_boolean, _code_boolean)}

def _decode(data, key):
    if '\xa5' in key:
        key2 = key[:string.index(key, '\xa5') + 1]
    else:
        key2 = key
    if key2 in _decoder_table:
        decoder = _decoder_table[key2][0]
    else:
        decoder = _decode_default
    return decoder(data, key)


def _code(data, key):
    if type(data) == _ICOpaqueDataType:
        return data.data
    if '\xa5' in key:
        key2 = key[:string.index(key, '\xa5') + 1]
    else:
        key2 = key
    if key2 in _decoder_table:
        coder = _decoder_table[key2][1]
    else:
        coder = _code_default
    return coder(data, key)


class IC:

    def __init__(self, signature='Pyth', ic=None):
        if ic:
            self.ic = ic
        else:
            self.ic = icglue.ICStart(signature)
            if hasattr(self.ic, 'ICFindConfigFile'):
                self.ic.ICFindConfigFile()
        self.h = Res.Resource('')

    def keys(self):
        rv = []
        self.ic.ICBegin(icReadOnlyPerm)
        num = self.ic.ICCountPref()
        for i in range(num):
            rv.append(self.ic.ICGetIndPref(i + 1))

        self.ic.ICEnd()
        return rv

    def has_key(self, key):
        return self.__contains__(key)

    def __contains__(self, key):
        try:
            dummy = self.ic.ICFindPrefHandle(key, self.h)
        except icglue.error:
            return 0

    def __getitem__(self, key):
        attr = self.ic.ICFindPrefHandle(key, self.h)
        return _decode(self.h.data, key)

    def __setitem__(self, key, value):
        value = _code(value, key)
        self.ic.ICSetPref(key, ICattr_no_change, value)

    def launchurl(self, url, hint=''):
        if url[:6] == 'file:/' and url[6] != '/':
            url = 'file:///' + url[6:]
        self.ic.ICLaunchURL(hint, url, 0, len(url))

    def parseurl(self, data, start=None, end=None, hint=''):
        if start is None:
            selStart = 0
            selEnd = len(data)
        else:
            selStart = selEnd = start
        if end is not None:
            selEnd = end
        selStart, selEnd = self.ic.ICParseURL(hint, data, selStart, selEnd, self.h)
        return (self.h.data, selStart, selEnd)

    def mapfile(self, file):
        if type(file) != type(''):
            file = file.as_tuple()[2]
        return self.ic.ICMapFilename(file)

    def maptypecreator(self, type, creator, filename=''):
        return self.ic.ICMapTypeCreator(type, creator, filename)

    def settypecreator(self, file):
        file = Carbon.File.pathname(file)
        record = self.mapfile(os.path.split(file)[1])
        MacOS.SetCreatorAndType(file, record[2], record[1])
        macostools.touched(fss)


_dft_ic = None

def launchurl(url, hint=''):
    global _dft_ic
    if _dft_ic is None:
        _dft_ic = IC()
    return _dft_ic.launchurl(url, hint)


def parseurl(data, start=None, end=None, hint=''):
    global _dft_ic
    if _dft_ic is None:
        _dft_ic = IC()
    return _dft_ic.parseurl(data, start, end, hint)


def mapfile(filename):
    global _dft_ic
    if _dft_ic is None:
        _dft_ic = IC()
    return _dft_ic.mapfile(filename)


def maptypecreator(type, creator, filename=''):
    global _dft_ic
    if _dft_ic is None:
        _dft_ic = IC()
    return _dft_ic.maptypecreator(type, creator, filename)


def settypecreator(file):
    global _dft_ic
    if _dft_ic is None:
        _dft_ic = IC()
    return _dft_ic.settypecreator(file)


def _test():
    ic = IC()
    for k in ic.keys():
        try:
            v = ic[k]
        except error:
            v = '????'

        print k, '\t', v

    sys.exit(1)


if __name__ == '__main__':
    _test()
