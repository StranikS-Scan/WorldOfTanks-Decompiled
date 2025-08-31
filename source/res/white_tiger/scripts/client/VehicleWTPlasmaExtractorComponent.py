# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/VehicleWTPlasmaExtractorComponent.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import EventKeys
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from cgf_components import wt_helpers

class VehicleWTPlasmaExtractorComponent(DynamicScriptComponent):

    def __init__(self):
        super(VehicleWTPlasmaExtractorComponent, self).__init__()
        self.__updatePlasmaMarker()

    def set_plasmaCounter(self, _):
        self.__updatePlasmaMarker()
        self.__updatePlayerPlugin()

    def __updatePlasmaMarker(self):
        arena = avatar_getter.getArena()
        gameModeStats = {}
        gameModeStats[self.entity.id] = {EventKeys.PLASMA_COUNT.value: self.plasmaCounter}
        arena.onGameModeSpecificStats(True, gameModeStats)

    def __updatePlayerPlugin(self):
        vehicle = avatar_getter.getPlayerVehicle()
        if wt_helpers.isBossVehicle(vehicle):
            ctrl = self.entity.guiSessionProvider.shared.vehicleState
            totalPlasmaBonus = self.plasmaCounter * self.multiplierDamagePerPlasma + 1
            ctrl.notifyStateChanged(VEHICLE_VIEW_STATE.PLASMA, (self.plasmaCounter, totalPlasmaBonus))
