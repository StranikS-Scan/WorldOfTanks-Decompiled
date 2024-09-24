# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VisualScriptEquipment.py
import BigWorld
from constants import EQUIPMENT_STAGES as STAGES
from helpers import dependency
from helpers.fixed_dict import getVisualScriptEquipmentState
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from visual_script.misc import ASPECT
from visual_script_client.contexts.ability_context import AbilityContextClient
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VisualScriptEquipment(DynamicScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(VisualScriptEquipment, self).__init__()
        self._vsPlan = None
        self._context = None
        return

    def _onAvatarReady(self):
        player = BigWorld.player()
        descriptor = vehicles.getItemByCompactDescr(self.compactDescr)
        arenaInfo = player.arena.arenaInfo
        self._vsPlan = arenaInfo.visualScriptCache.getPlan(descriptor.name, descriptor.visualScript[ASPECT.CLIENT])
        self._context = AbilityContextClient(self.entity, equipmentName=descriptor.name)
        self._vsPlan.setContext(self._context)
        self._vsPlan.start()
        self.set_errorState()
        self.set_equipmentState()

    def canActivate(self):
        if self._context is None:
            return (False, None)
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

    def set_errorState(self, _=None):
        if self._context is None:
            return
        else:
            self._context.onSetErrorState(self.errorState)
            state = getVisualScriptEquipmentState(self.equipmentState)
            self.__update(state)
            return

    def set_equipmentState(self, _=None):
        if self._context is None:
            return
        else:
            state = getVisualScriptEquipmentState(self.equipmentState)
            getattr(self._context, STAGES.toString(state.stage))()
            self.__update(state)
            return

    def update(self):
        state = getVisualScriptEquipmentState(self.equipmentState)
        self.__update(state)

    def __update(self, state):
        timeRemaining = max(state.endTime - BigWorld.serverTime(), 0.0) if state.endTime > 0 else state.endTime
        BigWorld.player().updateVehicleAmmo(self.entity.id, self.compactDescr, state.quantity, state.stage, state.prevStage, timeRemaining, state.totalTime)
