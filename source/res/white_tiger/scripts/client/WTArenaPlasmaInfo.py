# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTArenaPlasmaInfo.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import EventKeys
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
from white_tiger.gui.gui_constants import FEEDBACK_EVENT_ID
from wt_settings import g_wt_config

class WTArenaPlasmaInfo(DynamicScriptComponent):
    _WT23_PLASMA_BOOST_START_SOUND_ID = 'ev_wt_gameplay_plasma_on'

    def set_plasmaInfoList(self, prev):
        if self.plasmaInfoList != prev:
            for plasmaInfo in self.plasmaInfoList:
                self.__updateGameModeSpecificStats(plasmaInfo)

    def setNested_plasmaInfoList(self, path, prev):
        self.__updateGameModeSpecificStats(self.plasmaInfoList[path[0]])

    def set_bossPlasmaCounter(self, prevValue):
        if self.bossPlasmaCounter != prevValue:
            playerVehicle = avatar_getter.getPlayerVehicle()
            arenaDP = self.entity.sessionProvider.getArenaDP()
            for vInfo in arenaDP.getVehiclesInfoIterator():
                vehCD = vInfo.vehicleType.compactDescr
                if g_wt_config.isAnyTypeBoss(vehCD):
                    ctrl = playerVehicle.guiSessionProvider.shared.feedback
                    ctrl.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.WT_VEHICLE_PLASMA_ON_BOSS, vInfo.vehicleID, (self.bossPlasmaCounter,))
                    self.__updateStatForVehicle(vInfo.vehicleID, self.bossPlasmaCounter)
                    return

    def _onAvatarReady(self):
        self.set_plasmaInfoList(None)
        return

    def __updateGameModeSpecificStats(self, plasmaInfo):
        self.__updateStatForVehicle(plasmaInfo.vehicleId, plasmaInfo.plasmaCounter)
        if plasmaInfo.plasmaCounter == 1:
            self.__playSoundIDOnVehicle(plasmaInfo.vehicleId)

    def __updateStatForVehicle(self, vehicleID, plasmaCounter):
        arena = avatar_getter.getArena()
        if not arena:
            return
        gameModeStats = {}
        gameModeStats[vehicleID] = {EventKeys.PLASMA_COUNT.value: plasmaCounter}
        arena.onGameModeSpecificStats(True, gameModeStats)

    def __playSoundIDOnVehicle(self, vehID):
        vehicle = BigWorld.entities.get(vehID)
        if vehicle and vehicle.appearance and vehicle.appearance.engineAudition and vehicle.isAlive():
            soundObject = vehicle.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.CHASSIS)
            if soundObject:
                soundObject.play(self._WT23_PLASMA_BOOST_START_SOUND_ID)
