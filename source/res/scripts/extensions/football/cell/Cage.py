# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/cell/Cage.py
import BigWorld
import PhysicsWorld
from PhysicalObject import PhysicalObject
import ArenaType
import ResMgr
import Math
from items import _xml

def init():
    pass


class Cage(PhysicalObject):

    def __init__(self):
        settings = ArenaType.g_cache[self.arenaTypeID].football
        points, fences, normals = self.__readCell(settings.cellModel)
        points = [ x + settings.cellPosition for x in points ]
        cell = BigWorld.PyCell()
        cell.setup(points, fences, normals)
        self.physics = cell
        PhysicsWorld.getWorld().addToCache(self)

    def __readCell(self, fileName):
        points = list()
        fences = list()
        normals = list()
        rootSection = ResMgr.openSection(fileName, False)
        for name, value in _xml.getChildren(None, rootSection, 'points'):
            if name == 'point':
                points.append(value['geometry'].asVector3)

        for name, value in _xml.getChildren(None, rootSection, 'planes'):
            if name == 'plane':
                fences.append(_xml.readTupleOfNonNegativeInts(None, value, 'pindices'))
                normals.append(value['normal'].asVector3)

        return (points, fences, normals)

    def onDestroy(self):
        PhysicsWorld.getWorld().removeFromCache(self)

    def onLeavingCell(self):
        pass

    def onEnteredCell(self):
        if not hasattr(self, 'physics'):
            self.physics = BigWorld.PyCell()

    def onRestore(self):
        if not hasattr(self, 'physics'):
            self.physics = BigWorld.PyCell()

    def beforeSimulation(self):
        pass

    def afterSimulation(self):
        pass
