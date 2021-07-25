# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/players_panel.py
from account_helpers.settings_core.options import VehicleHPInPlayersPanelSetting
from account_helpers.settings_core.settings_constants import GAME, BattleCommStorageKeys
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.battle.shared.formatters import normalizeHealthPercent
from gui.Scaleform.daapi.view.meta.PlayersPanelMeta import PlayersPanelMeta
from gui.Scaleform.genConsts.PLAYERS_PANEL_STATE import PLAYERS_PANEL_STATE
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_PLAYERS_PANEL_STATE_RANGE = (PLAYERS_PANEL_STATE.HIDDEN,
 PLAYERS_PANEL_STATE.SHORT,
 PLAYERS_PANEL_STATE.MEDIUM,
 PLAYERS_PANEL_STATE.LONG,
 PLAYERS_PANEL_STATE.FULL)
PLAYER_PANEL_SETTINGS_TO_HP_STATE = {VehicleHPInPlayersPanelSetting.Options.ALT: PLAYERS_PANEL_STATE.SHOW_HP_ON_ALT,
 VehicleHPInPlayersPanelSetting.Options.ALWAYS: PLAYERS_PANEL_STATE.ALWAYS_SHOW_HP,
 VehicleHPInPlayersPanelSetting.Options.NEVER: PLAYERS_PANEL_STATE.NEVER_SHOW_HP}

def convertSettingToFeatures(value):
    return PLAYER_PANEL_SETTINGS_TO_HP_STATE.get(VehicleHPInPlayersPanelSetting.Options(value), -1)


class PlayerPanelStateSetting(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    @classmethod
    def read(cls):
        state = cls.settingsCore.getSetting(GAME.PLAYERS_PANELS_STATE)
        return state if state in _PLAYERS_PANEL_STATE_RANGE else PLAYERS_PANEL_STATE.MEDIUM

    @classmethod
    def write(cls, state):
        if state in _PLAYERS_PANEL_STATE_RANGE:
            cls.settingsCore.applySetting(GAME.PLAYERS_PANELS_STATE, state)
            return True
        LOG_ERROR('State of players panel is invalid', state)
        return False


class PlayersPanel(IBattleFieldListener, PlayersPanelMeta, IAbstractPeriodView):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self._mode = PLAYERS_PANEL_STATE.SHORT

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        arenaDP = self.sessionProvider.getArenaDP()
        vInfo = arenaDP.getVehicleInfo(vehicleID)
        if vInfo.isObserver():
            return
        if arenaDP.isPlayerObserver():
            isAlly = avatar_getter.getPlayerTeam() == vInfo.team
        else:
            isAlly = arenaDP.isAllyTeam(vInfo.team)
        self.as_setPlayerHPS(isAlly, vehicleID, normalizeHealthPercent(newHealth, maxHealth))

    def tryToSetPanelModeByMouse(self, mode):
        if mode != self._mode and PlayerPanelStateSetting.write(mode):
            self._mode = mode
            self.as_setPanelModeS(mode)

    def switchToOtherPlayer(self, vehicleID):
        aih = avatar_getter.getInputHandler()
        if aih.isAllowToSwitchPositionOrFPV():
            self.guiSessionProvider.shared.viewPoints.selectVehicle(int(vehicleID))

    def setInitialMode(self):
        self._mode = PlayerPanelStateSetting.read()
        self.as_setPanelModeS(self._mode)

    def setLargeMode(self):
        self.as_setPanelModeS(PLAYERS_PANEL_STATE.FULL)

    def _populate(self):
        super(PlayersPanel, self)._populate()
        self.addListener(events.GameEvent.NEXT_PLAYERS_PANEL_MODE, self._handleNextMode, EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
        if self.settingsCore:
            self.settingsCore.onSettingsChanged += self.__onSettingsChanged
            isChatVisible = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST))
            self.as_setChatCommandsVisibilityS(isChatVisible)
            playersHPBarsVisibilitySetting = self.settingsCore.getSetting(GAME.SHOW_VEHICLE_HP_IN_PLAYERS_PANEL)
            self.as_setPanelHPBarVisibilityStateS(convertSettingToFeatures(playersHPBarsVisibilitySetting))

    def _dispose(self):
        self.removeListener(events.GameEvent.NEXT_PLAYERS_PANEL_MODE, self._handleNextMode, EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
        if self.settingsCore:
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(PlayersPanel, self)._dispose()

    def _handleNextMode(self, _):
        mode = (self._mode + 1) % (PLAYERS_PANEL_STATE.FULL + 1)
        if PlayerPanelStateSetting.write(mode):
            self._mode = mode
            self.as_setPanelModeS(mode)

    def __handleShowExtendedInfo(self, event):
        self.as_setOverrideExInfoS(event.ctx['isDown'])

    def __onSettingsChanged(self, diff):
        playersPanelCommEnabled = diff.get(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST)
        if playersPanelCommEnabled is not None:
            self.as_setChatCommandsVisibilityS(bool(playersPanelCommEnabled))
        playersHPBarsVisibleState = diff.get(GAME.SHOW_VEHICLE_HP_IN_PLAYERS_PANEL)
        if playersHPBarsVisibleState is not None:
            self.as_setPanelHPBarVisibilityStateS(convertSettingToFeatures(playersHPBarsVisibleState))
        return
