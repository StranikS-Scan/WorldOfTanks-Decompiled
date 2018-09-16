# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/client/Goal.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class Goal(BigWorld.Entity):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        BigWorld.Entity.__init__(self)

    def prerequisites(self):
        return []

    def reload(self):
        pass

    def destroy(self):
        self.onLeaveWorld()

    def onEnterWorld(self, prereqs):
        self.sessionProvider.dynamic.footballEntitiesCtrl.registerEntity(self)

    def onLeaveWorld(self):
        self.sessionProvider.dynamic.footballEntitiesCtrl.unregisterEntity(self)

    def onGoal(self, data):
        LOG_DEBUG_DEV('[Football] Goal onGoal')
