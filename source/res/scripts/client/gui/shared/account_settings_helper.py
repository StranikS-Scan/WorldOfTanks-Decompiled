# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/account_settings_helper.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCore

class WelcomeScreen(CONST_CONTAINER):
    CREW_22_WELCOME = 'crew22Welcome'


class AccountSettingsHelper(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    @classmethod
    def welcomeScreenShown(cls, screen):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = cls.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        settings[screen] = True
        cls.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)

    @classmethod
    def isWelcomeScreenShown(cls, screen):
        settingsCore = dependency.instance(ISettingsCore)
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        return settings.get(screen, False)
