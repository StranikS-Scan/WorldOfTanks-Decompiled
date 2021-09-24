# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/reinforcement_panel.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EventReinforcementPanelMeta import EventReinforcementPanelMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class EventReinforcementPanel(EventReinforcementPanelMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventReinforcementPanel, self).__init__()
        self.__currentVehicleID = None
        return

    def _populate(self):
        super(EventReinforcementPanel, self)._populate()
        spawnCtrl = self.__sessionProvider.dynamic.spawn
        if spawnCtrl is not None:
            spawnCtrl.onTeamLivesUpdated += self.__onTeamLivesUpdated
        vehState = self.__sessionProvider.shared.vehicleState
        if vehState is not None:
            vehState.onVehicleControlling += self.__onVehicleControlling
        self.__currentVehicleID = vehState.getControllingVehicleID()
        self.__onTeamLivesUpdated()
        return

    def _dispose(self):
        vehState = self.__sessionProvider.shared.vehicleState
        if vehState is not None:
            vehState.onVehicleControlling -= self.__onVehicleControlling
        spawnCtrl = self.__sessionProvider.dynamic.spawn
        if spawnCtrl is not None:
            spawnCtrl.onTeamLivesUpdated -= self.__onTeamLivesUpdated
        super(EventReinforcementPanel, self)._dispose()
        return

    def __onLivesUpdated(self, lives):
        if lives is not None:
            self.as_setPlayerLivesS(lives)
        return

    def __onTeamLivesUpdated(self):
        teamLivesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
        self.__onLivesUpdated(teamLivesComponent.getLives(self.__currentVehicleID) if teamLivesComponent else None)
        return

    def __onVehicleControlling(self, vehicle):
        if self.__currentVehicleID != vehicle.id:
            self.__currentVehicleID = vehicle.id
            self.__onTeamLivesUpdated()
