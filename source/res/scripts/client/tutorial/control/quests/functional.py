# Embedded file name: scripts/client/tutorial/control/quests/functional.py
import copy
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core.SettingsCore import g_settingsCore
from tutorial.control.functional import FunctionalEffect, FunctionalShowWindowEffect, FunctionalRunTriggerEffect
from tutorial.logger import LOG_ERROR

class SaveTutorialSettingEffect(FunctionalEffect):

    def triggerEffect(self):
        setting = self.getTarget()
        if setting is None:
            LOG_ERROR('Tutorial setting is not found', self._effect.getTargetID())
            return
        else:
            g_settingsCore.serverSettings.setTutorialSetting({setting.getSettingName(): setting.getSettingValue()})
            return


class SaveAccountSettingEffect(FunctionalEffect):

    def triggerEffect(self):
        setting = self.getTarget()
        if setting is None:
            LOG_ERROR('Tutorial setting is not found', self._effect.getTargetID())
            return
        else:
            AccountSettings.setSettings(setting.getSettingName(), setting.getSettingValue())
            return


class ShowSharedWindowEffect(FunctionalShowWindowEffect):

    def _setActions(self, window):
        self._tutorial.getFunctionalScene().setActions(copy.deepcopy(window.getActions()))


class QuestsFunctionalRunTriggerEffect(FunctionalRunTriggerEffect):

    def isInstantaneous(self):
        return True
