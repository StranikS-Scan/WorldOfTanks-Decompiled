# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/account_settings_helper.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class AccountSettingsHelper(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    @classmethod
    def welcomeScreenShown(cls):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = cls.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        settings[GuiSettingsBehavior.CREW_LAMP_WELCOME_SCREEN_SHOWN] = True
        cls.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)
