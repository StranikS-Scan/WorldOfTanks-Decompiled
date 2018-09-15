# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableObject.py
import BigWorld
import Math
import SoundGroups
from ModelHitTester import SegmentCollisionResult
from debug_utils import LOG_ERROR

class ClientSelectableObject(BigWorld.Entity):

    def __init__(self, edgeMode=2):
        super(ClientSelectableObject, self).__init__()
        self.__edgeMode = edgeMode
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
            model.castsShadow = self._castsShadow()
            self.model = model
            self.filter = BigWorld.DumbFilter()
            self.model.addMotor(BigWorld.Servo(self.matrix))
            self.__setBSP(model)

    def onLeaveWorld(self):
        if self.__clickSound is not None:
            if self.__clickSound.isPlaying:
                self.__clickSound.stop()
            self.__clickSound.releaseMatrix()
            self.__clickSound = None
        self.highlight(False)
        return

    def collideSegment(self, startPoint, endPoint, skipGun=False):
        worldToModelMatrix = Math.Matrix(self.model.matrix)
        worldToModelMatrix.invert()
        startPoint = worldToModelMatrix.applyPoint(startPoint)
        endPoint = worldToModelMatrix.applyPoint(endPoint)
        res = None
        collisions = self.__bspModel.collideSegment(startPoint, endPoint)
        if collisions is None:
            return
        else:
            for dist, _, hitAngleCos, _ in collisions:
                if res is None or res[0] >= dist:
                    res = SegmentCollisionResult(dist, hitAngleCos, 0)

            return res

    def enable(self, enabled):
        self.__enabled = enabled
        if not self.__enabled:
            self.highlight(False)

    @property
    def enabled(self):
        return self.__enabled

    def highlight(self, show):
        if show:
            if not self.__edged and self.__enabled:
                BigWorld.wgAddEdgeDetectEntity(self, 0, self.__edgeMode, True)
                self.__edged = True
                self.onMouseEnter()
        elif self.__edged:
            BigWorld.wgDelEdgeDetectEntity(self)
            self.__edged = False
            self.onMouseLeave()

    def onClicked(self):
        if self.__clickSound is None:
            if self.clickSoundName:
                self.__clickSound = SoundGroups.g_instance.getSound3D(self.model.root, self.clickSoundName)
                self.__clickSound.play()
        elif self.__clickSound.isPlaying:
            self.__clickSound.stop()
        else:
            self.__clickSound.play()
        return

    def onMouseEnter(self):
        pass

    def onMouseLeave(self):
        pass

    def _tryToOverrideBSP(self, bspModel):
        self.__setBSP(bspModel)

    def _castsShadow(self):
        return True

    def __setBSP(self, bspModel):
        if not self.__bspModel.setModel(bspModel):
            LOG_ERROR('ClientSelectableObject failed to setModel', bspModel.sources)
