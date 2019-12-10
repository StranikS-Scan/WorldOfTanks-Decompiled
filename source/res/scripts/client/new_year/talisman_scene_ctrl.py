# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/talisman_scene_ctrl.py
import logging
import weakref
import math
import BigWorld
import Math
import GUI
import Keys
from AvatarInputHandler.cameras import FovExtended
from NewYearTalismanBaseObject import NewYearTalismanBaseObject
from adisp import process
from async import await, async
from frameworks.state_machine import StateMachine, State, StateFlags, StringEventTransition, StringEvent
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.app_loader import sf_lobby
from gui.impl.dialogs.dialogs import showNYTalismanGiftDialog
from gui.impl.new_year.dialogs.new_year_talisman_select_confirm_dialog import NewYearTalismanSelectConfirmDialog
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.views.new_year_talisman_select_view import NewYearTalismanSelectViewWindow
from gui.impl.new_year.sound_rtpc_controller import SoundRTPCController
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from new_year.ny_constants import AnchorNames
from new_year.ny_processor import AddTalismanProcessor
from shared_utils import first
from skeletons.gui.impl import IOverlaysManager
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import ITalismanSceneController, INewYearController
from gui.shared.utils import decorators
from gui import g_keyEventHandlers
_logger = logging.getLogger(__name__)

class _AnimationState(object):

    class Preview(object):
        SHOW = 'show'
        SHOW_CONGRATS = 'show_congrats'
        SHOW_ACTION = 'show_action'
        HIDE = 'hide'

    class Gift(object):
        SHOW_HANGAR_IDLE = 'show_hangar_idle'
        SHOW_GIFT_IDLE = 'show_gift_idle'
        SHOW_CONFIRM = 'show_confirmation'
        SHOW_CONGRATS_WITHOUT_GIFT = 'show_congrats_without_gift'
        SHOW_CONGRATS_WITH_GIFT = 'show_congrats_with_gift'


_PREVIEW_CAMERA_NAME = 'previewCamera'
_VISIBLE_CONTAINERS = (APP_CONTAINERS_NAMES.OVERLAY,
 APP_CONTAINERS_NAMES.CURSOR,
 APP_CONTAINERS_NAMES.TOOL_TIPS,
 APP_CONTAINERS_NAMES.WAITING,
 APP_CONTAINERS_NAMES.SERVICE_LAYOUT)

class _StateID(object):
    INITIAL = 'init'
    SWITCHING_TO_HANGAR = 'switching.to.hangar'
    SWITCHING_TO_CHRISTMAS_TREE = 'switching.to.tree'
    SWITCHING_TO_GIFT = 'switching.to.gift'
    PREVIEW = 'preview'
    PREVIEW_SWITCHING = 'preview.switching'
    PREVIEW_WITH_UI = 'preview.ui'
    PREVIEW_MOVING_TO_TALISMAN = 'preview.moving.to.talisman'
    PREVIEW_CONFIRMATION = 'preview.confirmation'
    PREVIEW_MOVING_BACK = 'preview.moving.back'
    PREVIEW_CONGRATS = 'preview.congrats'
    GIFT_MOVING_TO_TALISMAN = 'gift.moving.to.talisman'
    GIFT_CONFIRMATION = 'gift.confirmation'
    GIFT_MOVING_BACK = 'gift.moving.back'


class _EventID(object):
    GO_TO_INITIAL = 'go.to.initial'
    SWITCH_TO_HANGAR = 'switch.to.hangar'
    SWITCH_TO_CHRISTMAS_TREE = 'switch.to.tree'
    SWITCH_TO_GIFT = 'switch.to.gift'
    SWITCH_TO_PREVIEW = 'preview.switch'
    PREVIEW_SHOW_UI = 'preview.show.UI'
    PREVIEW_MOVE_TO_TALISMAN = 'preview.move.to'
    PREVIEW_SHOW_CONFIRM = 'preview.show.confirm'
    PREVIEW_MOVE_BACK = 'preview.move.back'
    SHOW_CONGRATS = 'show.congrats'
    GIFT_MOVE_TO_TALISMAN = 'gift.move.to.talisman'
    GIFT_SHOW_CONFIRM = 'gift.show.confirm'
    GIFT_MOVE_BACK = 'gift.move.back'


