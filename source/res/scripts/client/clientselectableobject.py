# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableObject.py
import BigWorld
import Math
import SoundGroups
from ModelHitTester import SegmentCollisionResult
from debug_utils import LOG_ERROR, LOG_DEBUG_DEV

class ClientSelectableObject(BigWorld.Entity):
    __cameraLocked = False

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.__bspModel = BigWorld.WGBspCollisionModel()
        self.__enabled = True
        self.__edged = False
        self._clickSound = None
        self.__cameraFlyToSound = None
        self.__cameraFlyFromSound = None
        self.customBspModelName = None
        self.mouseOverSound = None
        self.model = None
        return

    @property
    def enabled(self):
        return self.__enabled

    @property
    def cameraLocked(self):
        return ClientSelectableObject.__cameraLocked

    @staticmethod
    def lockCamera(lock):
        ClientSelectableObject.__cameraLocked = lock

    @staticmethod
    def neutraliseSound(sound):
        if sound is not None:
            if sound.isPlaying:
                sound.stop()
            sound.releaseMatrix()
        return

    def prerequisites(self):
        return [self.modelName]

    def onEnterWorld(self, prereqs):
        if self.modelName == '':
            return
        else:
            if self.modelName not in prereqs.failedIDs:
                model = prereqs[self.modelName]
                self.model = model
                self.filter = BigWorld.DumbFilter()
                self.model.addMotor(BigWorld.Servo(self.matrix))
                if self.customBspModelName is not None:
                    self.__doCustomBspModel()
                elif not self.__bspModel.setModel(self.model):
                    LOG_ERROR('ClientSelectableObject failed to setModel', self.modelName)
            return

    def onLeaveWorld(self):
        ClientSelectableObject.lockCamera(False)
        ClientSelectableObject.neutraliseSound(self._clickSound)
        self._clickSound = None
        ClientSelectableObject.neutraliseSound(self.__cameraFlyToSound)
        self.__cameraFlyToSound = None
        ClientSelectableObject.neutraliseSound(self.__cameraFlyFromSound)
        self.__cameraFlyFromSound = None
        self.highlight(False)
        return

    def enable(self, enabled):
        self.__enabled = enabled
        if not self.__enabled:
            self.highlight(False)

    def highlight(self, show):
        if show:
            if not self.__edged and self.__enabled:
                BigWorld.wgAddEdgeDetectEntity(self, 0, 2, True)
                self.__edged = True
        elif self.__edged:
            BigWorld.wgDelEdgeDetectEntity(self)
            self.__edged = False

    def onClicked(self, cameraCallback=None):
        from halloween_shared import LEVIATHAN_COMPACT_DESCRIPTION
        if self.selectionId == 'leviathan':
            from gui.shared import events, g_eventBus
            from gui.shared.event_bus import EVENT_BUS_SCOPE
            from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LEVIATHAN_PREVIEW, ctx={'itemCD': LEVIATHAN_COMPACT_DESCRIPTION,
             'previewAlias': VIEW_ALIAS.LOBBY_HANGAR,
             'vehicleStrCD': None,
             'entity3d': self}), scope=EVENT_BUS_SCOPE.LOBBY)
        if self._clickSound is None:
            if self.clickSoundName:
                self._clickSound = SoundGroups.g_instance.getSound3D(self.model.root, self.clickSoundName)
                self._clickSound.play()
                LOG_DEBUG_DEV('ClientSelectableObject: playing click sound ' + self.clickSoundName)
        elif self._clickSound.isPlaying:
            self._clickSound.stop()
        else:
            self._clickSound.play()
            LOG_DEBUG_DEV('ClientSelectableObject: playing click sound ' + self.clickSoundName)
        return

    def playCameraFlyToSound(self):
        if self.__cameraFlyToSound is None:
            if self.cameraFlyToSoundName:
                self.__cameraFlyToSound = SoundGroups.g_instance.getSound2D(self.cameraFlyToSoundName)
        if self.__cameraFlyToSound is not None:
            if self.__cameraFlyToSound.isPlaying:
                self.__cameraFlyToSound.stop()
            self.__cameraFlyToSound.play()
            LOG_DEBUG_DEV('ClientSelectableObject: playing camera fly to sound ' + self.cameraFlyToSoundName)
            return True
        else:
            return False
            return

    def playCameraFlyFromSound(self):
        if self.__cameraFlyFromSound is None:
            if self.cameraFlyFromSoundName:
                self.__cameraFlyFromSound = SoundGroups.g_instance.getSound2D(self.cameraFlyFromSoundName)
        if self.__cameraFlyFromSound is not None:
            if self.__cameraFlyFromSound.isPlaying:
                self.__cameraFlyFromSound.stop()
            self.__cameraFlyFromSound.play()
            LOG_DEBUG_DEV('ClientSelectableObject: playing camera fly from sound ' + self.cameraFlyFromSoundName)
            return True
        else:
            return False
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

    def _getModelHeight(self):
        return self.model.height

    def __doCustomBspModel(self):
        prereqs = [self.customBspModelName]
        BigWorld.loadResourceListBG(list(prereqs), self.__customBspModelLoaded)

    def __customBspModelLoaded(self, resourceRefs):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load resources %s' % (resourceRefs.failedIDs,))
        else:
            theModel = resourceRefs[self.customBspModelName]
            self.__bspModel.setModel(theModel)
