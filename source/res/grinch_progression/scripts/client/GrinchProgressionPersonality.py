# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/GrinchProgressionPersonality.py
from grinch_progression import initProgression
from GrinchProgressionAccountSettings import ACCOUNT_DEFAULT_SETTINGS
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS
from grinch_progression.account_helpers.account_settings import extendAccountSettings

def preInit():
    initProgression()


def init():
    extendAccountSettings()
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)


def start():
    pass


def fini():
    pass