class _TalismanStateMachine(StateMachine):
    __slots__ = ('__camera', '__savedCamera', '__savedOptimizationFlag', '__dofHelper', '__savedFov')
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(_TalismanStateMachine, self).__init__()
        self.__camera = None
        self.__savedCamera = None
        self.__savedOptimizationFlag = False
        self.__dofHelper = None
        self.__savedFov = 0.0
        return

    def stop(self):
        self.__camera = None
        if self.__savedCamera is not None:
            self.restoreHangar(force=True)
            self.__savedCamera = None
        super(_TalismanStateMachine, self).stop()
        return

    def configure(self):
        self.__camera = BigWorld.FreeCamera()
        initial = State(stateID=_StateID.INITIAL, flags=StateFlags.INITIAL)
        switchingToHangar = _SwitchingToHangarState()
        switchingToGift = _SwitchingToGiftState()
        switchToTree = _SwitchingToChristmasTreeState()
        preview = _PreviewMainState()
        previewSwitching = _PreviewSwitchingState()
        previewWithUI = _PreviewWithUIState()
        previewMovingToTalisman = _PreviewMovingToTalismanState()
        previewConfirmation = _PreviewConfirmationState()
        previewMovingBack = _PreviewMovingBackState()
        previewCongrats = _PreviewCongratsState()
        preview.addChildState(previewSwitching)
        preview.addChildState(previewWithUI)
        preview.addChildState(previewMovingToTalisman)
        preview.addChildState(previewConfirmation)
        preview.addChildState(previewMovingBack)
        preview.addChildState(previewCongrats)
        giftMovingToTalisman = _GiftMovingToTalismanState()
        giftConfirmation = _GiftConfirmationState()
        giftMovingBack = _GiftMovingBackState()
        initial.addTransition(StringEventTransition(_EventID.SWITCH_TO_PREVIEW), target=previewSwitching)
        initial.addTransition(StringEventTransition(_EventID.GIFT_MOVE_TO_TALISMAN), target=giftMovingToTalisman)
        previewSwitching.addTransition(StringEventTransition(_EventID.PREVIEW_SHOW_UI), target=previewWithUI)
        previewWithUI.addTransition(StringEventTransition(_EventID.PREVIEW_MOVE_TO_TALISMAN), target=previewMovingToTalisman)
        previewMovingToTalisman.addTransition(StringEventTransition(_EventID.PREVIEW_SHOW_CONFIRM), target=previewConfirmation)
        previewConfirmation.addTransition(StringEventTransition(_EventID.PREVIEW_MOVE_BACK), target=previewMovingBack)
        previewConfirmation.addTransition(StringEventTransition(_EventID.SWITCH_TO_HANGAR), target=switchingToHangar)
        previewConfirmation.addTransition(StringEventTransition(_EventID.SHOW_CONGRATS), target=previewCongrats)
        previewCongrats.addTransition(StringEventTransition(_EventID.SWITCH_TO_GIFT), target=switchingToGift)
        previewMovingBack.addTransition(StringEventTransition(_EventID.PREVIEW_SHOW_UI), target=previewWithUI)
        previewWithUI.addTransition(StringEventTransition(_EventID.SWITCH_TO_HANGAR), target=switchingToHangar)
        switchingToHangar.addTransition(StringEventTransition(_EventID.GO_TO_INITIAL), target=initial)
        switchingToGift.addTransition(StringEventTransition(_EventID.GO_TO_INITIAL), target=initial)
        giftMovingToTalisman.addTransition(StringEventTransition(_EventID.GIFT_SHOW_CONFIRM), target=giftConfirmation)
        giftConfirmation.addTransition(StringEventTransition(_EventID.GIFT_MOVE_BACK), target=giftMovingBack)
        giftConfirmation.addTransition(StringEventTransition(_EventID.SWITCH_TO_CHRISTMAS_TREE), target=switchToTree)
        giftMovingBack.addTransition(StringEventTransition(_EventID.GO_TO_INITIAL), target=initial)
        switchToTree.addTransition(StringEventTransition(_EventID.GO_TO_INITIAL), target=initial)
        self.addState(initial)
        self.addState(switchingToHangar)
        self.addState(switchingToGift)
        self.addState(switchToTree)
        self.addState(preview)
        self.addState(giftMovingToTalisman)
        self.addState(giftConfirmation)
        self.addState(giftMovingBack)

    def prepareHangar(self, dofParams, fov):
        self.__savedCamera = BigWorld.camera()
        self.__dofHelper = BigWorld.PyCustomizationHelper(None, 0, False, None)
        self.__dofHelper.setDOFparams(*dofParams)
        self.__dofHelper.setDOFenabled(True)
        self.__savedFov = FovExtended.instance().getLastSetHorizontalFov()
        FovExtended.instance().setFovByAbsoluteValue(fov)
        self.__hideHangarUI()
        return

    def restoreHangar(self, force=False):
        if force and self.__hangarSpace.space is not None and self.__hangarSpace.space.camera:
            self.__savedCamera = self.__hangarSpace.space.camera
        BigWorld.camera(self.__savedCamera)
        self.__savedCamera = None
        if self.__dofHelper is not None:
            self.__dofHelper.setDOFenabled(False)
            self.__dofHelper = None
        if force:
            FovExtended.instance().resetFov()
        else:
            FovExtended.instance().setFovByAbsoluteValue(self.__savedFov)
        self.__restoreHangarUI()
        return

    def getCamera(self):
        return self.__camera

    @sf_lobby
    def __app(self):
        return None

    def __hideHangarUI(self):
        optimizer = GUI.WGUIOptimizer()
        self.__savedOptimizationFlag = optimizer.getEnable()
        optimizer.setEnable(False)
        if self.__app is not None and self.__app.containerManager is not None:
            self.__app.containerManager.as_storeContainersVisibleS()
            self.__app.containerManager.as_setContainersVisibleS(False, _VISIBLE_CONTAINERS)
        return

    def __restoreHangarUI(self):
        GUI.WGUIOptimizer().setEnable(self.__savedOptimizationFlag)
        if self.__app is not None and self.__app.containerManager is not None:
            self.__app.containerManager.as_setContainersVisibleS(True, _VISIBLE_CONTAINERS)
        return


