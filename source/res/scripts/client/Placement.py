# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Placement.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AirDropEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class Placement(BigWorld.Entity):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        pass

    def onEnterWorld(self, *args):
        LOG_DEBUG_DEV('[Placement] onEnterWorld', BigWorld.time())
        event = AirDropEvent(AirDropEvent.AIR_DROP_SPAWNED, ctx={'id': self.id,
         'position': self.position})
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)
        cmpSystem = self.guiSessionProvider.arenaVisitor.getComponentSystem()
        if cmpSystem:
            if hasattr(cmpSystem, 'airDropComponent'):
                airDropComponent = getattr(cmpSystem, 'airDropComponent')
                airDropComponent.scheduleLoot(self.id, self.position, self.dropTime)

    def onLeaveWorld(self):
        LOG_DEBUG_DEV('[Placement] onLeaveWorld', BigWorld.time())
        event = AirDropEvent(AirDropEvent.AIR_DROP_LANDED, ctx={'id': self.id})
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)
