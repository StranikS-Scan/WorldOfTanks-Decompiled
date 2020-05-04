# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/se20/customizable_objects_manager.py
from functools import partial
import BigWorld
import Event
import WWISE
from ClientSelectableCameraObject import ClientSelectableCameraObject
from constants import QUEUE_TYPE, EventHangarEnvironmentName
from adisp import process
from helpers import dependency
from gui.app_loader import sf_lobby
from shared_utils import CONST_CONTAINER
from skeletons.se20 import ICustomizableObjectsManager
from gui.prb_control.dispatcher import g_prbLoader
from skeletons.gui.shared.utils import IHangarSpace
from gui.prb_control.entities.listener import IGlobalListener
from se20.customization_camera import CustomizationCamera
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.customization import ICustomizationService
_DEFAULT_ANCHOR_NAME = 'se20'
_DEFAULT_ENVIRONMENT_NAME = 'SE20'
_WWISE_STATES_CONFIGS = {EventHangarEnvironmentName.RANDOM_PHASE_1.value: {'STATE_hangar_view': 'STATE_hangar_view_01',
                                                   'STATE_ev_2020_secret_event_hangar': 'STATE_ev_2020_secret_event_hangar_before'},
 EventHangarEnvironmentName.EVENT_PHASE_1.value: {'STATE_hangar_view': 'STATE_hangar_view_02',
                                                  'STATE_ev_2020_secret_event_hangar': 'STATE_ev_2020_secret_event_hangar_before'},
 EventHangarEnvironmentName.RANDOM_PHASE_2.value: {'STATE_hangar_view': 'STATE_hangar_view_01',
                                                   'STATE_ev_2020_secret_event_hangar': 'STATE_ev_2020_secret_event_hangar_after'},
 EventHangarEnvironmentName.EVENT_PHASE_2.value: {'STATE_hangar_view': 'STATE_hangar_view_02',
                                                  'STATE_ev_2020_secret_event_hangar': 'STATE_ev_2020_secret_event_hangar_after'}}

class AnchorNames(CONST_CONTAINER):
    DEFAULT = 'se20'
    HERO_TANK = 'hero_tank'
    RANDOM = None


class CustomizableObjectsManager(ICustomizableObjectsManager, IGlobalListener):
    hangarSpace = dependency.descriptor(IHangarSpace)
    eventsCache = dependency.descriptor(IEventsCache)
    c11nService = dependency.descriptor(ICustomizationService)

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
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher:
                self.__dispatcher = dispatcher
                self.__dispatcher.addListener(self)
        return

    def init(self):
        self.__cam.init()
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        self.c11nService.onCustomizationClosed += self.__onCustomizationClosed

    def onPrbEntitySwitching(self):
        if self.__dispatcher:
            prbEntity = self.__dispatcher.getEntity()
            if prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
                ClientSelectableCameraObject.switchCamera(immediate=True)

    def onPrbEntitySwitched(self):
        if self.__dispatcher:
            prbEntity = self.__dispatcher.getEntity()
            if prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
                self.switchByAnchorName()
            else:
                self.switchByAnchorName(AnchorNames.RANDOM)
            self.onPrbEntityChanged(prbEntity.getQueueType())

    def isCamActive(self):
        return self.__cam.isActive

    def fini(self):
        self.__cam.destroy()
        self.__cameraAnchors.clear()
        self.__customizableObjects.clear()
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.c11nService.onCustomizationClosed -= self.__onCustomizationClosed

    def switchByAnchorName(self, anchorName=AnchorNames.DEFAULT):
        self.__switchTo(anchorName, lambda : self.__updateEnvironment(anchorName))

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

    @process
    def __onPreQueueJoined(self, queueType=None, callback=None):
        yield lambda callback: callback(None)
        if queueType == QUEUE_TYPE.EVENT_BATTLES:
            self.switchByAnchorName()

    @staticmethod
    def __leaveEntity(ob, ctx, callback=None, switchCallback=None):
        if switchCallback:
            switchCallback(callback=partial(ob.__class__.leave, ob, ctx, callback))
        yield lambda callback: callback(None)

    @sf_lobby
    def __app(self):
        return None

    def __isSwitchingFromHeroTank(self, anchorName):
        return self.__currentAnchor != AnchorNames.HERO_TANK and anchorName != AnchorNames.RANDOM

    @process
    def __switchTo(self, anchorName, callback=None):
        yield lambda callback: callback(None)
        if self.__currentAnchor == anchorName:
            return
        self.__currentAnchor = anchorName
        if self.__showFade and self.__isSwitchingFromHeroTank(anchorName):
            readyToSwitch = yield self.__app.fadeMgr.startFade(settings={'duration': 0.65})
            if readyToSwitch:
                self.__switchCamera(self.__currentAnchor)
        else:
            self.__switchCamera(self.__currentAnchor)
        if callback:
            callback()

    def __switchCamera(self, anchorName):
        if anchorName == _DEFAULT_ANCHOR_NAME:
            ClientSelectableCameraObject.switchCamera(None, immediate=True)
        self.__cam.deactivate()
        if anchorName == AnchorNames.DEFAULT:
            self.__switchToCameraAnchor(anchorName)
        return

    def __updateEnvironment(self, anchorName):
        if not self.hangarSpace.space:
            return
        else:
            spaceId = self.hangarSpace.space.spaceId
            configName = 'eventHangar' if anchorName == AnchorNames.DEFAULT else 'randomHangar'
            hangarEnvironment = self.eventsCache.getGameEventData()
            hangarEnvironmentSettings = hangarEnvironment.get('hangarEnvironmentSettings', None)
            renderEnv = BigWorld.CustomizationEnvironment()
            if hangarEnvironmentSettings is None:
                renderEnv.enable(False)
                return
            envConfig = hangarEnvironmentSettings[configName]
            environmentId = envConfig['environmentId']
            visibilityMask = envConfig['visibilityMask']
            BigWorld.wg_setSpaceItemsVisibilityMask(spaceId, visibilityMask)
            if environmentId:
                renderEnv.enable(True, environmentId)
            else:
                renderEnv.enable(False)
            wwiseStates = _WWISE_STATES_CONFIGS[environmentId]
            for group, state in wwiseStates.items():
                WWISE.WW_setState(group, state)

            return

    def __switchToCameraAnchor(self, anchorName):
        anchorDescr = self.getCameraAnchor(anchorName)
        if anchorDescr is not None:
            entity = self.getCustomizableEntity(anchorName)
            if entity is not None:
                self.__cam.activate(entity.position, anchorDescr)
        return

    def __onSpaceCreated(self):
        self._startPreQueueListeners()
        self.__initDispatcher()
        oldValue = self.__showFade
        self.__showFade = False
        self.onPrbEntitySwitched()
        self.__updateEnvironment(self.__currentAnchor)
        self.__showFade = oldValue

    def __onSpaceDestroy(self, _):
        self._stopPreQueueListeners()
        self.__currentAnchor = None
        self.__dispatcher = None
        self.__cam.deactivate()
        return

    def __onEventsCacheSyncCompleted(self):
        self.__updateEnvironment(self.__currentAnchor)

    def __onCustomizationClosed(self):
        self.__updateEnvironment(self.__currentAnchor)

    def _startPreQueueListeners(self):
        g_prbCtrlEvents.onPreQueueJoined += self.__onPreQueueJoined

    def _stopPreQueueListeners(self):
        g_prbCtrlEvents.onPreQueueJoined -= self.__onPreQueueJoined
