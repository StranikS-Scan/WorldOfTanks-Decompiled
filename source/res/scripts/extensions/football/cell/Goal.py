# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/cell/Goal.py
import weakref
import BigWorld
import PhysicsWorld
from PhysicalObject import PhysicalObject
from debug_utils import LOG_DEBUG_DEV

def init():
    pass


class Goal(PhysicalObject):

    def __init__(self):
        self.team = 0
        self.__isBallScored = False
        physics = BigWorld.PyGoal()
        goalSize = (16.5, 12.0, 42.0)
        goalCenter = (0.0, 0.0, 0.0)
        goalWorldPosition = self.position
        physics.setup(goalSize, goalCenter, goalWorldPosition)
        self.footballArena = self.arena.components['ArenaFootballMechanics']
        physics.owner = weakref.ref(self)
        physics.physicalObjectcollisionImpactCb = self.__hitCallback
        self.physics = physics
        PhysicsWorld.getWorld().addToCache(self)
        LOG_DEBUG_DEV('[GOAL CREATED] at position: ' + str(self.position))

    def __hitCallback(self, hitStr, *args):
        if not self.__isBallScored:
            self.footballArena.onFootballGoal(3 - self.team)
            self.__isBallScored = True

    def onDestroy(self):
        PhysicsWorld.getWorld().removeFromCache(self)
        self.footballArena = None
        return

    def onLeavingCell(self):
        pass

    def onEnteredCell(self):
        if not hasattr(self, 'physics'):
            self.physics = BigWorld.PyGoal()

    def onRestore(self):
        if not hasattr(self, 'physics'):
            self.physics = BigWorld.PyGoal()

    def beforeSimulation(self):
        pass

    def afterSimulation(self):
        pass

    def setTeam(self, teamID):
        self.team = teamID

    def resetState(self):
        self.__isBallScored = False
