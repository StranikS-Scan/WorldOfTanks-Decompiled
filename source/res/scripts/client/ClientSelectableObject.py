# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableObject.py
import BigWorld
import Math
import SoundGroups
from ModelHitTester import SegmentCollisionResult
from debug_utils import LOG_ERROR

class ClientSelectableObject(BigWorld.Entity):

    @property
    def enabled(self):
        return self.__enabled

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.__bspModel = BigWorld.WGBspCollisionModel()
        self.__enabled = True
        self.__edged = False
        self.__clickSound = None
        return

    def prerequisites(self):
        return [self.modelName]

    def onEnterWorld(self, prereqs):
        if self.modelName not in prereqs.failedIDs:
            model = prereqs[self.modelName]
            self.model = model
            self.filter = BigWorld.DumbFilter()
            if not self.__bspModel.setModel(self.model):
                LOG_ERROR('ClientSelectableObject failed to setModel', self.modelName)

    def onLeaveWorld(self):
        if self.__clickSound is not None:
            if self.__clickSound.isPlaying:
                self.__clickSound.stop()
            self.__clickSound = None
        self.highlight(False)
        return

    def collideSegment(self, startPoint, endPoint, skipGun=False):
        worldToVehMatrix = Math.Matrix(self.model.matrix)
        worldToVehMatrix.invert()
        startPoint = worldToVehMatrix.applyPoint(startPoint)
        endPoint = worldToVehMatrix.applyPoint(endPoint)
        res = None
        collisions = self.__bspModel.collideSegment(startPoint, endPoint)
        if collisions is None:
            return res
        else:
            for dist, _, hitAngleCos, _ in collisions:
                if res is None or res[0] >= dist:
                    res = SegmentCollisionResult(dist, hitAngleCos, 0)

            return res

    def enable(self, enabled):
        self.__enabled = enabled
        if not self.__enabled:
            self.highlight(False)

    def highlight(self, show):
        if show:
            if not self.__edged and self.__enabled:
                BigWorld.wgAddEdgeDetectEntity(self, 0, 2)
                self.__edged = True
        elif self.__edged:
            BigWorld.wgDelEdgeDetectEntity(self)
            self.__edged = False

    def onClicked(self):
        if self.__clickSound is None:
            if len(self.clickSoundName) > 0:
                self.__clickSound = SoundGroups.g_instance.getSound3D(self.model.root, self.clickSoundName)
                self.__clickSound.play()
                return
        elif self.__clickSound.isPlaying:
            self.__clickSound.stop()
        else:
            self.__clickSound.play()
        return
