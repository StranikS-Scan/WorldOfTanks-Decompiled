# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableObject.py
import BigWorld
import Math
import SoundGroups
from ModelHitTester import SegmentCollisionResult
from debug_utils import LOG_ERROR
from christmas.ChristmasTank import ChristmasTank

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
        self.__onClickCallback = None
        self.__tooltipID = 0
        if hasattr(self, 'childObject') and self.childObject == 'ChristmasTank':
            self.__childObject = ChristmasTank(self)
        else:
            self.__childObject = None
        return

    def prerequisites(self):
        return [self.modelName]

    def tooltipID(self):
        return self.__childObject.tooltipID() if self.__childObject is not None else 0

    def onEnterWorld(self, prereqs):
        if self.modelName != '' and self.modelName not in prereqs.failedIDs:
            model = prereqs[self.modelName]
            self.model = model
            self.filter = BigWorld.DumbFilter()
            self.model.addMotor(BigWorld.Servo(self.matrix))
            if not self.__bspModel.setModel(self.model):
                LOG_ERROR('ClientSelectableObject failed to setModel', self.modelName)
        if self.__childObject is not None:
            self.__childObject.onEnterWorld()
        return

    def onLeaveWorld(self):
        if self.__clickSound is not None:
            if self.__clickSound.isPlaying:
                self.__clickSound.stop()
            self.__clickSound.releaseMatrix()
            self.__clickSound = None
        if self.__childObject is not None:
            self.__childObject.onLeaveWorld()
            self.__childObject = None
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
                BigWorld.wgAddEdgeDetectEntity(self, 0, 0, True)
                self.__edged = True
        elif self.__edged:
            BigWorld.wgDelEdgeDetectEntity(self)
            self.__edged = False

    def setOnClickCallback(self, callback):
        self.__onClickCallback = callback

    def onClicked(self):
        if self.__childObject is not None:
            self.__childObject.onClicked()
        if self.__onClickCallback is not None:
            self.__onClickCallback()
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
