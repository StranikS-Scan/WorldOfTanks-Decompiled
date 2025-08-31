# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger_account_settings.py
from typing import TYPE_CHECKING
from account_helpers import AccountSettings
from white_tiger_common.wt_constants import WHITE_TIGER_ACC_SETTINGS_KEY, ACCOUNT_DEFAULT_SETTINGS, WHITE_TIGER_INTRO_VIEWED, WHITE_TIGER_OUTRO_VIDEO_VIEWED
if TYPE_CHECKING:
    from typing import Any

def getSettings(name):
    settings = AccountSettings.getSettings(WHITE_TIGER_ACC_SETTINGS_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[WHITE_TIGER_ACC_SETTINGS_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(WHITE_TIGER_ACC_SETTINGS_KEY)
    settings[name] = value
    AccountSettings.setSettings(WHITE_TIGER_ACC_SETTINGS_KEY, settings)


def isIntroViewed():
    return getSettings(WHITE_TIGER_INTRO_VIEWED)


def setIntroViewed(status):
    return setSettings(WHITE_TIGER_INTRO_VIEWED, status)


def isOutroVideoViewed():
    return getSettings(WHITE_TIGER_OUTRO_VIDEO_VIEWED)


def setOutroVideoViewed(status):
    return setSettings(WHITE_TIGER_OUTRO_VIDEO_VIEWED, status)
