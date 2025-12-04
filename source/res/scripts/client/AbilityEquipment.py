# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AbilityEquipment.py
import BigWorld
from constants import EQUIPMENT_STAGES as STAGES
from items import vehicles
from visual_script.misc import ASPECT
from visual_script_client.contexts.ability_context import AbilityContextClient
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers.fixed_dict import getVisualScriptEquipmentPublicState
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class AbilityEquipment(DynamicScriptComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AbilityEquipment, self).__init__()
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
        self.set_equipmentStatePublic()

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

    def set_equipmentStatePublic(self, _=None):
        if self._context is None:
            return
        else:
            state = getVisualScriptEquipmentPublicState(self.equipmentStatePublic)
            getattr(self._context, STAGES.toString(state.stage))()
            return

    def showGlowForSlot(self):
        equipments = self._sessionProvider.shared.equipments
        equipments.onShowGlowForSlot(self.compactDescr)

    def showBlinkReloadTime(self):
        equipments = self._sessionProvider.shared.equipments
        equipments.onShowBlinkReloadTime()
