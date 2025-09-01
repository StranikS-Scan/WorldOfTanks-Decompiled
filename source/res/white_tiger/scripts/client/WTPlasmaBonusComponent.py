# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTPlasmaBonusComponent.py
import logging
import Event
from constants import IS_VS_EDITOR
from script_component.DynamicScriptComponent import DynamicScriptComponent
if not IS_VS_EDITOR:
    from white_tiger.gui.battle_control.white_tiger_battle_constants import VEHICLE_VIEW_STATE
    from gui.battle_control import avatar_getter
    import SoundGroups
_logger = logging.getLogger(__name__)

class WTPlasmaBonusComponent(DynamicScriptComponent):
    _WT23_PLASMA_BOOST_UI_SOUND_ID = 'ev_wt_ui_plasma_boost'

    def __init__(self):
        super(WTPlasmaBonusComponent, self).__init__()
        self.__plasmaVehicleBonuses = {}
        self.onPlasmaChanged = Event.Event()

    def set_plasmaBonusPerVehicle(self, prev=None):
        previousDict = dict(self.__plasmaVehicleBonuses)
        for vehiclePlasmaPair in self.plasmaBonusPerVehicle:
            self.__plasmaVehicleBonuses[vehiclePlasmaPair[0]] = vehiclePlasmaPair[1]

        self.__notifyUIAboutPlasmaChanges()
        self.__notifyPlayersPlugin()
        self.__triggerPlasmaBonusSound(previousDict)

    def getPlasmaBonusForVehicle(self, vehicleID):
        return self.__plasmaVehicleBonuses[vehicleID] if vehicleID in self.__plasmaVehicleBonuses else 0

    def getPlasmaBonusMultiplier(self, plasmaBonus):
        return (self.plasmaBonusLevelMultipliers[plasmaBonus] - 1) * 100 if plasmaBonus in self.plasmaBonusLevelMultipliers else 0

    def _onAvatarReady(self):
        for vehiclePlasmaPair in self.plasmaBonusPerVehicle:
            self.__plasmaVehicleBonuses[vehiclePlasmaPair[0]] = vehiclePlasmaPair[1]

        self.__notifyUIAboutPlasmaChanges()
        self.__notifyPlayersPlugin()

    def __notifyUIAboutPlasmaChanges(self):
        gameModeStats = {}
        for vehID in self.__plasmaVehicleBonuses:
            plasmaBonus = self.__plasmaVehicleBonuses.get(vehID, 0)
            gameModeStats[vehID] = plasmaBonus

        self.onPlasmaChanged(gameModeStats)

    def __notifyPlayersPlugin(self):
        vehicle = avatar_getter.getPlayerVehicle()
        if not vehicle:
            return
        vehicleID = avatar_getter.getPlayerVehicleID()
        ctrl = vehicle.guiSessionProvider.shared.vehicleState
        if vehicleID in self.__plasmaVehicleBonuses and ctrl:
            ctrl.notifyStateChanged(VEHICLE_VIEW_STATE.PLASMA, (self.__plasmaVehicleBonuses[vehicleID], self.plasmaBonusLevelMultipliers[self.__plasmaVehicleBonuses[vehicleID]]))

    def __triggerPlasmaBonusSound(self, previousPlasmaCountDict):
        vehicle = avatar_getter.getPlayerVehicle()
        if not vehicle:
            return
        vehicleID = avatar_getter.getPlayerVehicleID()
        if vehicleID in self.__plasmaVehicleBonuses:
            if self.__isPlasmaBonusChanged(vehicleID, previousPlasmaCountDict):
                SoundGroups.g_instance.playSound2D(self._WT23_PLASMA_BOOST_UI_SOUND_ID)

    def __isPlasmaBonusChanged(self, vehicleID, previousPlasmaCountDict):
        return True if not previousPlasmaCountDict or vehicleID not in previousPlasmaCountDict or not self.__plasmaVehicleBonuses else previousPlasmaCountDict[vehicleID] != self.__plasmaVehicleBonuses[vehicleID]
