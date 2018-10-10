# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/ext/__init__.py
import types
import BigWorld
from helpers import i18n
from gui.Scaleform.locale.MESSENGER import MESSENGER
from external_strings_utils import isAccountNameValid
from external_strings_utils import _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH
import constants
from debug_utils import LOG_ERROR, LOG_DEBUG
from messenger import g_settings
from messenger.ext import dictionaries
from messenger.m_constants import CLIENT_ERROR_ID
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
        if not isinstance(text, types.UnicodeType):
            text = unicode(text, 'utf-8')
        return g_olDictionary.searchAndReplace(text) if g_settings.userPrefs.enableOlFilter else text


def isBattleChatEnabled(common=False):
    result = True
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is None:
        LOG_ERROR('ClientArena not found')
        return result
    else:
        guiType = arena.guiType
        if guiType is None:
            return result
        if guiType in (constants.ARENA_GUI_TYPE.RANDOM, constants.ARENA_GUI_TYPE.RANKED, constants.ARENA_GUI_TYPE.EPIC_RANDOM):
            result = not g_settings.userPrefs.disableBattleChat
        if result and common:
            result = arena.bonusType in (constants.ARENA_BONUS_TYPE.TRAINING, constants.ARENA_BONUS_TYPE.EPIC_RANDOM_TRAINING)
        return result


def validateAccountName(name):
    if not name:
        return (False, CLIENT_ERROR_ID.NAME_EMPTY)
    else:
        return (False, CLIENT_ERROR_ID.NAME_INVALID) if not isAccountNameValid(name) else (True, None)


def checkAccountName(token):
    result, reason = validateAccountName(token)
    if reason == CLIENT_ERROR_ID.NAME_EMPTY:
        reason = i18n.makeString(MESSENGER.CLIENT_WARNING_EMPTYUSERSEARCHTOKEN_MESSAGE)
    elif reason == CLIENT_ERROR_ID.NAME_INVALID:
        reason = i18n.makeString(MESSENGER.CLIENT_WARNING_INVALIDUSERSEARCHTOKEN_MESSAGE, _ACCOUNT_NAME_MIN_LENGTH, _ACCOUNT_NAME_MAX_LENGTH)
    return (result, reason)


def isSenderIgnored(user):
    return isNotFriendSenderIgnored(user, g_settings.userPrefs.invitesFromFriendsOnly)


def isNotFriendSenderIgnored(user, areFriendsOnly):
    if user:
        if areFriendsOnly:
            if user.isFriend():
                return False
            LOG_DEBUG('Invite is ignored, shows invites from friends only', user)
            return True
        if user.isIgnored():
            LOG_DEBUG('Invite is ignored, there is the contact in ignore list', user)
            return True
    elif areFriendsOnly:
        LOG_DEBUG('Invite is ignored, shows invites from friends only', user)
    return areFriendsOnly