class _TalismanState(State):
    __slots__ = ()
    _talismanController = dependency.descriptor(ITalismanSceneController)

    @sf_lobby
    def _app(self):
        return None

    def _postEvent(self, eventID, **kwargs):
        machine = self.getMachine()
        if machine is not None:
            machine.post(StringEvent(eventID, **kwargs))
        return

    def _setGiftAnimation(self, talismanName, stateID):
        self._talismanController.setGiftAnimationState(talismanName, stateID)

    def _setPreviewAnimation(self, talismanName, stateID):
        self._talismanController.setPreviewAnimationState(talismanName, stateID)


class _HangarTransformState(_TalismanState):
    __slots__ = ()
    _newYearController = dependency.descriptor(INewYearController)

    def _hideHangarAndSetCamera(self, cameraDescriptor):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            dofParams = (cameraDescriptor.nearStart,
             cameraDescriptor.nearDist,
             cameraDescriptor.farStart,
             cameraDescriptor.farDist)
            machine.prepareHangar(dofParams, math.radians(cameraDescriptor.fov))
            self.__prepareCamera(cameraDescriptor)
            return

    def _restoreHangarAndCamera(self):
        machine = self.getMachine()
        if machine is not None:
            machine.restoreHangar()
        return

    def __prepareCamera(self, cameraDescriptor):
        m = Math.Matrix(cameraDescriptor.matrix)
        m.invert()
        camera = self.getMachine().getCamera()
        camera.set(m)
        BigWorld.camera(camera)


class _SwitchingToHangarState(_HangarTransformState):
    __slots__ = ()

    def __init__(self, stateID=_StateID.SWITCHING_TO_HANGAR):
        super(_SwitchingToHangarState, self).__init__(stateID=stateID)

    def _onEntered(self, _):
        self.__switchToHangar()

    @process
    def __switchToHangar(self):
        yield self._app.fadeManager.startFade()
        self._restoreHangarAndCamera()
        self.__hideTalismans()
        self._postEvent(_EventID.GO_TO_INITIAL)

    def __hideTalismans(self):
        for item in self._newYearController.getTalismans(isInInventory=False):
            self._setPreviewAnimation(item.getSetting(), _AnimationState.Preview.HIDE)


