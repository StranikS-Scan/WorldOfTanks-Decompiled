# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory_personality.py
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from museum_of_glory.cgf.museum_entry_manager import initMuseumOfGloryMarker
from museum_of_glory.dependency.registrator import registerMuseumOfGloryPersonality
from museum_of_glory.museum_of_glory_constants import ACCOUNT_DEFAULT_SETTINGS

def preInit():
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    registerMuseumOfGloryPersonality()
    initMuseumOfGloryMarker()


def init():
    pass


def start():
    pass


def fini():
    pass
