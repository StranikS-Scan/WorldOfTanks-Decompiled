# Embedded file name: scripts/client/messenger/ext/__init__.py
import types
import BigWorld
from helpers import i18n
from gui.Scaleform.locale.MESSENGER import MESSENGER
from external_strings_utils import isAccountNameValid
from external_strings_utils import _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH
import constants
from debug_utils import LOG_ERROR
from messenger import g_settings
from messenger.ext import dictionaries
MESSENGER_OLDICT_FILE_PATH = 'text/messenger_oldictionary.xml'
MESSENGER_DOMAIN_FILE_PATH = 'text/messenger_dndictionary.xml'
g_dnDictionary = dictionaries.DomainNameDictionary.load(MESSENGER_DOMAIN_FILE_PATH)
if constants.SPECIAL_OL_FILTER:
    g_olDictionary = dictionaries.SpecialOLDictionary.load(MESSENGER_OLDICT_FILE_PATH)
else:
    g_olDictionary = dictionaries.BasicOLDictionary.load(MESSENGER_OLDICT_FILE_PATH)

def passCensor(text):
    if text is None:
        return u''
    else:
        if type(text) is not types.UnicodeType:
            text = unicode(text, 'utf-8')
        if g_settings.userPrefs.enableOlFilter:
            return g_olDictionary.searchAndReplace(text)
        return text


def isBattleChatEnabled():
    result = True
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is None:
        LOG_ERROR('ClientArena not found')
        return result
    else:
        guiType = arena.guiType
        if guiType is None:
            return result
        if guiType == constants.ARENA_GUI_TYPE.RANDOM:
            result = not g_settings.userPrefs.disableBattleChat
        return result


def getMinimapCellName(cellIdx):
    from gui.WindowsManager import g_windowsManager
    battleWindow = g_windowsManager.battleWindow
    if battleWindow:
        cellName = battleWindow.minimap.getCellName(cellIdx)
    else:
        cellName = 'N/A'
    return cellName


def checkAccountName(token):
    if not len(token):
        reason = i18n.makeString(MESSENGER.CLIENT_WARNING_EMPTYUSERSEARCHTOKEN_MESSAGE)
        return (False, reason)
    elif not isAccountNameValid(token):
        reason = i18n.makeString(MESSENGER.CLIENT_WARNING_INVALIDUSERSEARCHTOKEN_MESSAGE, _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH)
        return (False, reason)
    else:
        return (True, None)
