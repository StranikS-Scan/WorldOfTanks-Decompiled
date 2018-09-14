# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/external_strings_utils.py
import re
import unicodedata
from debug_utils import LOG_CURRENT_EXCEPTION
from constants import CREDENTIALS_RESTRICTION, CREDENTIALS_RESTRICTION_SET
_MAX_NORMALIZED_NAME_BYTES = 96

class TextRestrictionsBasic(object):
    __slots__ = ('ACCOUNT_NAME_RE', 'ACCOUNT_NAME_MIN_LENGTH', 'ACCOUNT_NAME_MAX_LENGTH', 'ACCOUNT_NAME_MIN_LENGTH_REG', 'LOGIN_NAME_RE', 'LOGIN_NAME_MIN_LENGTH', 'LOGIN_NAME_MAX_LENGTH', 'PASSWORD_RE', 'PASSWORD_MIN_LENGTH', 'PASSWORD_MAX_LENGTH', 'UPPERCASE_CLAN_ABBREV', 'REQUIRE_NORMALIZED_CLAN_ABBREV', 'CLAN_ABBREV_RE', 'CLAN_NAME_MAX_LENGTH', 'CLAN_ABBREV_MAX_LENGTH', 'CLAN_DESCR_MAX_LENGTH', 'CLAN_MOTTO_MAX_LENGTH')

    def __init__(self):
        self.ACCOUNT_NAME_RE = re.compile('^[a-zA-Z0-9_]+$')
        self.ACCOUNT_NAME_MIN_LENGTH = 2
        self.ACCOUNT_NAME_MAX_LENGTH = 24
        self.ACCOUNT_NAME_MIN_LENGTH_REG = 3
        self.LOGIN_NAME_RE = re.compile('^[a-z0-9_-]+(\\.[a-z0-9_-]+)*@[a-z0-9-]+(\\.[a-z0-9-]+)*\\.([a-z]{2,4})$')
        self.LOGIN_NAME_MIN_LENGTH = 1
        self.LOGIN_NAME_MAX_LENGTH = 255
        self.PASSWORD_RE = re.compile('^[a-zA-Z0-9_]+$')
        self.PASSWORD_MIN_LENGTH = 6
        self.PASSWORD_MAX_LENGTH = 100
        self.UPPERCASE_CLAN_ABBREV = True
        self.REQUIRE_NORMALIZED_CLAN_ABBREV = True
        self.CLAN_ABBREV_RE = re.compile('^[A-Z0-9_\\-]+$')
        self.CLAN_NAME_MAX_LENGTH = 70
        self.CLAN_ABBREV_MAX_LENGTH = 5
        self.CLAN_DESCR_MAX_LENGTH = 1000
        self.CLAN_MOTTO_MAX_LENGTH = 100


class TextRestrictionsChinese(TextRestrictionsBasic):
    __slots__ = TextRestrictionsBasic.__slots__

    def __init__(self):
        super(TextRestrictionsChinese, self).__init__()
        ACCOUNT_NAME_EXCLUDED_SYMBOLS = range(32) + [34,
         38,
         39,
         47,
         58,
         60,
         62,
         64,
         127]
        self.ACCOUNT_NAME_RE = re.compile(u'(?u)^[^' + u''.join(map(lambda n: u'\\x%0.2x' % n, ACCOUNT_NAME_EXCLUDED_SYMBOLS)) + unichr(65535) + unichr(65534) + u']+$')
        self.ACCOUNT_NAME_MIN_LENGTH_REG = self.ACCOUNT_NAME_MIN_LENGTH
        self.LOGIN_NAME_RE = re.compile('^[_a-z0-9-+@.]+$')
        self.LOGIN_NAME_MIN_LENGTH = 4
        self.LOGIN_NAME_MAX_LENGTH = 50
        self.PASSWORD_RE = re.compile('^[!-~]+$')
        self.PASSWORD_MAX_LENGTH = 32
        self.CLAN_ABBREV_RE = self.ACCOUNT_NAME_RE
        self.UPPERCASE_CLAN_ABBREV = False
        self.REQUIRE_NORMALIZED_CLAN_ABBREV = False


