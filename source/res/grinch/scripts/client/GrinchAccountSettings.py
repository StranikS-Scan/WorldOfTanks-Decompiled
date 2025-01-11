# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/GrinchAccountSettings.py
from account_helpers import AccountSettings
_GRINCH_KEY = 'grinch_key'
PRB_HINT_NUM = 'prb_hint_num'
ACCOUNT_DEFAULT_SETTINGS = {_GRINCH_KEY: {PRB_HINT_NUM: 0}}

def getSettings(name):
    settings = AccountSettings.getSettings(_GRINCH_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[_GRINCH_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(_GRINCH_KEY)
    settings[name] = value
    AccountSettings.setSettings(_GRINCH_KEY, settings)
