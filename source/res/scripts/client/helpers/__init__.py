# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/__init__.py
import types
import BigWorld
import ResMgr
import Settings
import i18n
import constants
from debug_utils import LOG_CURRENT_EXCEPTION
from soft_exception import SoftException
VERSION_FILE_PATH = '../version.xml'

def gEffectsDisabled():
    return False


def isPlayerAccount():
    return hasattr(BigWorld.player(), 'databaseID')


def isPlayerAvatar():
    return hasattr(BigWorld.player(), 'arena')


def getLanguageCode():
    return i18n.makeString('#settings:LANGUAGE_CODE') if i18n.doesTextExist('#settings:LANGUAGE_CODE') else None


def getClientLanguage():
    lng = constants.DEFAULT_LANGUAGE
    try:
        lng = getLanguageCode()
        if lng is None:
            lng = constants.DEFAULT_LANGUAGE
    except Exception:
        LOG_CURRENT_EXCEPTION()

    return lng


def getClientOverride():
    if constants.IS_CHINA:
        return 'CN'
    else:
        return 'KR' if getClientLanguage() == 'ko' else None


def getLocalizedData(dataDict, key, defVal=''):
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


def getShortClientVersion():
    sec = ResMgr.openSection(VERSION_FILE_PATH)
    return sec.readString('version').split('#')[0]


def getFullClientVersion():
    sec = ResMgr.openSection(VERSION_FILE_PATH)
    version = i18n.makeString(sec.readString('appname')) + ' ' + sec.readString('version')
    return version


def isShowStartupVideo():
    from gui import GUI_SETTINGS
    if not GUI_SETTINGS.guiEnabled:
        return False
    else:
        p = Settings.g_instance.userPrefs
        if p is not None:
            if p.readInt(Settings.KEY_SHOW_STARTUP_MOVIE, 1) == 1:
                if GUI_SETTINGS.compulsoryIntroVideos:
                    return True
                return isIntroVideoSettingChanged(p)
            return False
        return True


def isIntroVideoSettingChanged(userPrefs=None):
    userPrefs = userPrefs if userPrefs is not None else Settings.g_instance.userPrefs
    import account_shared
    mainVersion = account_shared.getClientMainVersion()
    lastVideoVersion = userPrefs.readString(Settings.INTRO_VIDEO_VERSION, '')
    return lastVideoVersion != mainVersion


def writeIntroVideoSetting():
    userPrefs = Settings.g_instance.userPrefs
    if userPrefs is not None:
        import account_shared
        userPrefs.writeString(Settings.INTRO_VIDEO_VERSION, account_shared.getClientMainVersion())
    return


def newFakeModel():
    return BigWorld.Model('')


_g_alphabetOrderExcept = {1105: 1077.5,
 1025: 1045.5,
 197: 196,
 196: 197,
 229: 228,
 228: 229,
 1030: 1048,
 1110: 1080,
 1028: 1045.5,
 1108: 1077.5}

def _getSymOrderIdx(symbol):
    if not isinstance(symbol, types.UnicodeType):
        raise SoftException('')
    symIdx = ord(symbol)
    return _g_alphabetOrderExcept.get(symIdx, symIdx)


def strcmp(word1, word2):
    if not isinstance(word1, types.UnicodeType):
        raise SoftException('First argument should be unicode')
    if not isinstance(word2, types.UnicodeType):
        raise SoftException('Second argument should be unicode')
    for sym1, sym2 in zip(word1, word2):
        if sym1 != sym2:
            return int(round(_getSymOrderIdx(sym1) - _getSymOrderIdx(sym2)))

    return len(word1) - len(word2)


def setHangarVisibility(isVisible):
    BigWorld.worldDrawEnabled(isVisible)


def getHelperServicesConfig(manager):
    from helpers.statistics import StatisticsCollector
    from skeletons.helpers.statistics import IStatisticsCollector
    collector = StatisticsCollector()
    collector.init()
    manager.addInstance(IStatisticsCollector, collector, finalizer='fini')


class ReferralButtonHandler(object):

    @classmethod
    def invoke(cls, **kwargs):
        from gui.shared.event_dispatcher import showReferralProgramWindow
        from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL
        value = kwargs.get('value', None)
        url = value.get('action_url', None) if isinstance(value, dict) else None
        url = getReferralProgramURL() + url
        showReferralProgramWindow(url)
        return
