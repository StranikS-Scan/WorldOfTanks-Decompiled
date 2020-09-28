# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/reinforcement_panel.py
from gui.Scaleform.daapi.view.meta.WTReinforcementPanelMeta import WTReinforcementPanelMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class WTReinforcementPanel(WTReinforcementPanelMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WTReinforcementPanel, self).__init__()
        self.__currentVehicleID = None
        return

    def _populate(self):
        super(WTReinforcementPanel, self)._populate()
        ctrl = self.__sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onTeammatesRespawnLivesUpdated += self.__onTeamsRespawnLivesUpdated
        vehState = self.__sessionProvider.shared.vehicleState
        if vehState is not None:
            vehState.onVehicleControlling += self.__onVehicleControlling
        self.__currentVehicleID = vehState.getControllingVehicleID()
        self.__onLivesUpdated(ctrl.playerLives)
        return

    def _dispose(self):
        super(WTReinforcementPanel, self)._dispose()
        vehState = self.__sessionProvider.shared.vehicleState
        if vehState is not None:
            vehState.onVehicleControlling -= self.__onVehicleControlling
        ctrl = self.__sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onTeammatesRespawnLivesUpdated -= self.__onTeamsRespawnLivesUpdated
        return

    def __onLivesUpdated(self, lives):
        self.as_setPlayerLivesS(lives)

    def __onTeamsRespawnLivesUpdated(self, lives):
        if self.__currentVehicleID in lives:
            self.__onLivesUpdated(lives[self.__currentVehicleID])

    def __onVehicleControlling(self, vehicle):
        if self.__currentVehicleID != vehicle.id:
            self.__currentVehicleID = vehicle.id
            lives = self.__sessionProvider.dynamic.respawn.teammatesLives.get(self.__currentVehicleID, 0)
            self.__onLivesUpdated(lives)
