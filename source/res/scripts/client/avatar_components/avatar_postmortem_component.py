# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/avatar_postmortem_component.py
import BattleReplay
import logging
from AvatarInputHandler.control_modes import PostMortemControlMode
from account_helpers.settings_core.settings_constants import GAME
from aih_constants import CTRL_MODE_NAME
from helpers import dependency
from constants import POSTMORTEM_MODIFIERS, DEFAULT_POSTMORTEM_SETTINGS, ARENA_BONUS_TYPE
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_TRAJECTORY_PROGRESS_DELAY = 0.1
_logger = logging.getLogger(__name__)

class SimulatedVehicleType(object):
    VEHICLE = 'vehicle'
    PLAYER = 'player'
    ATTACKER = 'attacker'


class AvatarPostmortemComponent(object):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def deadOnReconnection(self):
        return self.__deadOnReconnection

    @deadOnReconnection.setter
    def deadOnReconnection(self, value):
        self.__deadOnReconnection = value

    def __init__(self):
        super(AvatarPostmortemComponent, self).__init__()
        self._currentGameModeSettings = None
        self.__deadOnReconnection = False
        self.__isSimpleDeathCam = False
        return

    def onBecomePlayer(self):
        self.__setGameMode()
        self.__deadOnReconnection = False

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomeNonPlayer(self):
        self.settingsCore.serverSettings.settingsCache.onSyncCompleted -= self.__onSettingsSyncCompleted
        self.destroy()

    def canSwitchToAllyVehicle(self):
        return False if self.arenaBonusType in (ARENA_BONUS_TYPE.EPIC_BATTLE,) else True

    def isPostmortemFeatureEnabled(self, feature):
        if feature not in CTRL_MODE_NAME.POSTMORTEM_CONTROL_MODES:
            _logger.error('Feature: {} is not defined as a KILL_CAM_FEATURES')
            return False
        if feature is CTRL_MODE_NAME.POSTMORTEM:
            return True
        isFeatureEnabled = self._currentGameModeSettings.get(feature, False)
        _logger.debug('Game mode: %s feature: %s is enabled: %s', self._currentGameModeSettings, feature, isFeatureEnabled)
        return isFeatureEnabled

    def isPostmortemModificationActive(self, feature, constraint):
        if feature not in CTRL_MODE_NAME.POSTMORTEM_CONTROL_MODES or constraint not in POSTMORTEM_MODIFIERS.ALL:
            _logger.error('Feature: %s or constrain: %s are not defined correctly', feature, constraint)
            return False
        modifierName = feature + 'Modifiers'
        modifierList = self._currentGameModeSettings.get(modifierName, '')
        isModifierEnabled = constraint in modifierList
        _logger.debug('Game mode: %s modifier: %s is enabled: %s', self._currentGameModeSettings, feature, isModifierEnabled)
        return isModifierEnabled

    def destroy(self):
        self._currentGameModeSettings = None
        return

    def getNextControlMode(self):
        currentControlMode = self.inputHandler.ctrlModeName
        isReplay = BattleReplay.g_replayCtrl.isTimeWarpInProgress
        if currentControlMode not in CTRL_MODE_NAME.POSTMORTEM_CONTROL_MODES:
            if isReplay or self.deadOnReconnection or not self._guiSessionProvider.shared.killCamCtrl:
                return CTRL_MODE_NAME.POSTMORTEM
            if self.isPostmortemFeatureEnabled(CTRL_MODE_NAME.LOOK_AT_KILLER):
                return CTRL_MODE_NAME.LOOK_AT_KILLER
        if self.isPostmortemFeatureEnabled(CTRL_MODE_NAME.KILL_CAM) and (currentControlMode is CTRL_MODE_NAME.LOOK_AT_KILLER or currentControlMode not in CTRL_MODE_NAME.POSTMORTEM_CONTROL_MODES):
            return CTRL_MODE_NAME.KILL_CAM
        if currentControlMode in (CTRL_MODE_NAME.KILL_CAM, CTRL_MODE_NAME.DEATH_FREE_CAM):
            return CTRL_MODE_NAME.POSTMORTEM
        if currentControlMode == CTRL_MODE_NAME.POSTMORTEM:
            if self.isPostmortemFeatureEnabled(CTRL_MODE_NAME.DEATH_FREE_CAM):
                return CTRL_MODE_NAME.DEATH_FREE_CAM
        return CTRL_MODE_NAME.POSTMORTEM

    def isSimpleDeathCam(self):
        return self.__isSimpleDeathCam

    def __setGameMode(self):
        postmortemSettings = self.arenaExtraData.get('postmortemSettings', None)
        if postmortemSettings is None:
            self._currentGameModeSettings = DEFAULT_POSTMORTEM_SETTINGS
        else:
            self._currentGameModeSettings = postmortemSettings.get('gamemode', {})
        self.__applyPostMortemSettings()
        return

    def __applyPostMortemSettings(self):
        from account_helpers.settings_core.options import PostMortemModeSetting
        if self.settingsCore.serverSettings.settingsCache.isSynced():
            postMortemSettingValue = self.settingsCore.getSetting(GAME.POSTMORTEM_MODE)
            isSimplifiedDeathCam = postMortemSettingValue == PostMortemModeSetting.POST_MORTEM_MODES.index(PostMortemModeSetting.OPTIONS.SIMPLE)
            showDeathCam = postMortemSettingValue == PostMortemModeSetting.POST_MORTEM_MODES.index(PostMortemModeSetting.OPTIONS.ANALYSIS) or isSimplifiedDeathCam
            showKillerVision = postMortemSettingValue != PostMortemModeSetting.POST_MORTEM_MODES.index(PostMortemModeSetting.OPTIONS.SELF)
            self.cell.setSendKillCamSimulationData(showDeathCam)
            self.__isSimpleDeathCam = isSimplifiedDeathCam
            PostMortemControlMode.setIsPostmortemDelayEnabled(showKillerVision)
            if self.isPostmortemFeatureEnabled(CTRL_MODE_NAME.KILL_CAM):
                _logger.debug('Switching %s feature to %s', CTRL_MODE_NAME.KILL_CAM, showDeathCam)
                self._currentGameModeSettings[CTRL_MODE_NAME.KILL_CAM] = showDeathCam
        else:
            self.settingsCore.serverSettings.settingsCache.onSyncCompleted += self.__onSettingsSyncCompleted

    def __onSettingsSyncCompleted(self):
        self.settingsCore.serverSettings.settingsCache.onSyncCompleted -= self.__onSettingsSyncCompleted
        self.__applyPostMortemSettings()
