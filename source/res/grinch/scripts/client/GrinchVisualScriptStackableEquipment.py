# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/GrinchVisualScriptStackableEquipment.py
import BigWorld
from items import vehicles
from visual_script.misc import ASPECT
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from GrinchVisualScriptEquipment import GrinchVisualScriptEquipment
from grinch.gui.shared.events import StackableEquipmentUpdateEvent
from grinch.visual_script_client.ability_context import StackableAbilityContextClient

class GrinchVisualScriptStackableEquipment(GrinchVisualScriptEquipment):

    def _onAvatarReady(self):
        super(GrinchVisualScriptStackableEquipment, self)._onAvatarReady()
        self._sendStackableEquipmentEvent()

    def initVSE(self):
        player = BigWorld.player()
        descriptor = vehicles.getItemByCompactDescr(self.compactDescr)
        arenaInfo = player.arena.arenaInfo
        self._vsPlan = arenaInfo.visualScriptCache.getPlan(descriptor.name, descriptor.visualScript[ASPECT.CLIENT])
        self._context = StackableAbilityContextClient(self.entity, equipmentName=descriptor.name)
        self._vsPlan.setContext(self._context)
        self._vsPlan.start()

    @property
    def _maxStacksReached(self):
        return self.stacks >= self.maxStacks

    def set_stacks(self, _):
        if self._context is not None:
            self._context.updateStacks(self.stacks)
        self._sendStackableEquipmentEvent()
        return

    def _sendStackableEquipmentEvent(self):
        g_eventBus.handleEvent(StackableEquipmentUpdateEvent(StackableEquipmentUpdateEvent.STACKABLE_EQUIPMENT_UPDATED, stacks=self.stacks, reloadTime=self.stackReloadTime, reloadTimeLeft=self.__calculateStackReloadTimeLeft()), scope=EVENT_BUS_SCOPE.BATTLE)

    def __calculateStackReloadTimeLeft(self):
        return self.stackReloadTime - int(BigWorld.serverTime() - self.lastStackAddedTime) if not self._maxStacksReached else 0
