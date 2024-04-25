# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/player_lives.py
import logging
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.meta.HBPlayerLivesMeta import HBPlayerLivesMeta
from TeamInfoLivesComponent import TeamInfoLivesComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class HistoricalBattlesPlayerLives(HBPlayerLivesMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(HistoricalBattlesPlayerLives, self)._populate()
        TeamInfoLivesComponent.onTeamLivesUpdated += self.__onRespawnLivesUpdated
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__update()
        return

    def _dispose(self):
        TeamInfoLivesComponent.onTeamLivesUpdated -= self.__onRespawnLivesUpdated
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(HistoricalBattlesPlayerLives, self)._dispose()
        return

    @property
    def _teamLivesComponent(self):
        return BigWorld.player().arena.teamInfo.dynamicComponents.get('teamLivesComponent')

    def __onRespawnLivesUpdated(self):
        self.__update()

    def __update(self, playerVehicleID=None):
        if not playerVehicleID:
            playerVehicleID = avatar_getter.getPlayerVehicleID()
        teamLivesComponent = self._teamLivesComponent
        if not teamLivesComponent:
            _logger.error('[HistoricalBattlesPlayerLives] No teamLivesComponent!')
            return
        playerLives = teamLivesComponent.getLives(playerVehicleID)
        playerDeath = teamLivesComponent.getUsedLives(playerVehicleID)
        lockedLives = teamLivesComponent.getLockedLives(playerVehicleID)
        self.as_setCountLivesS(playerLives, playerDeath, lockedLives)

    def __onVehicleStateUpdated(self, state, vehicleID):
        if state == VEHICLE_VIEW_STATE.PLAYER_INFO:
            self.__update(vehicleID)
