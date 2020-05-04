# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/player_lives.py
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.meta.EventPlayerLivesMeta import EventPlayerLivesMeta
from game_event_getter import GameEventGetterMixin

class EventPlayerLives(EventPlayerLivesMeta, GameEventGetterMixin):

    def _populate(self):
        super(EventPlayerLives, self)._populate()
        self.teammateLifecycle.onUpdated += self.__onRespawnLivesUpdated
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__update()
        return

    def _dispose(self):
        self.teammateLifecycle.onUpdated -= self.__onRespawnLivesUpdated
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(EventPlayerLives, self)._dispose()
        return

    def __onRespawnLivesUpdated(self):
        self.__update()

    def __update(self, playerVehicleID=None):
        if not playerVehicleID:
            playerVehicleID = avatar_getter.getPlayerVehicleID()
        teammateLifecycleData = self.teammateLifecycle.getParams()
        playerData = teammateLifecycleData.get(playerVehicleID, {})
        maxLivesLimit = teammateLifecycleData.get('maxLivesLimit', 0)
        playerLives = playerData.get('lives', 0)
        playerDeath = playerData.get('death', 0)
        lockedLives = maxLivesLimit - playerLives - playerDeath
        self.as_setCountLivesS(playerLives, playerDeath, lockedLives)

    def __onVehicleStateUpdated(self, state, vehicleID):
        if state == VEHICLE_VIEW_STATE.PLAYER_INFO:
            self.__update(vehicleID)
