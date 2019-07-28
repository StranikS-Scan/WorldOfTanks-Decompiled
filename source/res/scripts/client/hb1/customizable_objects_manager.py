# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hb1/customizable_objects_manager.py
import BigWorld
import Event
from constants import QUEUE_TYPE
from adisp import process
from helpers import dependency
from gui.app_loader import sf_lobby
from skeletons.hb1 import ICustomizableObjectsManager
from gui.prb_control.dispatcher import g_prbLoader
from skeletons.gui.shared.utils import IHangarSpace
from gui.prb_control.entities.listener import IGlobalListener
from .customization_camera import CustomizationCamera
_DEFAULT_ANCHOR_NAME = 'hb1'
_DEFAULT_ENVIRONMENT_NAME = 'HB1'

class CustomizableObjectsManager(ICustomizableObjectsManager, IGlobalListener):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(CustomizableObjectsManager, self).__init__()
        self.__cameraAnchors = {}
        self.__customizableObjects = {}
        self.__cam = CustomizationCamera()
        self.__currentAnchor = None
        self.__dispatcher = None
        self.__initDispatcher()
        self.__showFade = True
        self.onPrbEntityChanged = Event.Event()
        return

    def __initDispatcher(self):
        if self.__dispatcher is None:
            self.__dispatcher = g_prbLoader.getDispatcher()
            self.__dispatcher.addListener(self)
        return

    def init(self):
        self.__cam.init()
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def onPrbEntitySwitched(self):
        prbEntity = self.__dispatcher.getEntity()
        if prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
            self.switchByAnchorName()
        elif self.__currentAnchor is not None:
            self.switchByAnchorName(None)
        self.onPrbEntityChanged(prbEntity.getQueueType())
        return

    def isCamActive(self):
        return self.__cam.isActive

    def fini(self):
        self.__cam.destroy()
        self.__cameraAnchors.clear()
        self.__customizableObjects.clear()
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy

    def switchByAnchorName(self, anchorName=_DEFAULT_ANCHOR_NAME):
        self.__switchTo(anchorName)

    def addCustomizableEntity(self, entity):
        anchorName = entity.anchorName
        self.__customizableObjects[anchorName] = entity

    def removeCustomizableEntity(self, entity):
        anchorName = entity.anchorName
        self.__customizableObjects.pop(anchorName, None)
        return

    def getCustomizableEntity(self, anchorName):
        return self.__customizableObjects.get(anchorName)

    def addCameraAnchor(self, anchorName, anchor):
        self.__cameraAnchors[anchorName] = anchor

    def removeCameraAnchor(self, anchorName):
        if anchorName in self.__cameraAnchors:
            del self.__cameraAnchors[anchorName]

    def getCameraAnchor(self, anchorName):
        return self.__cameraAnchors.get(anchorName)

    def showFade(self, show):
        self.__showFade = show

    @sf_lobby
    def __app(self):
        return None

    @process
    def __switchTo(self, anchorName):
        yield lambda callback: callback(None)
        if self.__currentAnchor == anchorName:
            return
        self.__currentAnchor = anchorName
        if self.__showFade:
            readyToSwitch = yield self.__app.fadeManager.startFade()
            if readyToSwitch:
                self.__switchCamera(self.__currentAnchor)
        else:
            self.__switchCamera(self.__currentAnchor)

    def __switchCamera(self, anchorName):
        self.__cam.deactivate()
        renderEnv = BigWorld.CustomizationEnvironment()
        if anchorName is not None:
            self.__switchToCameraAnchor(anchorName)
            renderEnv.enable(True, _DEFAULT_ENVIRONMENT_NAME)
        else:
            renderEnv.enable(False)
        return

    def __switchToCameraAnchor(self, anchorName):
        anchorDescr = self.getCameraAnchor(anchorName)
        if anchorDescr is not None:
            entity = self.getCustomizableEntity(anchorName)
            if entity is not None:
                self.__cam.activate(entity.position, anchorDescr)
        return

    def __onSpaceCreated(self):
        self.__initDispatcher()
        oldValue = self.__showFade
        self.__showFade = False
        self.onPrbEntitySwitched()
        self.__showFade = oldValue

    def __onSpaceDestroy(self, _):
        self.__currentAnchor = None
        self.__dispatcher = None
        return
