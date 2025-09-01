# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/hangar_helpers.py
import logging
from functools import partial
from typing import TYPE_CHECKING
import CGF
import Event
import SoundGroups
from GenericComponents import Sequence
from cgf_components.hangar_camera_manager import HangarCameraManager
from cgf_components.pm30_hangar_components import HangarOperationsManager
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.lobby.personal_missions_30.personal_mission_constants import OperationIDs, CameraNameTemplates, StageAdditions, STAGES_CONFIG, TopCameras, CAMERA_IMMEDIATE_TRANSITION_DURATION, SoundsKeys, SoundsStateKeys
from gui.impl.lobby.personal_missions_30.personal_mission_constants import StageInfo
from gui.impl.lobby.personal_missions_30.views_helpers import hasAssemblingVideo
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showPM30OperationAssemblingVideoWindow
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.shared.utils import IHangarSpace
if TYPE_CHECKING:
    from typing import Optional, Callable
    from cgf_components.pm30_hangar_components import AssemblingStagesComponent
_logger = logging.getLogger(__name__)

class AssemblingManager(object):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.onCameraFlightStarted = Event.Event()
        self.onCameraFlightFinished = Event.Event()
        self.onAssemblingVideoFinished = Event.Event()
        self.onAssemblingAnimationStarted = Event.Event()
        self.onAssemblingAnimationFinished = Event.Event()
        self.__operationID = None
        self.__currentStage = None
        self.__vehicleGO = None
        self.__vehicleStagesComponent = None
        self.__stageNumberForAssembling = None
        self.__hangarOperationsManager = None
        self.__cameraManager = None
        self.__stageFade = None
        self.__activeComponents = StageInfo(0, 0, set(), set())
        self.__cameraSwitchingCallback = None
        return

    def init(self):
        cameraManager = self.getCameraManager()
        if cameraManager is not None:
            cameraManager.onCameraSwitched += self.__onCameraSwitched
        return

    def deactivate(self):
        self.deactivateVehicleGO()
        self.setHangarProgressionStateOff()

    def destroy(self):
        cameraManager = self.getCameraManager()
        if cameraManager is not None:
            cameraManager.onCameraSwitched -= self.__onCameraSwitched
        self.__vehicleGO = None
        self.__vehicleStagesComponent = None
        self.__hangarOperationsManager = None
        self.__cameraManager = None
        self.__stageNumberForAssembling = None
        self.__operationID = None
        self.__currentStage = None
        self.__stageFade = None
        self.__activeComponents = None
        self.__cameraSwitchingCallback = None
        self.onCameraFlightStarted.clear()
        self.onCameraFlightFinished.clear()
        self.onAssemblingVideoFinished.clear()
        self.onAssemblingAnimationStarted.clear()
        self.onAssemblingAnimationFinished.clear()
        return

    def getHangarOperationsManager(self):
        if not self.__hangarOperationsManager:
            spaceID = self.hangarSpace.spaceID
            manager = CGF.getManager(spaceID, HangarOperationsManager) if spaceID is not None else None
            self.__hangarOperationsManager = manager
        return self.__hangarOperationsManager

    def getCameraManager(self):
        if not self.__cameraManager:
            spaceID = self.hangarSpace.spaceID
            manager = CGF.getManager(spaceID, HangarCameraManager) if spaceID is not None else None
            self.__cameraManager = manager
        return self.__cameraManager

    def assembleStage(self, stageNumber, isFinalStage=False):
        self.__stageNumberForAssembling = stageNumber
        if isFinalStage:
            self.__activateStages(self.__stageNumberForAssembling)
            return
        self.__stageFade = self.__getStage(self.__stageNumberForAssembling, isFade=True)
        if self.__stageFade:
            self.onAssemblingAnimationStarted()
            self.switchCameraToStagePosition(stageNumber, callback=partial(self.__activateStageFade, self.__stageFade))
        else:
            showPM30OperationAssemblingVideoWindow(self.__operationID, stageNumber, closingCallback=self.__onVideoFinished)

    def assembleObtainedStages(self):
        self.__activateStages(self.__currentStage)

    def switchCameraToStagePosition(self, stageNumber, instantly=False, callback=None):
        cameraName = CameraNameTemplates.STAGE.format(self.__operationID, stageNumber)
        self.__switchByCameraName(cameraName, instantly=instantly, callback=callback)

    def switchCameraToTopPosition(self, topCameraNumber, instantly=False, callback=None):
        cameraName = CameraNameTemplates.TOP.format(self.__operationID, topCameraNumber)
        self.__switchByCameraName(cameraName, instantly=instantly, callback=callback)

    def switchCameraToFreePosition(self, instantly=False, callback=None):
        cameraName = CameraNameTemplates.FREE.format(self.__operationID)
        self.__switchByCameraName(cameraName, instantly=instantly, callback=callback)

    def switchCameraToMainPosition(self, isOperationFullCompleted, instantly=False, callback=None):
        if isOperationFullCompleted:
            self.switchCameraToFreePosition(instantly=instantly, callback=callback)
        else:
            self.switchCameraToTopPosition(TopCameras.SECOND, instantly=instantly, callback=callback)

    def changeVehicleGO(self, operationID, currentStage):
        vehicleGOForOperation, vehicleStagesComponent = self.__getVehicleGOForOperation(operationID)
        if not vehicleGOForOperation:
            _logger.warning('[PM3.0] VehicleGO for operation=%s is not found', operationID)
            return
        if not self.__vehicleGO:
            self.__setAndActivateVehicleGO(vehicleGOForOperation, vehicleStagesComponent, operationID, currentStage)
        elif self.__vehicleGO != vehicleGOForOperation:
            self.deactivateVehicleGO()
            self.__setAndActivateVehicleGO(vehicleGOForOperation, vehicleStagesComponent, operationID, currentStage)

    def getCameraEvents(self, viewModel):
        return [(viewModel.onMoveSpace, self.__onMoveSpace), (viewModel.onMouseOver3dScene, self.__onMouseOver3dScene)]

    def activateSelectableLogic(self):
        self.hangarSpace.lockVehicleSelectable(self)

    def deactivateSelectableLogic(self):
        self.hangarSpace.unlockVehicleSelectable(self)

    def deactivateVehicleGO(self):
        if self.__hangarOperationsManager.gameObjectsAreRemoved:
            return
        if self.__vehicleGO and self.__vehicleGO.isValid():
            for activeStageNumber in self.__activeComponents.stages.copy():
                self.__deactivateStage(activeStageNumber)

            for activeAddition in self.__activeComponents.additions.copy():
                self.__deactivateAddition(activeAddition)

            self.__vehicleGO.deactivate()
        else:
            _logger.warning('[PM3.0] Vehicle GO for %s operation is not found or invalid', self.__operationID)

    def startTopCameraAnimation(self):
        self.switchCameraToTopPosition(TopCameras.FIRST, instantly=True)
        nextTick(partial(self.switchCameraToTopPosition, TopCameras.SECOND))()

    def showStageAssemblingVideo(self, stageNumber):
        if hasAssemblingVideo(self.__operationID, stageNumber):
            showPM30OperationAssemblingVideoWindow(self.__operationID, stageNumber)

    @staticmethod
    def setHangarProgressionStateOn():
        SoundGroups.g_instance.setState(SoundsStateKeys.HANGAR_PROGRESSION_STATE, SoundsStateKeys.HANGAR_PROGRESSION_ON_STATE)

    @staticmethod
    def setHangarProgressionStateOff():
        SoundGroups.g_instance.setState(SoundsStateKeys.HANGAR_PROGRESSION_STATE, SoundsStateKeys.HANGAR_PROGRESSION_OFF_STATE)

    def isVehicleGOForOperationReady(self, operationID):
        return all(self.__getVehicleGOForOperation(operationID))

    def isSwitchingToTopCameraNeeded(self):
        cameraManager = self.getCameraManager()
        if not cameraManager:
            _logger.warning('[PM3.0] CameraManager is not found')
            return
        topCameras = [CameraNameTemplates.TOP.format(self.__operationID, TopCameras.FIRST), CameraNameTemplates.TOP.format(self.__operationID, TopCameras.SECOND)]
        return cameraManager.getCurrentCameraName() not in topCameras

    def isSwitchingToFreeCameraNeeded(self):
        cameraManager = self.getCameraManager()
        if not cameraManager:
            _logger.warning('[PM3.0] CameraManager is not found')
            return
        return not cameraManager.getCurrentCameraName() == CameraNameTemplates.FREE.format(self.__operationID)

    def __activateVehicleGO(self):
        if self.__vehicleGO:
            self.assembleObtainedStages()
            self.__vehicleGO.activate()

    def __switchByCameraName(self, cameraName, instantly=False, callback=None):
        cameraManager = self.getCameraManager()
        if not cameraManager:
            _logger.warning('[PM3.0] CameraManager is not found')
            return
        else:
            if not instantly:
                self.onCameraFlightStarted()
            if callback is not None:
                self.__cameraSwitchingCallback = callback
            currentCameraName = cameraManager.getCurrentCameraName()
            if currentCameraName == cameraName:
                cameraManager.resetCameraTarget(CAMERA_IMMEDIATE_TRANSITION_DURATION)
                self.__onCameraSwitched(None)
            else:
                freeCameraName = CameraNameTemplates.FREE.format(self.__operationID)
                if currentCameraName == freeCameraName:
                    self.setHangarProgressionStateOn()
                elif cameraName == freeCameraName:
                    self.setHangarProgressionStateOff()
                if not instantly:
                    SoundGroups.g_instance.playSound2D(SoundsKeys.SWITCH_CAMERA_EVENT)
                cameraManager.switchByCameraName(cameraName, instantly=instantly)
            return

    def __getVehicleGOForOperation(self, operationID):
        manager = self.getHangarOperationsManager()
        vehicleGO = None
        vehicleStagesComponent = None
        if not manager:
            _logger.warning('[PM3.0] HangarOperationsManager is not found')
            return (vehicleGO, vehicleStagesComponent)
        else:
            if operationID == OperationIDs.OPERATION_FIRST:
                vehicleGO, vehicleStagesComponent = manager.vehicleForOperation8, manager.stagesComponentForOperation8
            elif operationID == OperationIDs.OPERATION_SECOND:
                vehicleGO, vehicleStagesComponent = manager.vehicleForOperation9, manager.stagesComponentForOperation9
            elif operationID == OperationIDs.OPERATION_THIRD:
                vehicleGO, vehicleStagesComponent = manager.vehicleForOperation10, manager.stagesComponentForOperation10
            return (vehicleGO, vehicleStagesComponent)

    def __setAndActivateVehicleGO(self, vehicleGOForOperation, vehicleStagesComponent, operationID, currentStage):
        self.__vehicleGO, self.__vehicleStagesComponent = vehicleGOForOperation, vehicleStagesComponent
        self.__operationID = operationID
        self.__currentStage = currentStage
        self.__activateVehicleGO()

    def __getStage(self, stageNumber, isFade=False):
        if not self.__vehicleStagesComponent:
            _logger.warning('[PM3.0] AssemblingStagesComponent is not found')
            return
        stageKey = 'stage_{}_fade' if isFade else 'stage_{}'
        stage = getattr(self.__vehicleStagesComponent, stageKey.format(stageNumber))
        if not (stage and stage.isValid()):
            if not isFade:
                _logger.warning('[PM3.0] GO for %s is not found or invalid', stageKey.format(stageNumber))
            return
        return stage

    def __getStageAddition(self, additionKey):
        if not self.__vehicleStagesComponent:
            _logger.warning('[PM3.0] AssemblingStagesComponent is not found')
            return
        addition = getattr(self.__vehicleStagesComponent, additionKey)
        if not (addition and addition.isValid()):
            _logger.warning('[PM3.0] GO for %s is not found or invalid', additionKey)
            return
        return addition

    def __activateStages(self, stageNumber):
        stageInfo = STAGES_CONFIG[self.__operationID][stageNumber]
        for activeStageNumber in self.__activeComponents.stages.difference(stageInfo.stages):
            self.__deactivateStage(activeStageNumber)

        for activeAddition in self.__activeComponents.additions.difference(stageInfo.additions):
            self.__deactivateAddition(activeAddition)

        for stage in stageInfo.stages:
            self.__activateStage(stage)

        for addition in stageInfo.additions:
            self.__activateAddition(addition)

    def __activateStage(self, stageNumber):
        stage = self.__getStage(stageNumber)
        if stage:
            stage.activate()
            self.__activeComponents.stages.add(stageNumber)

    def __deactivateStage(self, stageNumber):
        stage = self.__getStage(stageNumber)
        if stage:
            stage.deactivate()
            if stageNumber in self.__activeComponents.stages:
                self.__activeComponents.stages.remove(stageNumber)

    def __activateAddition(self, additionKey):
        addition = self.__getStageAddition(additionKey)
        if addition:
            addition.activate()
            self.__activeComponents.additions.add(additionKey)

    def __deactivateAddition(self, additionKey):
        addition = self.__getStageAddition(additionKey)
        if addition:
            addition.deactivate()
            if additionKey in self.__activeComponents.additions:
                self.__activeComponents.additions.remove(additionKey)

    def __activateStageFade(self, stageFade):
        sequence = stageFade.findComponentByType(Sequence)
        if sequence:
            self.__hangarOperationsManager.addTimer('assemblingAnimation_{}'.format(self.__stageNumberForAssembling), sequence.duration, self.__onAnimationFinished)
            soundEvent = SoundsKeys.PLAY_ANIMATION_EVENT % (self.__operationID, self.__stageNumberForAssembling)
            SoundGroups.g_instance.playSound2D(soundEvent)
            stageFade.activate()
            sequence.start()

    def __deactivateStageFade(self):
        if self.__stageFade and self.__stageFade.isValid():
            self.__stageFade.deactivate()
            self.__stageFade = None
        else:
            _logger.warning('[PM3.0] GO for %s is not found or invalid', 'stage_{}_fade'.format(self.__stageNumberForAssembling))
        return

    def __onAnimationFinished(self):
        self.__deactivateStageFade()
        self.__activateStages(self.__stageNumberForAssembling)
        self.onAssemblingAnimationFinished()

    def __onVideoFinished(self):
        self.__activateStages(self.__stageNumberForAssembling)
        self.onAssemblingVideoFinished(self.__stageNumberForAssembling)

    def __onCameraSwitched(self, _):
        self.onCameraFlightFinished()
        if self.__cameraSwitchingCallback is not None:
            self.__cameraSwitchingCallback()
            self.__cameraSwitchingCallback = None
        return

    @staticmethod
    def __onMoveSpace(args=None):
        if args is None:
            return
        else:
            ctx = {'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            return

    @staticmethod
    def __onMouseOver3dScene(args):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': bool(args.get('isOver3dScene'))}))
