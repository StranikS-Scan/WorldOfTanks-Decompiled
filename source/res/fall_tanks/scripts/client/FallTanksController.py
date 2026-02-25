# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/FallTanksController.py
from __future__ import absolute_import
from collections import namedtuple
import typing
import BigWorld
import SoundGroups
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from fall_tanks.gui.battle_control.fall_tanks_battle_constants import VEHICLE_VIEW_STATE
from fall_tanks.gui.feature.fall_tanks_sounds import FallTanksSounds
EvacuationState = namedtuple('EvacuationState', ('isActive', 'totalTime', 'endTime'))

def getPlayerVehicleFallTanksController():
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get('FallTanksController') if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


class FallTanksController(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getEvacuationState(self):
        return EvacuationState(self.evacuationState.endTime > 0, self.evacuationState.baseTime, self.evacuationState.endTime)

    def set_evacuationState(self, prevState):
        if prevState.endTime > 0 and self.evacuationState.endTime == 0:
            SoundGroups.g_instance.playSound2D(FallTanksSounds.TELEPORT_EVENT)
        self.__guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.VEHICLE_EVACUATION, self.getEvacuationState())

    def startVehicleEvacuation(self):
        self.cell.initiateVehicleEvacuation()

    def stopVehicleEvacuation(self):
        self.cell.cancelVehicleEvacuation()
