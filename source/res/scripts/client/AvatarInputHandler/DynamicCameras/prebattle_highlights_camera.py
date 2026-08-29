# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/prebattle_highlights_camera.py
import math
import logging
import BigWorld
import CGF
from functools import partial
from AvatarInputHandler.cameras import FovExtended
from CameraComponents import CameraComponent, ActiveCameraComponent, FovComponent, DofComponent
from GenericComponents import getGlobalTagStorage
from cgf_modules.sequence_events import sequenceSubscribe
from constants import PREBATTLE_SEQUENCE_EVENT_NAMES
from gui.battle_control.avatar_getter import getSpaceID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.controllers.prebattle_highlights.pbh_constants import TANK_CAMERA_TEMPLATE
_logger = logging.getLogger(__name__)
PBH_CAMERA_EVENTS = (PREBATTLE_SEQUENCE_EVENT_NAMES.ON_FOCUS_CAMERA_0, PREBATTLE_SEQUENCE_EVENT_NAMES.ON_FOCUS_CAMERA_1, PREBATTLE_SEQUENCE_EVENT_NAMES.ON_FOCUS_CAMERA_2)
INITIAL_CAMERA_INDEX = 0

class PrebattleHighlightsCamera(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, _):
        self.__cameraGo = None
        self.__pbhSize = None
        self.__customizationHelper = None
        return

    @property
    def aimingSystem(self):
        return None

    def enable(self):
        self.__pbhSize = self.__sessionProvider.dynamic.prebattleHighlightsController.getPBHSize()
        self.__customizationHelper = BigWorld.PyCustomizationHelper(None, 0, False, None)
        self.__subscribeOnSeqEvents()
        self.__tryToChangeCamera(INITIAL_CAMERA_INDEX)
        return

    def disable(self):
        if self.__cameraGo:
            queue = CGF.CommandQueue(self.__cameraGo.spaceID)
            queue.removeComponent(self.__cameraGo, ActiveCameraComponent)
        FovExtended.instance().resetFov()
        self.__customizationHelper.setDOFenabled(False)
        self.__customizationHelper.setDOFparams(0.0, 0.0, 0.0, 0.0)
        self.__customizationHelper = None
        self.__cameraGo = None
        return

    def __getPBHCameraGo(self, size, index=0):
        cameraTag = TANK_CAMERA_TEMPLATE.format(size, index)
        spaceID = BigWorld.player().spaceID
        cameraGo = getGlobalTagStorage(spaceID).getGameObjects(cameraTag)
        if not cameraGo:
            _logger.error('PBH camera GameObject not found: no objects with tag %s in spaceId=%s', cameraTag, spaceID)
            return None
        else:
            if len(cameraGo) > 1:
                _logger.warning('Multiple PBH camera GameObjects found for tag %s in spaceId=%s (count=%s). Using the first one.', cameraTag, spaceID, len(cameraGo))
            if not cameraGo[0].hasComponent(CameraComponent):
                _logger.error('No CameraComponent on PBH camera')
                return None
            return cameraGo[0]

    def __subscribeOnSeqEvents(self):
        spaceID = getSpaceID()
        for index, event in enumerate(PBH_CAMERA_EVENTS):
            sequenceSubscribe(spaceID, event, partial(self.__tryToChangeCamera, index))

    def __tryToChangeCamera(self, index):
        cameraGo = self.__getPBHCameraGo(self.__pbhSize, index)
        if cameraGo is None:
            return
        else:
            queue = CGF.CommandQueue(cameraGo.spaceID)
            if self.__cameraGo and self.__cameraGo.hasComponent(ActiveCameraComponent):
                queue.removeComponent(cameraGo, ActiveCameraComponent)
            queue.createComponent(cameraGo, ActiveCameraComponent)
            self.__cameraGo = cameraGo
            self.__applyCameraSettings(cameraGo)
            return

    def __applyCameraSettings(self, go):
        fovComponent = go.findRead(FovComponent)
        if fovComponent:
            FovExtended.instance().setFovByAbsoluteValue(math.degrees(fovComponent.value))
        dofComponent = go.findRead(DofComponent)
        if dofComponent:
            self.__customizationHelper.setDOFenabled(True)
            self.__customizationHelper.setDOFparams(dofComponent.nearStart, dofComponent.nearDist, dofComponent.farStart, dofComponent.farDist)
