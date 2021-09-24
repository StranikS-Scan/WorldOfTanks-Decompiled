# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleEquipment.py
from debug_utils import LOG_DEBUG_DEV
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from items import vehicles
from visual_script.misc import ASPECT
from constants import EQUIPMENT_STAGES as STAGES
from visual_script_client.contexts.ability_context import AbilityContextClient

class VehicleEquipment(DynamicScriptComponent):

    def __init__(self):
        descriptor = vehicles.getItemByCompactDescr(self.compactDescr)
        LOG_DEBUG_DEV('descriptor', descriptor.visualScript[ASPECT.CLIENT])
        self._vsPlan = None
        self._context = None
        super(VehicleEquipment, self).__init__()
        return

    def onAvatarReady(self):
        descriptor = vehicles.getItemByCompactDescr(self.compactDescr)
        arenaInfo = BigWorld.player().arena.arenaInfo
        self._vsPlan = arenaInfo.VSCache.getPlan(descriptor.name, descriptor.visualScript[ASPECT.CLIENT])
        self._context = AbilityContextClient(self.entity)
        self._vsPlan.setContext(self._context)
        self._vsPlan.start()
        self.set_stage()

    def tryActivate(self):
        self._context.canActive()
        return (self._context.canActivate, self._context.errorKey)

    def onDestroy(self):
        if self._context is not None:
            self._context.cleanup()
        if self._vsPlan is not None:
            self._vsPlan.stop()
        if self._context is not None:
            self._context.destroy()
        self._context = None
        self._vsPlan = None
        return

    def set_stage(self, prev=None):
        if self._context is None:
            return
        else:
            timeRemainig = self.endTime
            if self.endTime > 0:
                timeRemainig = max(self.endTime - BigWorld.serverTime(), 0.0)
            getattr(self._context, STAGES.toString(self.stage))()
            LOG_DEBUG_DEV('stage', self.entity.id, self.compactDescr, self.quantity, self.stage, self.prevStage, timeRemainig, self.totalTime)
            if BigWorld.player().guiSessionProvider.shared.equipments.hasEquipment(self.compactDescr):
                BigWorld.player().updateVehicleAmmo(self.entity.id, self.compactDescr, self.quantity, self.stage, self.prevStage, timeRemainig, self.totalTime)
            return
