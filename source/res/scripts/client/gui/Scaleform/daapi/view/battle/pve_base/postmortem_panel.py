# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/postmortem_panel.py
from enum import IntEnum
import BattleReplay
import BigWorld
import WWISE
from TeamInfoLivesComponent import TeamInfoLivesComponent
from gui.Scaleform.daapi.view.meta.PvePostmortemPanelMeta import PvePostmortemPanelMeta
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.respawn_hud import RespawnHUDClientModel
from pve_battle_hud import WidgetType

class LivesState(IntEnum):
    NONE = 1
    HAS_LIVES = 2
    HAS_LOCKED_LIVES = 3
    NO_LIVES = 4


class PvePostmortemPanel(PvePostmortemPanelMeta):
    __slots__ = ('_settings', '_livesState')

    def __init__(self):
        super(PvePostmortemPanel, self).__init__()
        self._settings = None
        self._livesState = LivesState.NONE
        return

    def resetDeathInfo(self):
        super(PvePostmortemPanel, self).resetDeathInfo()
        self._livesState = LivesState.NONE

    def _populate(self):
        super(PvePostmortemPanel, self)._populate()
        if BattleReplay.isPlaying():
            self.as_hidePanelS()
        self._settingsChangeHandler(WidgetType.RESPAWN_HUD)

    def _dispose(self):
        self._settings = None
        super(PvePostmortemPanel, self)._dispose()
        return

    def _addGameListeners(self):
        super(PvePostmortemPanel, self)._addGameListeners()
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged += self._settingsChangeHandler
        teamLives = self._teamLives
        if teamLives is not None:
            teamLives.onTeamLivesUpdated += self._onTeamLivesUpdated
        self.sessionProvider.onBattleSessionStop += self._onBattleSessionStop
        return

    def _removeGameListeners(self):
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged -= self._settingsChangeHandler
        teamLives = self._teamLives
        if teamLives is not None:
            teamLives.onTeamLivesUpdated -= self._onTeamLivesUpdated
        self.sessionProvider.onBattleSessionStop -= self._onBattleSessionStop
        super(PvePostmortemPanel, self)._removeGameListeners()
        return

    def _onBattleSessionStop(self):
        self._livesState = LivesState.NONE

    def _settingsChangeHandler(self, settingsID):
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl is None:
            return
        else:
            if settingsID == WidgetType.RESPAWN_HUD:
                respawnHUDSettings = settingsCtrl.getSettings(WidgetType.RESPAWN_HUD)
                if not respawnHUDSettings:
                    return
                self._settings = respawnHUDSettings
                self._updateLivesState()
            return

    @property
    def _respawnComponent(self):
        vehicleID = BigWorld.player().playerVehicleID
        vehicle = BigWorld.entities.get(vehicleID)
        return vehicle.dynamicComponents.get('VehicleRespawnComponent') if vehicle else None

    @property
    def _teamLives(self):
        return TeamInfoLivesComponent.getInstance()

    def _onTeamLivesUpdated(self):
        self._updateLivesState()

    def _showOwnDeathInfo(self):
        super(PvePostmortemPanel, self)._showOwnDeathInfo()
        self._updateLivesState()

    def _updateLivesState(self):
        isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
        if not self._settings or not self._teamLives or not self._respawnComponent or not isInPostmortem:
            return
        currentState = self._calcCurrentLivesState()
        if self._livesState == currentState:
            return
        if currentState == LivesState.HAS_LIVES and self._currentRespawnDelay <= 0:
            return
        self._applyLivesState(currentState)

    def _calcCurrentLivesState(self):
        teamLives = self._teamLives
        if not teamLives:
            return LivesState.NONE
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        if teamLives.getLives(playerVehicleID) > 0:
            state = LivesState.HAS_LIVES
        elif teamLives.getLockedLives(playerVehicleID) > 0:
            state = LivesState.HAS_LOCKED_LIVES
        else:
            state = LivesState.NO_LIVES
        return state

    def _applyLivesState(self, livesState):
        if not self._settings:
            return
        self._livesState = livesState
        if self._livesState == LivesState.HAS_LIVES:
            self.as_setHintTitleS(self._settings.getDynamicRespawnHeader())
            self.as_setHintDescrS(self._settings.getDynamicRespawnSubheader())
            self.as_setTimerS(self._respawnComponent.delay, self._respawnComponent.delay - self._currentRespawnDelay)
            self._playSound(self._settings.dynamicRespawnSound)
            self.as_setCanExitS(False)
        elif self._livesState == LivesState.HAS_LOCKED_LIVES:
            self.as_setHintTitleS(self._settings.getStaticRespawnHeader())
            self.as_setHintDescrS(self._settings.getStaticRespawnSubheader())
            self.as_showLockedLivesS()
            self._playSound(self._settings.staticRespawnSound)
            self.as_setCanExitS(False)
        elif self._livesState == LivesState.NO_LIVES:
            self.as_setHintTitleS(self._settings.getBattleOverHeader())
            self.as_setHintDescrS(self._settings.getBattleOverSubheader())
            self._playSound(self._settings.battleOverSound)
            self.as_setCanExitS(True)

    @property
    def _currentRespawnDelay(self):
        return round(self._respawnComponent.spawnTime - BigWorld.serverTime())

    @staticmethod
    def _playSound(name):
        if name:
            WWISE.WW_eventGlobal(name)
