# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/fun_account_settings.py
from __future__ import absolute_import
import copy
from typing import TYPE_CHECKING
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS
from fun_random.gui.fun_gui_constants import AccountSettingsConstants, ACCOUNT_SUBMODE_DEFAULT_SETTINGS
if TYPE_CHECKING:
    from typing import Any

class FunAccountSettings(object):

    @staticmethod
    def _getSettings():
        return AccountSettings.getSettings(AccountSettingsConstants.FUN_RANDOM_ACCOUNT_SETTINGS) or {}

    @staticmethod
    def _setSettings(settings):
        AccountSettings.setSettings(AccountSettingsConstants.FUN_RANDOM_ACCOUNT_SETTINGS, settings)

    @classmethod
    def getIsTriggerCompletionSeen(cls, triggerID):
        settings = cls._getSettings()
        return settings.get(AccountSettingsConstants.FUN_RANDOM_SEEN_TRIGGERS_COMPLETION, {}).get(triggerID, False)

    @classmethod
    def setIsTriggerCompletionSeen(cls, triggerID, isSeen):
        settings = cls._getSettings()
        settings.setdefault(AccountSettingsConstants.FUN_RANDOM_SEEN_TRIGGERS_COMPLETION, {})[triggerID] = isSeen
        cls._setSettings(settings)


class FunSubModeAccountSettings(object):

    def __init__(self, subModeKey):
        self.subModeKey = subModeKey

    def getSettings(self, name):
        defaultValue = ACCOUNT_SUBMODE_DEFAULT_SETTINGS.get(name)
        settings = AccountSettings.getSettings(AccountSettingsConstants.FUN_RANDOM_ACCOUNT_SETTINGS) or {}
        return settings.get(self.subModeKey, {}).get(name, defaultValue)

    def setSettings(self, name, value):
        settings = AccountSettings.getSettings(AccountSettingsConstants.FUN_RANDOM_ACCOUNT_SETTINGS) or {}
        settings.setdefault(self.subModeKey, {})[name] = value
        AccountSettings.setSettings(AccountSettingsConstants.FUN_RANDOM_ACCOUNT_SETTINGS, settings)

    def isInfoPageShown(self):
        return self.getSettings(AccountSettingsConstants.FUN_RANDOM_INFO_PAGE_SHOWN)

    def setInfoPageShown(self, status):
        return self.setSettings(AccountSettingsConstants.FUN_RANDOM_INFO_PAGE_SHOWN, status)


def setSubModeDefaultSettings(subModeKey):
    settings = AccountSettings.getSettingsDefault(AccountSettingsConstants.FUN_RANDOM_ACCOUNT_SETTINGS) or {}
    settings[subModeKey] = copy.deepcopy(ACCOUNT_SUBMODE_DEFAULT_SETTINGS)
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, {AccountSettingsConstants.FUN_RANDOM_ACCOUNT_SETTINGS: settings})