class _SwitchingToGiftState(_SwitchingToHangarState):
    __slots__ = ('__talismanName',)

    def __init__(self):
        super(_SwitchingToGiftState, self).__init__(stateID=_StateID.SWITCHING_TO_GIFT)
        self.__talismanName = None
        return

    def _onEntered(self, event):
        super(_SwitchingToGiftState, self)._onEntered(event)
        self.__talismanName = event.getArguments()['talismanName']

    def _onExited(self):
        NewYearNavigation.switchToTalismans()
        state = _AnimationState.Gift.SHOW_CONGRATS_WITHOUT_GIFT if self._newYearController.isTalismanToyTaken() else _AnimationState.Gift.SHOW_CONGRATS_WITH_GIFT
        self._setGiftAnimation(self.__talismanName, state)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_SET)


def _blockNonPreviewOverlays(overlay):
    return not isinstance(overlay, (NewYearTalismanSelectViewWindow, NewYearTalismanSelectConfirmDialog))


class _PreviewMainState(State):
    __overlays = dependency.descriptor(IOverlaysManager)

    def __init__(self):
        super(_PreviewMainState, self).__init__(_StateID.PREVIEW)

    def clear(self):
        self.__overlays.release()
        super(_PreviewMainState, self).clear()

    def _onEntered(self, event):
        self.__overlays.suspend(condition=_blockNonPreviewOverlays)

    def _onExited(self):
        self.__overlays.release()


class _PreviewSwitchingState(_HangarTransformState):
    __slots__ = ()

    def __init__(self):
        super(_PreviewSwitchingState, self).__init__(stateID=_StateID.PREVIEW_SWITCHING, flags=StateFlags.INITIAL)

    def _onEntered(self, event):
        descriptor = event.getArgument('previewCameraDescriptor')
        if descriptor is None:
            _logger.error('Preview camera descriptor has not been created!')
            return
        else:
            self.__switch(descriptor)
            return

    @process
    def __switch(self, previewCameraDescriptor):
        yield self._app.fadeManager.startFade()
        self._hideHangarAndSetCamera(previewCameraDescriptor)
        self.__showTalismans()
        self._postEvent(_EventID.PREVIEW_SHOW_UI)

    def __showTalismans(self):
        for item in self._newYearController.getTalismans(isInInventory=False):
            self._setPreviewAnimation(item.getSetting(), _AnimationState.Preview.SHOW)


class _PreviewWithUIState(_TalismanState):
    __slots__ = ('__window',)

    def __init__(self):
        super(_PreviewWithUIState, self).__init__(stateID=_StateID.PREVIEW_WITH_UI)
        self.__window = None
        return

    def clear(self):
        self.__destroyWindow()
        super(_PreviewWithUIState, self).clear()

    def _onEntered(self, _):
        self.__window = NewYearTalismanSelectViewWindow()
        self.__window.load()
        self._talismanController.setPreviewTalismansInteractive(True)

    def _onExited(self):
        self.__destroyWindow()

    def __destroyWindow(self):
        self._talismanController.setPreviewTalismansInteractive(False)
        if self.__window is None:
            return
        else:
            self.__window.destroy()
            self.__window = None
            return


class _PreviewMovementState(_TalismanState):
    __slots__ = ('__movement', '_arguments')

    def __init__(self, stateID):
        super(_PreviewMovementState, self).__init__(stateID=stateID)
        self.__movement = None
        self._arguments = None
        return

    def clear(self):
        self._arguments = None
        self.__clearMovement()
        super(_PreviewMovementState, self).clear()
        return

    def _onEntered(self, event):
        self._arguments = event.getArguments()
        self.__startMovement()

    def _getKeyFrames(self):
        raise NotImplementedError

    def _onMovementFinished(self):
        raise NotImplementedError

    def __startMovement(self):
        camera = self.getMachine().getCamera()
        m = Math.Matrix(camera.invViewMatrix)
        keyFrames = [(0.0, m)]
        keyFrames.extend(self._getKeyFrames())
        self.__movement = _CameraMovement()
        self.__movement.start(keyFrames, camera, self.__onMovementFinish)

    def __clearMovement(self):
        if self.__movement is None:
            return
        else:
            self.__movement.destroy()
            self.__movement = None
            return

    def __onMovementFinish(self):
        self.__clearMovement()
        self._onMovementFinished()


