# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/epic_mode_controller.py
import BigWorld
from account_helpers.settings_core.settings_constants import GAME
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from helpers.statistics import HARDWARE_SCORE_PARAMS
from skeletons.gui.game_control import IEpicModeController
from debug_utils import LOG_DEBUG
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_RESTRICED_PRESET_NAMES = ['MIN']
_VIRTUAL_MEMORY_LIMIT = 2048

class EpicModeController(IEpicModeController):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        pass

    def init(self):
        pass

    def fini(self):
        pass

    def onLobbyInited(self, ctx):
        validateEpicRandom = self.__checkForEpicRandomValidation()
        if validateEpicRandom:
            self.__validateEpicRandomUsage()

    def onConnected(self):
        self.settingsCore.onSettingsApplied += self.__onSettingsApplied

    def onDisconnected(self):
        self.settingsCore.onSettingsApplied -= self.__onSettingsApplied

    def __onSettingsApplied(self, diff):
        containsEpic = GAME.GAMEPLAY_EPIC_STANDARD in diff
        containsDomination = GAME.GAMEPLAY_DOMINATION in diff
        if containsDomination or containsEpic:
            self.__checkForEpicDominationValidation()
        if self.__checkForEpicRandomValidation():
            if containsEpic:
                filters = self.__getFilters()
                filters['isEpicRandomCheckboxClicked'] = True
                self.__setFilters(filters)

    def __checkForEpicRandomValidation(self):
        filters = self.__getFilters()
        isEpicRandomCheckboxClicked = filters['isEpicRandomCheckboxClicked']
        return not isEpicRandomCheckboxClicked

    def __checkForEpicDominationValidation(self):
        epicCtfEnabled = self.settingsCore.getSetting(GAME.GAMEPLAY_EPIC_STANDARD)
        dominationEnabled = self.settingsCore.getSetting(GAME.GAMEPLAY_DOMINATION)
        self.settingsCore.applySetting(GAME.GAMEPLAY_EPIC_DOMINATION, epicCtfEnabled and dominationEnabled)

    def __getFilters(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)

    def __setFilters(self, filters):
        self.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, filters)

    def __validateEpicRandomUsage(self):
        recomPreset = BigWorld.detectGraphicsPresetFromSystemSettings()
        currentVirtualMemory = BigWorld.getAutoDetectGraphicsSettingsScore(HARDWARE_SCORE_PARAMS.PARAM_VIRTUAL_MEMORY)
        epicCtfEnabled = self.settingsCore.getSetting(GAME.GAMEPLAY_EPIC_STANDARD)
        settingsChanged = False
        restriced = False
        for name in _RESTRICED_PRESET_NAMES:
            presetId = BigWorld.getSystemPerformancePresetIdFromName(name)
            if presetId == recomPreset:
                restriced = True

        if restriced or currentVirtualMemory <= _VIRTUAL_MEMORY_LIMIT:
            if epicCtfEnabled:
                self.settingsCore.applySetting(GAME.GAMEPLAY_EPIC_STANDARD, False)
                self.settingsCore.applySetting(GAME.GAMEPLAY_EPIC_DOMINATION, False)
                settingsChanged = True
        elif not epicCtfEnabled:
            self.settingsCore.applySetting(GAME.GAMEPLAY_EPIC_STANDARD, True)
            dominationEnabled = self.settingsCore.getSetting(GAME.GAMEPLAY_DOMINATION)
            self.settingsCore.applySetting(GAME.GAMEPLAY_EPIC_DOMINATION, dominationEnabled)
            settingsChanged = True
        LOG_DEBUG('epicCtfEnabled ', epicCtfEnabled, 'recomPreset = ', recomPreset, ' virtualMemory = ', currentVirtualMemory, 'settingsShouldChanged ', settingsChanged)
        if settingsChanged:
            confirmators = self.settingsCore.applyStorages(False)
            self.settingsCore.confirmChanges(confirmators)
            self.settingsCore.clearStorages()
