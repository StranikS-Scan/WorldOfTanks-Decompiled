# Embedded file name: scripts/client/helpers/__init__.py
import types
import BigWorld
import ResMgr
import Settings
import i18n
import constants
from debug_utils import LOG_CURRENT_EXCEPTION
VERSION_FILE_PATH = '../version.xml'

def isPlayerAccount():
    return hasattr(BigWorld.player(), 'databaseID')


def isPlayerAvatar():
    return hasattr(BigWorld.player(), 'arena')


def getLanguageCode():
    if i18n.doesTextExist('#settings:LANGUAGE_CODE'):
        return i18n.makeString('#settings:LANGUAGE_CODE')
    else:
        return None


def getClientLanguage():
    """
    Return client string of language code
    """
    lng = constants.DEFAULT_LANGUAGE
    try:
        lng = getLanguageCode()
        if lng is None:
            lng = constants.DEFAULT_LANGUAGE
    except Exception:
        LOG_CURRENT_EXCEPTION()

    return lng


def getClientOverride():
    if constants.IS_KOREA:
        return 'KR'
    elif constants.IS_CHINA:
        return 'CN'
    else:
        return None


def getLocalizedData(dataDict, key, defVal = ''):
    resVal = defVal
    if dataDict:
        lng = getClientLanguage()
        localesDict = dataDict.get(key, {})
        if localesDict:
            if lng in localesDict:
                resVal = localesDict[lng]
            elif constants.DEFAULT_LANGUAGE in localesDict:
                resVal = localesDict[constants.DEFAULT_LANGUAGE]
            else:
                resVal = localesDict.items()[0][1]
    return resVal


def int2roman(number):
    """
    Convert arabic number to roman number
    @param number: int - number
    @return: string - roman number
    """
    numerals = {1: 'I',
     4: 'IV',
     5: 'V',
     9: 'IX',
     10: 'X',
     40: 'XL',
     50: 'L',
     90: 'XC',
     100: 'C',
     400: 'CD',
     500: 'D',
     900: 'CM',
     1000: 'M'}
    result = ''
    for value, numeral in sorted(numerals.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value

    return result


def getClientVersion():
    sec = ResMgr.openSection(VERSION_FILE_PATH)
    return sec.readString('version')


def getFullClientVersion():
    sec = ResMgr.openSection(VERSION_FILE_PATH)
    version = i18n.makeString(sec.readString('appname')) + ' ' + sec.readString('version')
    return version


def isShowStartupVideo():
    if not BigWorld.wg_isSSE2Supported():
        return False
    else:
        p = Settings.g_instance.userPrefs
        return p is None or p.readInt(Settings.KEY_SHOW_STARTUP_MOVIE, 1) == 1


def newFakeModel():
    return BigWorld.Model('')


_g_alphabetOrderExcept = {1105: 1077.5,
 1025: 1045.5}

def _getSymOrderIdx(symbol):
    raise type(symbol) is types.UnicodeType or AssertionError
    symIdx = ord(symbol)
    return _g_alphabetOrderExcept.get(symIdx, symIdx)


def strcmp(word1, word2):
    raise type(word1) is types.UnicodeType or AssertionError
    raise type(word2) is types.UnicodeType or AssertionError
    for sym1, sym2 in zip(word1, word2):
        if sym1 != sym2:
            return int(round(_getSymOrderIdx(sym1) - _getSymOrderIdx(sym2)))

    return len(word1) - len(word2)


def setHangarVisibility(isVisible):
    BigWorld.worldDrawEnabled(isVisible)