class _PreviewMovingToTalismanState(_PreviewMovementState):
    __slots__ = ()

    def __init__(self):
        super(_PreviewMovingToTalismanState, self).__init__(stateID=_StateID.PREVIEW_MOVING_TO_TALISMAN)

    def _onEntered(self, event):
        super(_PreviewMovingToTalismanState, self)._onEntered(event)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_ZOOM_IN)
        self._setPreviewAnimation(self._arguments['talismanName'], _AnimationState.Preview.SHOW_ACTION)

    def _getKeyFrames(self):
        cameraDescriptors = self._arguments['cameraDescriptors']
        keyFrames = []
        for cam in cameraDescriptors:
            m = Math.Matrix(cam.matrix)
            keyFrames.append((cam.time, m))

        return keyFrames

    def _onMovementFinished(self):
        self._postEvent(_EventID.PREVIEW_SHOW_CONFIRM, **self._arguments)


class _PreviewMovingBackState(_PreviewMovementState):
    __slots__ = ()

    def __init__(self, stateID=''):
        super(_PreviewMovingBackState, self).__init__(stateID or _StateID.PREVIEW_MOVING_BACK)

    def _getKeyFrames(self):
        cameraDescriptors = self._arguments['cameraDescriptors']
        previewCameraDescriptor = self._arguments['previewCameraDescriptor']
        keyFrames = []
        time = 0.0
        for cam in reversed(cameraDescriptors):
            time += cam.time
            pos = cameraDescriptors.index(cam)
            if pos:
                prevCam = cameraDescriptors[pos - 1]
                time -= prevCam.time
                m = Math.Matrix(prevCam.matrix)
            else:
                m = Math.Matrix(previewCameraDescriptor.matrix)
            keyFrames.append((time, m))

        return keyFrames

    def _onMovementFinished(self):
        self._postEvent(_EventID.PREVIEW_SHOW_UI)


class _PreviewConfirmationState(_TalismanState):
    __slots__ = ()

    def __init__(self):
        super(_PreviewConfirmationState, self).__init__(stateID=_StateID.PREVIEW_CONFIRMATION)

    def _onEntered(self, event):
        self.__addTalisman(event.getArguments())

    @decorators.process('updating')
    def __addTalisman(self, arguments):
        result = yield AddTalismanProcessor(arguments['talismanName']).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self._postEvent(_EventID.SWITCH_TO_HANGAR)
        elif result.success:
            self._postEvent(_EventID.SHOW_CONGRATS, **arguments)
        else:
            self._postEvent(_EventID.PREVIEW_MOVE_BACK, **arguments)
            NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_ZOOM_OUT)


class _PreviewCongratsState(_PreviewMovingBackState):
    __slots__ = ()

    def __init__(self):
        super(_PreviewCongratsState, self).__init__(stateID=_StateID.PREVIEW_CONGRATS)

    def _onMovementFinished(self):
        talismanName = self._arguments['talismanName']
        self._setPreviewAnimation(talismanName, _AnimationState.Preview.SHOW_CONGRATS)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_ACTIVATE)


class _GiftMovingToTalismanState(_HangarTransformState):
    __slots__ = ()

    def __init__(self):
        super(_GiftMovingToTalismanState, self).__init__(stateID=_StateID.GIFT_MOVING_TO_TALISMAN)

    def _onEntered(self, event):
        descriptor = event.getArgument('cameraDescriptor')
        talismanName = event.getArgument('talismanName')
        self.__switch(descriptor, talismanName)
        self._talismanController.setTalismansInteractive(False)

    @process
    def __switch(self, cameraDescriptor, talismanName):
        yield self._app.fadeManager.startFade()
        self._hideHangarAndSetCamera(cameraDescriptor)
        self._postEvent(_EventID.GIFT_SHOW_CONFIRM, talismanName=talismanName)


