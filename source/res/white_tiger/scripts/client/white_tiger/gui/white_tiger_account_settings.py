# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/white_tiger_account_settings.py
from account_helpers import AccountSettings

class AccountSettingsKeys(object):
    EVENT_KEY = 'wt_keys'
    WT_BATTLES_DONE_HUNTER = 'wtBattlesDoneHunter'
    WT_BATTLES_DONE_BOSS = 'wtBattlesDoneBoss'
    WT_LAST_SEEN_STAMPS = 'wtLastSeenStamp'
    WT_LAST_SEEN_TICKETS = 'wtLastSeenTickets'
    WT_LAST_SEEN_LEVEL = 'wtLastSeenLevel'
    WT_PROGRESSION_QUESTS_TAB = 'wtProgressionQuestsTab'
    WT_SEEN_WELCOME_SCREEN = 'wtWelcomeScreenSeen'
    WT_BANNER_SEEN = 'wtBannerSeen'


class AccountFavoriteKeys(object):
    WHITE_TIGER_VEHICLE = 'WHITE_TIGER_VEHICLE'


ACCOUNT_DEFAULT_SETTINGS = {AccountSettingsKeys.EVENT_KEY: {AccountSettingsKeys.WT_BATTLES_DONE_HUNTER: 0,
                                 AccountSettingsKeys.WT_BATTLES_DONE_BOSS: 0,
                                 AccountSettingsKeys.WT_LAST_SEEN_STAMPS: 0,
                                 AccountSettingsKeys.WT_LAST_SEEN_TICKETS: 0,
                                 AccountSettingsKeys.WT_SEEN_WELCOME_SCREEN: False}}
ACCOUNT_DEFAULT_FAVORITES = {AccountFavoriteKeys.WHITE_TIGER_VEHICLE: 0}

def getSettings(name):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[AccountSettingsKeys.EVENT_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    settings[name] = value
    AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)


def getWTFavorites():
    return AccountSettings.getFavorites(AccountFavoriteKeys.WHITE_TIGER_VEHICLE)


def setWTFavorites(value):
    favorites = AccountSettings.getFavorites(AccountFavoriteKeys.WHITE_TIGER_VEHICLE)
    if value != favorites:
        AccountSettings.setFavorites(AccountFavoriteKeys.WHITE_TIGER_VEHICLE, value)


def isWelcomeScreenSeen():
    return getSettings(AccountSettingsKeys.WT_SEEN_WELCOME_SCREEN)


def setWelcomeScreenSeen(seen=True):
    return setSettings(AccountSettingsKeys.WT_SEEN_WELCOME_SCREEN, seen)


def isBannerSeen():
    return getSettings(AccountSettingsKeys.WT_BANNER_SEEN)


def setBannerSeen(seen=True):
    return setSettings(AccountSettingsKeys.WT_BANNER_SEEN, seen)