class TextRestrictionsKorea(TextRestrictionsChinese):
    __slots__ = TextRestrictionsChinese.__slots__

    def __init__(self):
        super(TextRestrictionsKorea, self).__init__()
        self.LOGIN_NAME_MIN_LENGTH = 1
        self.LOGIN_NAME_MAX_LENGTH = 50
        self.LOGIN_NAME_RE = re.compile('^[a-z0-9_-]+(\\.[a-z0-9_-]+)*@([a-z0-9]([a-z0-9-]*[a-z0-9])?\\.)+[a-z]{2,4}$')
        self.PASSWORD_RE = re.compile('^[!-~]+$')
        self.ACCOUNT_NAME_RE = re.compile(u'^[a-zA-Z0-9_\uac00-\ud79d]+$')


if CREDENTIALS_RESTRICTION_SET == CREDENTIALS_RESTRICTION.BASIC:
    textRestrictions = TextRestrictionsBasic()
elif CREDENTIALS_RESTRICTION_SET == CREDENTIALS_RESTRICTION.CHINESE:
    textRestrictions = TextRestrictionsChinese()
elif CREDENTIALS_RESTRICTION_SET == CREDENTIALS_RESTRICTION.KOREA:
    textRestrictions = TextRestrictionsKorea()
else:
    assert False, 'Unknown credential restrictions set'
_ACCOUNT_NAME_RE = textRestrictions.ACCOUNT_NAME_RE
_ACCOUNT_NAME_MIN_LENGTH = textRestrictions.ACCOUNT_NAME_MIN_LENGTH
_ACCOUNT_NAME_MAX_LENGTH = textRestrictions.ACCOUNT_NAME_MAX_LENGTH
_ACCOUNT_NAME_MIN_LENGTH_REG = textRestrictions.ACCOUNT_NAME_MIN_LENGTH_REG
_LOGIN_NAME_RE = textRestrictions.LOGIN_NAME_RE
_LOGIN_NAME_MIN_LENGTH = textRestrictions.LOGIN_NAME_MIN_LENGTH
_LOGIN_NAME_MAX_LENGTH = textRestrictions.LOGIN_NAME_MAX_LENGTH
_PASSWORD_RE = textRestrictions.PASSWORD_RE
_PASSWORD_MIN_LENGTH = textRestrictions.PASSWORD_MIN_LENGTH
_PASSWORD_MAX_LENGTH = textRestrictions.PASSWORD_MAX_LENGTH
_CLAN_ABBREV_RE = textRestrictions.CLAN_ABBREV_RE
_CLAN_NAME_MAX_LENGTH = textRestrictions.CLAN_NAME_MAX_LENGTH
_CLAN_ABBREV_MAX_LENGTH = textRestrictions.CLAN_ABBREV_MAX_LENGTH
_UPPERCASE_CLAN_ABBREV = textRestrictions.UPPERCASE_CLAN_ABBREV
_REQUIRE_NORMALIZED_CLAN_ABBREV = textRestrictions.REQUIRE_NORMALIZED_CLAN_ABBREV
CLAN_DESCR_MAX_LENGTH = textRestrictions.CLAN_DESCR_MAX_LENGTH
CLAN_MOTTO_MAX_LENGTH = textRestrictions.CLAN_MOTTO_MAX_LENGTH

def getClanAbbrevMaxLength():
    return _CLAN_ABBREV_MAX_LENGTH


CLAN_DESCR_MAX_BYTES = CLAN_DESCR_MAX_LENGTH * 4
CLAN_MOTTO_MAX_BYTES = CLAN_MOTTO_MAX_LENGTH * 4

def unicode_from_utf8(utf8str, unicodeNormalForm='NFKC'):
    unicodeStr = unicode(utf8str, 'utf8')
    return (unicodedata.normalize(unicodeNormalForm, unicodeStr), unicodeStr)


def utf8_accepted(utf8str, regExp, minLen, maxLen, unicodeNormalForm='NFKC', checkBeforeNormalisation=True):
    nfkc, plain = unicode_from_utf8(utf8str, unicodeNormalForm)

    def matchFn(uniStr):
        return regExp.match(uniStr) and minLen <= len(uniStr) <= maxLen

    return False if checkBeforeNormalisation and not matchFn(plain) else matchFn(nfkc)


def normalized_unicode_trim(utf8str, length, unicodeNormalForm='NFKC'):
    try:
        unicodeStr, _ = unicode_from_utf8(utf8str, unicodeNormalForm)
        if len(unicodeStr) > max(0, length):
            unicodeStr = unicodeStr[:length]
        return unicodeStr.encode('utf8')
    except:
        LOG_CURRENT_EXCEPTION()
        return None

    return None


