# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/customizable_objects_manager.py
from functools import partial
import BigWorld
import HBAccountSettings
from ClientSelectableCameraObject import ClientSelectableCameraObject
from historical_battles_common.hb_constants_extension import QUEUE_TYPE
from adisp import adisp_process
from helpers import dependency
from gui.app_loader import sf_lobby
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import AccountSettingsKeys
from shared_utils import CONST_CONTAINER
from historical_battles.skeletons.gui.customizable_objects_manager import ICustomizableObjectsManager
from skeletons.gui.shared.utils import IHangarSpace
from gui.prb_control.entities.listener import IGlobalListener
from historical_battles.gui.hb_customization_camera import CustomizationCamera
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IHangarSpaceSwitchController
HISTORICAL_BATTLES_SCENE = 'historical_battles'

class AnchorNames(CONST_CONTAINER):
    DEFAULT = 'se22'
    HERO_TANK = 'hero_tank'


class CustomizableObjectsManager(ICustomizableObjectsManager, IGlobalListener):
    spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    hangarSpace = dependency.descriptor(IHangarSpace)
    eventsCache = dependency.descriptor(IEventsCache)
    c11nService = dependency.descriptor(ICustomizationService)
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(CustomizableObjectsManager, self).__init__()
        self.__cameraAnchors = {}
        self.__customizableObjects = {}
        self.__cam = CustomizationCamera()
        self.__currentAnchor = None
        self.__showFade = True
        return

    def init(self):
        self.__cam.init()
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        self.spaceSwitchController.onCheckSceneChange += self.__onCheckSceneChange
        self.spaceSwitchController.onSpaceUpdated += self.__onSpaceUpdated
        self.hangarSpace.onSpaceCreate += self.__onSpaceUpdated
        self._gameEventController.onSelectedFrontChanged += self.__onSelectedFrontChanged

    def __onCheckSceneChange(self):
        prbDispatcher = self.prbDispatcher
        if prbDispatcher:
            prbEntity = prbDispatcher.getEntity()
            if prbEntity.getQueueType() in QUEUE_TYPE.HB_RANGE:
                self.spaceSwitchController.hangarSpaceUpdate(HISTORICAL_BATTLES_SCENE)

    def __onSpaceUpdated(self):
        if self.spaceSwitchController.currentSceneName != HISTORICAL_BATTLES_SCENE:
            return
        self.switchByAnchorName()

    def isCamActive(self):
        return self.__cam.isActive

    def fini(self):
        self.__cam.destroy()
        self.__cameraAnchors.clear()
        self.__customizableObjects.clear()
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.spaceSwitchController.onCheckSceneChange -= self.__onCheckSceneChange
        self.spaceSwitchController.onSpaceUpdated -= self.__onSpaceUpdated
        self.hangarSpace.onSpaceCreate -= self.__onSpaceUpdated
        self._gameEventController.onSelectedFrontChanged -= self.__onSelectedFrontChanged

    def switchByAnchorName(self, anchorName=AnchorNames.DEFAULT):
        self.__switchTo(anchorName, self.__updateEnvironment)

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

    @staticmethod
    def __leaveEntity(ob, ctx, callback=None, switchCallback=None):
        if switchCallback:
            switchCallback(callback=partial(ob.__class__.leave, ob, ctx, callback))
        yield lambda callback: callback(None)

    @sf_lobby
    def __app(self):
        return None

    def __isSwitchingFromHeroTank(self, anchorName):
        return self.__currentAnchor != AnchorNames.HERO_TANK

    @adisp_process
    def __switchTo(self, anchorName, callback=None):
        yield lambda callback: callback(None)
        if self.__currentAnchor == anchorName:
            return
        self.__currentAnchor = anchorName
        if self.__showFade and self.__isSwitchingFromHeroTank(anchorName):
            self.__switchCamera(self.__currentAnchor)
        else:
            self.__switchCamera(self.__currentAnchor)
        if callback:
            callback()

    def __switchCamera(self, anchorName):
        if anchorName == AnchorNames.DEFAULT:
            ClientSelectableCameraObject.switchCamera(None, immediate=True)
        self.__cam.deactivate()
        if anchorName == AnchorNames.DEFAULT:
            self.__switchToCameraAnchor(anchorName)
        return

    def __updateEnvironmentAndVisibilityMask(self):
        frontSettings = HBAccountSettings.getSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS) or {}
        self.__changeEnvironmentAndVisibilityMask(frontSettings.get(AccountSettingsKeys.SELECTED_HISTORICAL_BATTLES_FRONT, 0))

    def __updateEnvironment(self):
        self.__updateEnvironmentAndVisibilityMask()

    def __onSelectedFrontChanged(self):
        self.__updateEnvironmentAndVisibilityMask()

    def __changeEnvironmentAndVisibilityMask(self, frontIndex):
        if self.spaceSwitchController.currentSceneName != HISTORICAL_BATTLES_SCENE or not self.hangarSpace.inited or self.hangarSpace.spaceLoading():
            return
        currentCampaignSettings = self._gameEventController.getEnvironmentSettings()[frontIndex]
        environmentId = currentCampaignSettings['environmentId']
        visibilityMask = currentCampaignSettings['visibilityMask']
        if environmentId:
            environmentSwitcher = BigWorld.EnvironmentSwitcher(environmentId)
            environmentSwitcher.enable(True)
        BigWorld.wg_setSpaceItemsVisibilityMask(self.hangarSpace.space.spaceId, visibilityMask)

    def __switchToCameraAnchor(self, anchorName):
        anchorDescr = self.getCameraAnchor(anchorName)
        if anchorDescr is not None:
            entity = self.getCustomizableEntity(anchorName)
            if entity is not None:
                self.__cam.activate(entity.position, anchorDescr)
        return

    def __onSpaceDestroy(self, _):
        self.__currentAnchor = None
        self.__cam.deactivate()
        return

    def __onEventsCacheSyncCompleted(self):
        self.__updateEnvironment()
