# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/birthday_account_settings.py
import typing
from account_helpers import AccountSettings
from mt_birthday.birthday_constants import BirthdayStorageKeys, ACCOUNT_DEFAULT_SETTINGS
if typing.TYPE_CHECKING:
    from typing import Any

def getSettings(name):
    return AccountSettings.getSettings(BirthdayStorageKeys.MT_BIRTHDAY).get(name, ACCOUNT_DEFAULT_SETTINGS[BirthdayStorageKeys.MT_BIRTHDAY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(BirthdayStorageKeys.MT_BIRTHDAY)
    settings[name] = value
    AccountSettings.setSettings(BirthdayStorageKeys.MT_BIRTHDAY, settings)