def normalized_unicode_trim_and_lowercase(utf8str, length, unicodeNormalForm='NFKC'):
    try:
        unicodeStr, _ = unicode_from_utf8(utf8str, unicodeNormalForm)
        if len(unicodeStr) > max(0, length):
            unicodeStr = unicodeStr[:length]
        return unicodeStr.lower().encode('utf8')
    except:
        LOG_CURRENT_EXCEPTION()
        return None

    return None


def isAccountNameValid(text, minLength=_ACCOUNT_NAME_MIN_LENGTH):
    return utf8_accepted(text, _ACCOUNT_NAME_RE, minLength, _ACCOUNT_NAME_MAX_LENGTH)


def normalizedAccountName(text):
    return normalized_unicode_trim_and_lowercase(text, _ACCOUNT_NAME_MAX_LENGTH)


def isPasswordValid(text):
    return utf8_accepted(text, _PASSWORD_RE, _PASSWORD_MIN_LENGTH, _PASSWORD_MAX_LENGTH)


def isAccountLoginValid(text):
    return utf8_accepted(text, _LOGIN_NAME_RE, _LOGIN_NAME_MIN_LENGTH, _LOGIN_NAME_MAX_LENGTH)


def normalizedAccountLogin(text):
    try:
        text = normalize_utf8(text)
        if len(text) > _LOGIN_NAME_MAX_LENGTH:
            text = text[:_LOGIN_NAME_MAX_LENGTH]
        return text.lower()
    except:
        LOG_CURRENT_EXCEPTION()
        return None

    return None


def forgeAccountNormalizedName(origNormalizedName, centerID):
    ext = '\x01' + str(centerID)
    return origNormalizedName[:_MAX_NORMALIZED_NAME_BYTES - len(ext)] + ext


def isClanNameValid(text):
    try:
        utext = unicode(text, 'utf8').strip()
        if utext.encode('utf8') != text:
            return False
        if not 2 <= len(utext) <= _CLAN_NAME_MAX_LENGTH:
            return False
        for word in utext.split(' '):
            if not word or any(map(lambda c: ord(c) < 32, word)):
                return False

        return True
    except:
        LOG_CURRENT_EXCEPTION()
        return False


def normalizedClanName(text):
    try:
        utext, _ = unicode_from_utf8(text)
        if len(utext) > _CLAN_NAME_MAX_LENGTH:
            utext = utext[:_CLAN_NAME_MAX_LENGTH]
        return utext.lower().encode('utf8')
    except:
        LOG_CURRENT_EXCEPTION()
        return None

    return None


def isClanAbbrevValid(abbrev):
    return utf8_accepted(abbrev, _CLAN_ABBREV_RE, 2, _CLAN_ABBREV_MAX_LENGTH) and (not _REQUIRE_NORMALIZED_CLAN_ABBREV or abbrev == normalizedClanAbbrev(abbrev))


def normalizedClanAbbrev(abbrev):
    try:
        abbrev, _ = unicode_from_utf8(abbrev)
        if len(abbrev) > _CLAN_ABBREV_MAX_LENGTH:
            abbrev = abbrev[:_CLAN_ABBREV_MAX_LENGTH]
        if _UPPERCASE_CLAN_ABBREV:
            abbrev = abbrev.upper()
        return abbrev.encode('utf8')
    except:
        LOG_CURRENT_EXCEPTION()
        return None

    return None


def isChannelNameValid(channelName):
    test = channelName.strip()
    return test and test[0] not in '[<{('


def escapeSQL(text, default='\\0'):
    return default if text is None else text.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\x00', '\\0')


def normalize_utf8(utf8str):
    return unicode(utf8str, 'utf8').encode('utf8')


def truncate_utf8(utf8str, maxbytes):
    if len(utf8str) < maxbytes:
        return utf8str
    if maxbytes <= 0:
        return ''
    if _is_utf8_one_byte(utf8str[maxbytes - 1]):
        return utf8str[:maxbytes]
    for x in xrange(1, 5):
        if _is_utf8_first_byte(utf8str[maxbytes - x]):
            ut8_len = _decode_utf8_len_byte(utf8str[maxbytes - x])
            if x == ut8_len:
                break
            return utf8str[:maxbytes - x]

    return utf8str[:maxbytes]


def _is_utf8_one_byte(byte):
    o = ord(byte)
    return 127 & o == o


def _is_utf8_first_byte(byte):
    o = ord(byte)
    return 191 & o != o


def _decode_utf8_len_byte(byte):
    o = ord(byte)
    v = 240 & o
    if v >= 240:
        return 4
    if v >= 224:
        return 3
    if v >= 192:
        return 2
    return 1 if v < 127 else 0