class _GiftConfirmationState(_TalismanState):
    __slots__ = ()

    def __init__(self):
        super(_GiftConfirmationState, self).__init__(stateID=_StateID.GIFT_CONFIRMATION)

    def _onEntered(self, event):
        talismanName = event.getArgument('talismanName')
        self._setGiftAnimation(talismanName, _AnimationState.Gift.SHOW_CONFIRM)
        self.__showDialog(talismanName)

    @async
    def __showDialog(self, talismanName):
        toTree = yield await(showNYTalismanGiftDialog(talismanName))
        if toTree:
            self._postEvent(_EventID.SWITCH_TO_CHRISTMAS_TREE)
        else:
            SoundRTPCController.updateGiftAvailabilityRTPC()
            self._postEvent(_EventID.GIFT_MOVE_BACK, talismanName=talismanName)


class _GiftMovingBackState(_HangarTransformState):
    __slots__ = ()

    def __init__(self):
        super(_GiftMovingBackState, self).__init__(stateID=_StateID.GIFT_MOVING_BACK)

    def _onEntered(self, event):
        self.__switchBackToTalismans(event.getArgument('talismanName'))

    def _onExited(self):
        BigWorld.callback(self._app.fadeManager.CALLBACK_TIME, lambda : self._talismanController.setTalismansInteractive(True))

    @process
    def __switchBackToTalismans(self, talismanName):
        yield self._app.fadeManager.startFade()
        self._restoreHangarAndCamera()
        self.__changeAnimation(talismanName)
        self._postEvent(_EventID.GO_TO_INITIAL)

    def __changeAnimation(self, talismanName):
        if self._newYearController.isTalismanToyTaken():
            for item in self._newYearController.getTalismans(isInInventory=True):
                self._setGiftAnimation(item.getSetting(), _AnimationState.Gift.SHOW_HANGAR_IDLE)

        else:
            self._setGiftAnimation(talismanName, _AnimationState.Gift.SHOW_GIFT_IDLE)


class _SwitchingToChristmasTreeState(_HangarTransformState):
    __slots__ = ()

    def __init__(self):
        super(_SwitchingToChristmasTreeState, self).__init__(stateID=_StateID.SWITCHING_TO_CHRISTMAS_TREE)

    def _onEntered(self, _):
        self.__restore()

    def _onExited(self):
        NewYearNavigation.switchToTree()
        for item in self._newYearController.getTalismans(isInInventory=True):
            self._setGiftAnimation(item.getSetting(), _AnimationState.Gift.SHOW_HANGAR_IDLE)

        self._talismanController.setTalismansInteractive(True)

    @process
    def __restore(self):
        yield self._app.fadeManager.startFade()
        self._restoreHangarAndCamera()
        self._postEvent(_EventID.GO_TO_INITIAL)


