# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ArenaObserverInfo.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class ArenaObserverInfo(BigWorld.Entity):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onEnterWorld(self, prereqs):
        BigWorld.player().arena.registerArenaObserverInfo(self)

    def onLeaveWorld(self):
        BigWorld.player().arena.unregisterArenaObserverInfo(self)

    def onDynamicComponentCreated(self, component):
        LOG_DEBUG_DEV('Component created', component)
