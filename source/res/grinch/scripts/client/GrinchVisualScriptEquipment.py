# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/GrinchVisualScriptEquipment.py
import BigWorld
from constants import EQUIPMENT_STAGES as STAGES
from helpers.fixed_dict import getVisualScriptEquipmentPublicState
from items import vehicles
from visual_script.misc import ASPECT
from visual_script_client.contexts.ability_context import AbilityContextClient
from script_component.DynamicScriptComponent import DynamicScriptComponent

class GrinchVisualScriptEquipment(DynamicScriptComponent):

    def __init__(self):
        super(GrinchVisualScriptEquipment, self).__init__()
        self._vsPlan = None
        self._context = None
        return

    def _onAvatarReady(self):
        self.initVSE()
        self.set_state(self.state)
        self.set_locked(self.locked)

    def initVSE(self):
        player = BigWorld.player()
        descriptor = vehicles.getItemByCompactDescr(self.compactDescr)
        arenaInfo = player.arena.arenaInfo
        self._vsPlan = arenaInfo.visualScriptCache.getPlan(descriptor.name, descriptor.visualScript[ASPECT.CLIENT])
        self._context = AbilityContextClient(self.entity, equipmentName=descriptor.name)
        self._vsPlan.setContext(self._context)
        self._vsPlan.start()

    def canActivate(self):
        if self._context is not None:
            self._context.canActive()
            return (self._context.canActivate, self._context.errorKey)
        else:
            return (False, '')

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

    def set_locked(self, _):
        if self.entity.id != getattr(BigWorld.player(), 'playerVehicleID', 0):
            return
        eqCtrl = self.entity.guiSessionProvider.shared.equipments
        if eqCtrl.hasEquipment(self.compactDescr):
            eq = eqCtrl.getEquipment(self.compactDescr)
            eq.setLocked(self.locked)
            eqCtrl.onEquipmentUpdated(self.compactDescr, eq)

    def set_state(self, _):
        if self._context is None:
            return
        else:
            state = getVisualScriptEquipmentPublicState(self.state)
            getattr(self._context, STAGES.toString(state.stage))()
            return
