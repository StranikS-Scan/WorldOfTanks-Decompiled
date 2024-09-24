# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/account_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_NOTIFICATIONS
from tech_tree_trade_in_common.tech_tree_trade_in_constants import EVENT_NAME
_IS_TECH_TREE_TRADE_IN_INTRO_VIEWED = 'isTechTreeTradeInIntroViewed'
_DEFAULT_SETTINGS = {EVENT_NAME: {_IS_TECH_TREE_TRADE_IN_INTRO_VIEWED: False}}

def init():
    AccountSettings.overrideDefaultSettings(KEY_NOTIFICATIONS, _DEFAULT_SETTINGS)


def isTechTreeTradeInIntroViewed():
    return AccountSettings.getNotifications(EVENT_NAME)[_IS_TECH_TREE_TRADE_IN_INTRO_VIEWED]


def setTechTreeTradeInIntroViewed():
    settings = AccountSettings.getNotifications(EVENT_NAME)
    settings[_IS_TECH_TREE_TRADE_IN_INTRO_VIEWED] = True
    AccountSettings.setNotifications(EVENT_NAME, settings)
