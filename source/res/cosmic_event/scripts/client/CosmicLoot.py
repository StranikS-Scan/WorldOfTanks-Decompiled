# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/CosmicLoot.py
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from typing import TYPE_CHECKING
from cosmic_event_common.cosmic_constants import LOOT_STATE
from cosmic_event.gui.shared.events import LootEvent
if TYPE_CHECKING:
    from gui.shared.events import HasCtxEvent
    from typing import Optional

class CosmicLoot(BigWorld.Entity):

    def onEnterWorld(self, *args):
        if self.state == LOOT_STATE.SPAWNED:
            self.__sendEvent(LootEvent.SPAWNED, {'loot': self})
        elif self.state == LOOT_STATE.PREPARING:
            self.__sendEvent(LootEvent.PREPARING, {'loot': self})

    def onLeaveWorld(self, *args):
        self.__sendEvent(LootEvent.DESTROYED, {'loot': self})

    def set_state(self, _):
        if self.state == LOOT_STATE.SPAWNED:
            self.__sendEvent(LootEvent.SPAWNED, {'loot': self})
        elif self.state == LOOT_STATE.PICKED_UP:
            self.__sendEvent(LootEvent.PICKED_UP, {'loot': self})
        elif self.state == LOOT_STATE.PREPARING:
            self.__sendEvent(LootEvent.PREPARING, {'loot': self})

    def __sendEvent(self, event, ctx):
        g_eventBus.handleEvent(LootEvent(event, ctx=ctx), scope=EVENT_BUS_SCOPE.BATTLE)