class TalismanSceneController(ITalismanSceneController):
    __newYearController = dependency.descriptor(INewYearController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(TalismanSceneController, self).__init__()
        self.__selectedEntity = None
        self.__machine = _TalismanStateMachine()
        self.__talismans = {}
        self.__cameras = {}
        self.__previewTalismans = {}
        self.__previewCameras = {}
        self.__isOver3dScene = False
        self.__isGiftTaken = False
        return

    def init(self):
        g_keyEventHandlers.add(self.__handleKeyEvent)

    def fini(self):
        self.__clear()
        g_keyEventHandlers.remove(self.__handleKeyEvent)

    def onLobbyInited(self, event):
        self.__machine.configure()
        self.__machine.start()
        self.__isGiftTaken = self.__newYearController.isTalismanToyTaken()
        self.__newYearController.onStateChanged += self.__onStateChanged
        self.__newYearController.onDataUpdated += self.__onDataUpdated
        self.__hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.__hangarSpace.onMouseEnter += self.__onMouseEnter
        self.__hangarSpace.onMouseExit += self.__onMouseExit
        self.__hangarSpace.onNotifyCursorOver3dScene += self.__onNotifyCursorOver3dScene
        if self.__app is not None and self.__app.containerManager is not None:
            self.__app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        return

    def onDisconnected(self):
        self.__clear()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def hasTalismanGiftBubble(self):
        nyController = self.__newYearController
        hasGift = nyController.getTalismans(isInInventory=True) and not nyController.isTalismanToyTaken()
        return bool(hasGift)

    def switchToPreview(self):
        previewCameraDescriptor = first(self.__previewCameras.get(_PREVIEW_CAMERA_NAME, []))
        if previewCameraDescriptor is None:
            _logger.error('Preview Camera for selection screen is not set!')
            return
        else:
            self.__machine.post(StringEvent(_EventID.SWITCH_TO_PREVIEW, previewCameraDescriptor=previewCameraDescriptor))
            return

    def switchToHangar(self):
        self.__machine.post(StringEvent(_EventID.SWITCH_TO_HANGAR))

    def previewMoveTo(self, talismanName):
        cameraDescriptors = self.__previewCameras.get(talismanName, [])
        previewCameraDescriptor = first(self.__previewCameras.get(_PREVIEW_CAMERA_NAME, []))
        self.__machine.post(StringEvent(_EventID.PREVIEW_MOVE_TO_TALISMAN, cameraDescriptors=cameraDescriptors, previewCameraDescriptor=previewCameraDescriptor, talismanName=talismanName))

    def previewCongratsFinished(self, talismanName):
        self.__machine.post(StringEvent(_EventID.SWITCH_TO_GIFT, talismanName=talismanName))

    def giftMoveTo(self, talismanName):
        if talismanName not in self.__cameras:
            _logger.error('Can not move camera to %s', talismanName)
            return
        camera = self.__cameras[talismanName]
        self.__machine.post(StringEvent(_EventID.GIFT_MOVE_TO_TALISMAN, cameraDescriptor=camera, talismanName=talismanName))

    def setGiftAnimationState(self, talismanName, stateID):
        if talismanName in self.__talismans:
            self.__talismans[talismanName].setAnimatorTrigger(stateID)

    def setPreviewAnimationState(self, talismanName, stateID):
        if talismanName in self.__previewTalismans:
            self.__previewTalismans[talismanName].setAnimatorTrigger(stateID)

    def talismanAdded(self, entity):
        talismanName = entity.talismanName
        if talismanName in self.__talismans:
            _logger.error('Talisman %s is already created!', talismanName)
        self.__talismans[talismanName] = weakref.proxy(entity)

    def talismanAnimatorStarted(self, talismanName):
        inventory = [ item.getSetting() for item in self.__newYearController.getTalismans(isInInventory=True) ]
        if talismanName in inventory:
            state = _AnimationState.Gift.SHOW_HANGAR_IDLE if self.__newYearController.isTalismanToyTaken() else _AnimationState.Gift.SHOW_GIFT_IDLE
            self.setGiftAnimationState(talismanName, state)

    def talismanRemoved(self, entity):
        self.__talismans.pop(entity.talismanName, None)
        return

    def cameraAdded(self, descriptor):
        if descriptor.groupName in self.__cameras:
            _logger.error('Camera for %s is already created!', descriptor.groupName)
        self.__cameras[descriptor.groupName] = descriptor

    def talismanPreviewAdded(self, entity):
        if entity.talismanName in self.__previewTalismans:
            _logger.error('TalismanPreview %s is already created!', entity.talismanName)
        self.__previewTalismans[entity.talismanName] = weakref.proxy(entity)

    def talismanPreviewRemoved(self, entity):
        self.__previewTalismans.pop(entity.talismanName, None)
        return

    def cameraPreviewAdded(self, descriptor):
        groupName = descriptor.groupName
        self.__previewCameras.setdefault(groupName, []).append(descriptor)
        self.__previewCameras[groupName].sort(key=lambda x: x.time)

    def mouseEventsAvailable(self):
        return self.__machine.isStateEntered(_StateID.PREVIEW_WITH_UI) or self.__isOver3dScene and NewYearNavigation.getCurrentObject() == AnchorNames.MASCOT

    def isInGiftConfirmState(self):
        return self.__machine.isStateEntered(_StateID.GIFT_CONFIRMATION)

    def setTalismansInteractive(self, isInteractive):
        for entity in self.__talismans.itervalues():
            if entity is not None:
                entity.setInteractive(isInteractive)

        return

    def setPreviewTalismansInteractive(self, isInteractive):
        for entity in self.__previewTalismans.itervalues():
            if entity is not None:
                entity.setInteractive(isInteractive)

        return

    def isInPreview(self):
        return self.__machine.isStateEntered(_StateID.PREVIEW)

    @sf_lobby
    def __app(self):
        return None

    def __clear(self):
        self.__machine.stop()
        self.__selectedEntity = None
        self.__talismans.clear()
        self.__cameras.clear()
        self.__previewTalismans.clear()
        self.__previewCameras.clear()
        self.__newYearController.onStateChanged -= self.__onStateChanged
        self.__newYearController.onDataUpdated -= self.__onDataUpdated
        self.__hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.__hangarSpace.onMouseEnter -= self.__onMouseEnter
        self.__hangarSpace.onMouseExit -= self.__onMouseExit
        self.__hangarSpace.onNotifyCursorOver3dScene -= self.__onNotifyCursorOver3dScene
        if self.__app is not None and self.__app.containerManager is not None:
            self.__app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        return

    def __onStateChanged(self):
        if not self.__newYearController.isEnabled():
            self.__machine.stop()
        elif not self.__machine.isRunning():
            self.__machine.configure()
            self.__machine.start()

    def __onDataUpdated(self, _):
        isGiftTaken = self.__newYearController.isTalismanToyTaken()
        if self.__isGiftTaken != isGiftTaken and isGiftTaken is False:
            inventory = [ item.getSetting() for item in self.__newYearController.getTalismans(isInInventory=True) ]
            for talismanName in inventory:
                self.setGiftAnimationState(talismanName, _AnimationState.Gift.SHOW_GIFT_IDLE)

        self.__isGiftTaken = isGiftTaken

    def __onViewAddedToContainer(self, _, pyEntity):
        isInitial = self.__machine.isStateEntered(_StateID.INITIAL)
        if not isInitial and pyEntity.alias in (VIEW_ALIAS.BATTLE_QUEUE, VIEW_ALIAS.LOBBY_HANGAR):
            self.__restartMachine()

    def __restartMachine(self):
        self.__machine.stop()
        self.__machine.configure()
        self.__machine.start()

    def __onSpaceDestroy(self, _):
        if not self.__machine.isStateEntered(_StateID.INITIAL):
            self.__restartMachine()
        self.__cameras.clear()
        self.__previewCameras.clear()

    def __onNotifyCursorOver3dScene(self, isOver3dScene):
        self.__isOver3dScene = isOver3dScene

    def __handleKeyEvent(self, event):
        if event.key == Keys.KEY_LEFTMOUSE:
            if event.isKeyDown():
                self.__onMouseDown()
            else:
                self.__onMouseUp()

    def __onMouseEnter(self, entity):
        if isinstance(entity, NewYearTalismanBaseObject):
            self.__selectedEntity = weakref.proxy(entity)
            entity.setHighlight(True)

    def __onMouseExit(self, entity):
        if isinstance(entity, NewYearTalismanBaseObject):
            self.__selectedEntity = None
            entity.setHighlight(False)
        return

    def __onMouseDown(self):
        pass

    def __onMouseUp(self):
        if self.__selectedEntity is not None:
            self.__selectedEntity.onMouseClick()
        return


class _CameraMovement(CallbackDelayer):

    def __init__(self):
        super(_CameraMovement, self).__init__()
        self.__matrixAnimation = None
        self.__finishCbk = None
        self.__hangarCam = None
        self.__finishTime = 0.0
        self.__finishMatrix = None
        return

    def start(self, keyFrames, hangarCam, finishCbk):
        self.__hangarCam = hangarCam
        self.__finishCbk = finishCbk
        self.__matrixAnimation = Math.MatrixAnimation()
        self.__matrixAnimation.keyframes = keyFrames
        self.__finishTime, self.__finishMatrix = keyFrames[-1]
        self.__matrixAnimation.time = 0.0
        self.delayCallback(0.0, self.__update)
        self.__hangarCam.invViewProvider = self.__matrixAnimation

    def destroy(self):
        self.stopCallback(self.__update)
        self.__matrixAnimation = None
        self.__finishCbk = None
        if self.__hangarCam is not None:
            self.__hangarCam.invViewProvider = None
            if self.__finishMatrix is not None:
                finishMatrix = Math.Matrix(self.__finishMatrix)
                finishMatrix.invert()
                self.__hangarCam.set(finishMatrix)
            self.__hangarCam = None
        self.__finishMatrix = None
        super(_CameraMovement, self).destroy()
        return

    def __update(self):
        if self.__matrixAnimation.time > self.__finishTime:
            self.stopCallback(self.__update)
            self.__finishCbk()
            return None
        else:
            return 0.0
