# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleBeingAttackedComponent.py
import BigWorld
from helpers import dependency
from halloween.skeletons.gui.sound_controller import IHWSoundController

class HWVehicleBeingAttackedComponent(BigWorld.DynamicScriptComponent):
    _hwSoundController = dependency.descriptor(IHWSoundController)

    def onBeingAttacked(self, newHealth, attackerID):
        self._hwSoundController.onVehicleBeingAttacked(self.entity.id, attackerID, newHealth)
