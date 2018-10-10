# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/xmpp_string_grep.py
import stringprep
import types
import unicodedata
from soft_exception import SoftException

class XmppStringPrepError(SoftException):
    pass


def doMappingToNothing(char):
    return u'' if stringprep.in_table_b1(char) else char


def doMappingSpaceChars(char):
    return u' ' if stringprep.in_table_c12(char) else char


def normalizeToNFKC(data):
    return unicodedata.normalize('NFKC', data)


def normalizeToNFC(data):
    return unicodedata.normalize('NFC', data)


_NODE_PREP_PROHIBITED = {u'"',
 u'&',
 u"'",
 u'/',
 u':',
 u'<',
 u'>',
 u'@'}

def inNodeProhibitedChars(char):
    return char in _NODE_PREP_PROHIBITED


def _isCharProhibited(table, char):
    if table(char):
        raise XmppStringPrepError('There is prohibited character: {0!r}'.format(char))


def _isCharUnassigned(table, char):
    if table(char):
        raise XmppStringPrepError('There is unassigned character: {0!r}'.format(char))


class _StringPrepProfile(object):
    __slots__ = ('_unassigned', '_mapping', '_normalization', '_prohibited', '_bidi')

    def __init__(self, mapping=None, unassigned=None, normalization=None, prohibited=None, bidi=True):
        self._unassigned = unassigned or []
        self._mapping = mapping or []
        self._normalization = normalization
        self._prohibited = prohibited or []
        self._bidi = bidi

    def prepare(self, data):
        if not isinstance(data, types.UnicodeType):
            data = unicode(data, 'utf8')
        result = self._doMapping(data)
        result = self._doNormalization(result)
        result = self._checkProhibited(result)
        result = self._checkUnassigned(result)
        return result

    def _doMapping(self, data):
        result = data
        for table in self._mapping:
            result = map(table, data)

        return u''.join(result)

    def _doNormalization(self, data):
        result = data
        if self._normalization and callable(self._normalization):
            result = self._normalization(result)
        return result

    def _checkProhibited(self, data):
        for item in self._prohibited:
            map(lambda char, table=item: _isCharProhibited(table, char), data)

        return data

    def _checkUnassigned(self, data):
        for item in self._unassigned:
            map(lambda char, table=item: _isCharUnassigned(table, char), data)

        return data

    def _checkBidi(self, data):
        hasL = False
        hasRorAL = False
        for char in data:
            if stringprep.in_table_d1(char):
                hasRorAL = True
            if stringprep.in_table_d2(char):
                hasL = True

        if hasL and hasRorAL:
            raise XmppStringPrepError('String contains RandALCat characters and LCat characters')
        if hasRorAL and (not stringprep.in_table_d1(data[0]) or not stringprep.in_table_d1(data[-1])):
            raise XmppStringPrepError('RandALCat character MUST be the first character of the string, and a RandALCat character MUST be the last character of the string')
        return data


NodePrep = _StringPrepProfile(unassigned=(stringprep.in_table_a1,), mapping=(doMappingToNothing, stringprep.map_table_b2), normalization=normalizeToNFKC, prohibited=(stringprep.in_table_c11,
 stringprep.in_table_c12,
 stringprep.in_table_c21,
 stringprep.in_table_c22,
 stringprep.in_table_c3,
 stringprep.in_table_c4,
 stringprep.in_table_c5,
 stringprep.in_table_c6,
 stringprep.in_table_c7,
 stringprep.in_table_c8,
 stringprep.in_table_c9,
 inNodeProhibitedChars), bidi=True)
ResourcePrep = _StringPrepProfile(unassigned=(stringprep.in_table_a1,), mapping=(doMappingToNothing,), normalization=normalizeToNFC, prohibited=(stringprep.in_table_c12,
 stringprep.in_table_c21,
 stringprep.in_table_c22,
 stringprep.in_table_c3,
 stringprep.in_table_c4,
 stringprep.in_table_c5,
 stringprep.in_table_c6,
 stringprep.in_table_c7,
 stringprep.in_table_c8,
 stringprep.in_table_c9), bidi=True)
