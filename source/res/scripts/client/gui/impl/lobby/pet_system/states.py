# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/states.py
import typing
import CGF
from Event import Event
from cgf_components.hangar_camera_manager import HangarCameraManager
from frameworks.state_machine import StateFlags, StateIdsObserver
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import LobbyStateDescription, SFViewLobbyState, SubScopeSubLayerState
from gui.shared.event_dispatcher import showPetInfoPage, showHangar
from gui.subhangar.subhangar_state_groups import CameraMover, SmoothCameraMover, SubhangarStateGroupConfig, SubhangarStateGroupConfigProvider, SubhangarStateGroups
from helpers import dependency
from helpers.events_handler import EventsHandler
from pet_system_common.pet_constants import PET_CAMERA_NAME
from skeletons.gui.game_control import IFadingController
from skeletons.gui.pet_system import IPetSystemController
from skeletons.gui.shared.utils import IHangarSpace
from wg_async import wg_async
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine

def registerStates(machine):
    machine.addState(PetStorageState())
    machine.addState(PetEventFullscreenWindowState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(PetStorageState))
    machine.addNavigationTransitionFromParent(machine.getStateByCls(PetEventFullscreenWindowState))


class PetStorageObserver(StateIdsObserver):

    def __init__(self):
        super(PetStorageObserver, self).__init__(PetStorageState.STATE_ID)
        self.onStorageEntered = Event()
        self.onStorageExited = Event()
        self.currentState = False

    def onEnterState(self, state, event):
        super(PetStorageObserver, self).onExitState(state, event)
        self.currentState = True
        self.onStorageEntered()

    def onExitState(self, state, event):
        super(PetStorageObserver, self).onExitState(state, event)
        self.currentState = False
        self.onStorageExited()

    def clear(self):
        super(PetStorageObserver, self).clear()
        self.onStorageEntered.clear()
        self.onStorageExited.clear()


@SubScopeSubLayerState.parentOf
class PetStorageState(SFViewLobbyState, EventsHandler, SubhangarStateGroupConfigProvider):
    STATE_ID = VIEW_ALIAS.PET_STORAGE
    VIEW_KEY = ViewKey(VIEW_ALIAS.PET_STORAGE)
    __petController = dependency.descriptor(IPetSystemController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PetStorageState, self).__init__(flags)
        self.__cameraMover = CameraMover()

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((SubhangarStateGroups.PetDenStorage,), self.__cameraMover)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pet_system.petStorage.title()), infos=(LobbyStateDescription.Info(onMoreInfoRequested=showPetInfoPage),))

    def compareParams(self, params, otherParams):
        return True

    @classmethod
    def goTo(cls, moveInstantly=True):
        inHangar = cls.__petController.canInteractInHangar
        super(PetStorageState, cls).goTo(inHangar=inHangar)

    def _onEntered(self, event):
        super(PetStorageState, self)._onEntered(event)
        self._subscribe()
        if event.params.get('inHangar', False):
            self.__cameraMover = SmoothCameraMover()
        else:
            self.__cameraMover = CameraMover()

    def _onExited(self):
        self._unsubscribe()
        super(PetStorageState, self)._onExited()

    def _getEvents(self):
        return ((self.__hangarSpace.onSpaceChanged, self.__onSpaceChanged),)

    def __onSpaceChanged(self):
        showHangar()


@SubScopeSubLayerState.parentOf
class PetEventFullscreenWindowState(SFViewLobbyState, EventsHandler):
    STATE_ID = VIEW_ALIAS.PET_EVENT_FULLSCREEN
    VIEW_KEY = ViewKey(VIEW_ALIAS.PET_EVENT_FULLSCREEN)
    hangarSpace = dependency.descriptor(IHangarSpace)
    fadeManager = dependency.descriptor(IFadingController)
    petController = dependency.descriptor(IPetSystemController)

    def _onEntered(self, event):
        super(PetEventFullscreenWindowState, self)._onEntered(event)
        self._subscribe()
        self.__switchCamera()
        self.petController.petProxy.openEventScreen()

    def _onExited(self):
        self._unsubscribe()
        self.__switchCamera(isExit=True)
        self.petController.petProxy.closeEventScreen()
        super(PetEventFullscreenWindowState, self)._onExited()

    @wg_async
    def __switchCamera(self, isExit=False):
        yield self.fadeManager.show(WindowLayer.OVERLAY)
        try:
            cameraManager = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
            if cameraManager:
                if not isExit:
                    cameraManager.switchByCameraName(PET_CAMERA_NAME, instantly=True)
                elif cameraManager.getCurrentCameraName() == PET_CAMERA_NAME:
                    cameraManager.switchToTank()
        finally:
            yield self.fadeManager.hide(WindowLayer.OVERLAY)

    def _getEvents(self):
        return ((self.hangarSpace.onSpaceChanged, self.__onSpaceChanged),)

    def __onSpaceChanged(self):
        showHangar()
