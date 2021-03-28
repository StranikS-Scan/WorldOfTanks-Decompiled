# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/SettingsParams.py
from itertools import chain
import BigWorld
from account_helpers.settings_core import settings_constants, options
from gui.shared.utils import graphics
from gui.shared.utils.monitor_settings import g_monitorSettings
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
_DEFERRED_RENDER_IDX = 0

class SettingsParams(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __settingsDiffPreprocessing(self, diff):
        for option in chain(settings_constants.FEEDBACK.ALL(), (settings_constants.AIM.SPG,)):
            feedbackTab = diff.pop(option, None)
            if feedbackTab is not None:
                diff.update(feedbackTab)

        return diff

    def getGameSettings(self):
        return self.settingsCore.packSettings(settings_constants.GAME.ALL() + settings_constants.BattleCommStorageKeys.ALL())

    def getSoundSettings(self):
        return self.settingsCore.packSettings(settings_constants.SOUND.ALL())

    def getGraphicsSettings(self):
        return self.settingsCore.packSettings(settings_constants.GRAPHICS.ALL())

    def getMarkersSettings(self):
        return self.settingsCore.packSettings(settings_constants.MARKERS.ALL())

    def getFeedbackSettings(self):
        return {settings_constants.FEEDBACK.DAMAGE_LOG: self.getDamageLogSettings(),
         settings_constants.FEEDBACK.DAMAGE_INDICATOR: self.getDamageIndicatorSettings(),
         settings_constants.FEEDBACK.BATTLE_EVENTS: self.getBattleEventsSettings(),
         settings_constants.FEEDBACK.BATTLE_BORDER_MAP: self.getBattleBorderMapSettings(),
         settings_constants.FEEDBACK.QUESTS_PROGRESS: self.getQuestsProgressAndScorePanelSettings()}

    def getOtherSettings(self):
        return self.settingsCore.packSettings(settings_constants.OTHER.ALL())

    def getDamageLogSettings(self):
        return self.settingsCore.packSettings(settings_constants.DAMAGE_LOG.ALL())

    def getDamageIndicatorSettings(self):
        return self.settingsCore.packSettings(settings_constants.DAMAGE_INDICATOR.ALL())

    def getBattleEventsSettings(self):
        return self.settingsCore.packSettings(settings_constants.BATTLE_EVENTS.ALL())

    def getBattleBorderMapSettings(self):
        return self.settingsCore.packSettings(settings_constants.BATTLE_BORDER_MAP.ALL())

    def getQuestsProgressAndScorePanelSettings(self):
        settings = self.settingsCore.packSettings(settings_constants.QUESTS_PROGRESS.ALL() + settings_constants.ScorePanelStorageKeys.ALL())
        settings['allowQuestProgress'] = self.lobbyContext.getServerSettings().isPMBattleProgressEnabled()
        return settings

    def getAimSettings(self):
        settings = {settings_constants.AIM.SPG: self.settingsCore.packSettings(settings_constants.SPGAim.ALL())}
        settings.update(self.settingsCore.packSettings(settings_constants.AIM.ALL()))
        return settings

    def getControlsSettings(self):
        return self.settingsCore.packSettings(settings_constants.CONTROLS.ALL())

    def getMonitorSettings(self):
        return self.settingsCore.packSettings(settings_constants.GRAPHICS.getScreenConstants())

    def preview(self, settingName, value):
        if settingName in chain(settings_constants.FEEDBACK.ALL(), (settings_constants.AIM.SPG,)):
            settingName, value = value.popitem()
        self.settingsCore.previewSetting(settingName, value)

    def revert(self):
        self.settingsCore.revertSettings()
        self.settingsCore.clearStorages()

    def apply(self, diff, restartApproved):
        diff = self.__settingsDiffPreprocessing(diff)
        applyMethod = self.getApplyMethod(diff)
        self.settingsCore.applySettings(diff)
        confirmators = self.settingsCore.applyStorages(restartApproved)
        self.settingsCore.confirmChanges(confirmators)
        if set(graphics.GRAPHICS_SETTINGS.ALL()) & set(diff.keys()):
            BigWorld.commitPendingGraphicsSettings()
        self.settingsCore.clearStorages()
        return applyMethod == options.APPLY_METHOD.RESTART

    def getApplyMethod(self, diff):
        newMonitorIndex = diff.get(settings_constants.GRAPHICS.MONITOR, g_monitorSettings.activeMonitor)
        nextVideoMode = diff.get(settings_constants.GRAPHICS.VIDEO_MODE, g_monitorSettings.windowMode)
        requiresNextBattle = False
        havokSetting = diff.get('HAVOK_ENABLED', None)
        if havokSetting is not None:
            if havokSetting:
                requiresNextBattle = not BigWorld.wg_isDestrCanBeActivated()
        restartNeeded = nextVideoMode == BigWorld.WindowModeExclusiveFullscreen and newMonitorIndex != g_monitorSettings.noRestartExclusiveFullscreenMonitorIndex
        if restartNeeded:
            method = options.APPLY_METHOD.RESTART
        elif requiresNextBattle:
            method = options.APPLY_METHOD.NEXT_BATTLE
        else:
            method = options.APPLY_METHOD.NORMAL
        return options.highestPriorityMethod((method, self.settingsCore.getApplyMethod(diff)))
