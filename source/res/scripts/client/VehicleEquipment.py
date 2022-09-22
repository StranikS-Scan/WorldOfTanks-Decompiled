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

    def _onAvatarReady(self):
        descriptor = vehicles.getItemByCompactDescr(self.compactDescr)
        arenaInfo = BigWorld.player().arena.arenaInfo
        planNames = [ plan['name'] for plan in descriptor.visualScript[ASPECT.CLIENT] ]
        self._vsPlan = arenaInfo.VSCache.getPlan(descriptor.name, planNames)
        self._context = AbilityContextClient(self.entity)
        self._vsPlan.setContext(self._context)
        self._vsPlan.start()
        self.set_stage(self.stage)
        self.set_locked(self.locked)

    def tryActivate(self):
        if self._context is None:
            return (False, '')
        else:
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

    def set_stage(self, _):
        if self._context is None:
            return
        else:
            getattr(self._context, STAGES.toString(self.stage))()
            return

    def set_locked(self, prev):
        eqCtrl = self.entity.guiSessionProvider.shared.equipments
        if eqCtrl.hasEquipment(self.compactDescr):
            eq = eqCtrl.getEquipment(self.compactDescr)
            eq.setLocked(self.locked)
            eqCtrl.onEquipmentUpdated(self.compactDescr, eq)
