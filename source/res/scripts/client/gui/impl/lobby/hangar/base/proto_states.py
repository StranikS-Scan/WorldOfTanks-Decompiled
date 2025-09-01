# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/base/proto_states.py
from __future__ import absolute_import
import logging
import typing
import adisp
from BWUtil import AsyncReturn
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.game_control.loadout_controller import updateInteractor
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.random.sound_manager import ALL_VEHICLES_SOUND_SPACE
from gui.impl.lobby.tank_setup.tank_setup_sounds import playEnterTankSetupView, playExitTankSetupView
from gui.lobby_state_machine.states import SFViewLobbyState, LobbyState, LobbyStateDescription, TopScopeTopLayerState, SubScopeSubLayerState, LobbyStateFlags
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.game_control import ILoadoutController
from skeletons.gui.lobby_context import ILobbyContext
from sound_gui_manager import ViewSoundExtension
from wg_async import await_callback, wg_async, BrokenPromiseError, wg_await
_logger = logging.getLogger(__name__)

class _HangarStatePrototype(SFViewLobbyState):
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_HANGAR)


class _DefaultHangarStatePrototype(LobbyState):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.hangar()))


class _AllVehiclesStatePrototype(LobbyState):
    __soundExtension = ViewSoundExtension(ALL_VEHICLES_SOUND_SPACE)

    def _onEntered(self, event):
        super(_AllVehiclesStatePrototype, self)._onEntered(event)
        self.__soundExtension.initSoundManager()
        self.__soundExtension.startSoundSpace()

    def _onExited(self):
        self.__soundExtension.destroySoundManager()
        super(_AllVehiclesStatePrototype, self)._onExited()

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.allVehicles()))


class _LoadoutStatePrototype(LobbyState):
    __loadoutController = dependency.descriptor(ILoadoutController)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.loadout()))

    def _onEntered(self, event):
        super(_LoadoutStatePrototype, self)._onEntered(event)
        playEnterTankSetupView()

    @wg_async
    def _onExited(self):
        yield await_callback(self.__loadoutController.interactor.applyQuit)(skipApplyAutoRenewal=False)
        playExitTankSetupView()
        super(_LoadoutStatePrototype, self)._onExited()


class _LoadoutConfirmStatePrototype(LobbyState):
    __loadoutController = dependency.instance(ILoadoutController)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_LoadoutConfirmStatePrototype, self).__init__(flags)
        self.__dialog = None
        return

    def getNavigationDescription(self):
        return None

    @wg_async
    def waitForResult(self):
        result = yield self.__dialog()
        raise AsyncReturn(result.result)

    @wg_async
    def _onEntered(self, event):
        super(_LoadoutConfirmStatePrototype, self)._onEntered(event)
        interactor = self.__loadoutController.interactor
        self.__dialog = interactor.showExitConfirmDialog
        if event.targetStateID != self.getStateID():
            try:
                result = yield self.__dialog()
                if not result.result:
                    TopScopeTopLayerState.goTo()
                    return
                confirmed, data = result.result
                rollback = data.get('rollBack', False)
                proceed = confirmed or rollback
                yield updateInteractor(interactor, confirmed, rollback)
                if proceed:
                    self.getMachine().post(event)
                else:
                    TopScopeTopLayerState.goTo()
            except BrokenPromiseError:
                _logger.debug('%r dialog closed without user decision.', self.__class__.__name__)

    def _onExited(self):
        super(_LoadoutConfirmStatePrototype, self)._onExited()
        self.__dialog = None
        return


class _LoadoutSectionStatePrototype(LobbyState, EventsHandler):
    __loadoutController = dependency.descriptor(ILoadoutController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __RESTRICTED_EVENTS = [events.PrbInvitesEvent.ACCEPT, events.PrbActionEvent.SELECT, events.PrbActionEvent.LEAVE]

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_LoadoutSectionStatePrototype, self).__init__(flags=flags)
        self.__cachedParams = {}

    def serializeParams(self):
        return self.__cachedParams

    def _getRestrictions(self):
        return ((event, self.__handleRestrictedEvent, EVENT_BUS_SCOPE.LOBBY) for event in self.__RESTRICTED_EVENTS)

    def _interactorConfirm(self, event):
        interactorHasChanged = self.__loadoutController.interactor.hasChanged()
        if event is None:
            return interactorHasChanged
        else:
            targetingSelf = event.targetStateID == self.getStateID()
            return not targetingSelf and interactorHasChanged

    def _getConfirmationState(self):
        return self.getMachine().getStateByID(self.STATE_ID)

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(_LoadoutSectionStatePrototype, self)._onEntered(event)
        self.__lobbyContext.addPlatoonCreationConfirmator(self.__confirmatorWrapper)
        self.__lobbyContext.addHeaderNavigationConfirmator(self.__confirmatorWrapper)

    def _onExited(self):
        self.__cachedParams = {}
        super(_LoadoutSectionStatePrototype, self)._onExited()
        self.__lobbyContext.deletePlatoonCreationConfirmator(self.__confirmatorWrapper)
        self.__lobbyContext.deleteHeaderNavigationConfirmator(self.__confirmatorWrapper)

    @wg_async
    def __handleRestrictedEvent(self, event=None):
        interactor = self.__loadoutController.interactor
        if not self._interactorConfirm(event):
            SubScopeSubLayerState.goTo()
            raise AsyncReturn(True)
        state = self._getConfirmationState()
        state.goTo()
        try:
            confirmed, data = yield state.waitForResult()
            rollback = data.get('rollBack', False)
            self.proceed = confirmed or rollback
            yield updateInteractor(interactor, confirmed, rollback)
            if self.proceed:
                SubScopeSubLayerState.goTo()
            else:
                TopScopeTopLayerState.goTo()
        except BrokenPromiseError:
            self.proceed = False

        raise AsyncReturn(self.proceed)

    @adisp.adisp_async
    @wg_async
    def __confirmatorWrapper(self, callback):
        result = yield wg_await(self.__handleRestrictedEvent())
        callback(result)


class _ShellsLoadoutStatePrototype(LobbyState):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.loadout.shells()))


class _EquipmentLoadoutStatePrototype(LobbyState):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.loadout.equipment()))


class _InstructionsLoadoutStatePrototype(LobbyState):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.loadout.instructions()))


class _ConsumablesLoadoutStatePrototype(LobbyState):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.loadout.consumables()))


def generateBasicLoadoutStateClasses(parentHangarStateCls, loadoutResource, loadoutStatePrototypeCls=_LoadoutStatePrototype, confirmStatePrototypeCls=_LoadoutConfirmStatePrototype, sectionStatePrototypeCls=_LoadoutSectionStatePrototype, shellsStatePrototypeCls=_ShellsLoadoutStatePrototype, equipmentStatePrototypeCls=_EquipmentLoadoutStatePrototype, instructionsStatePrototypeCls=_InstructionsLoadoutStatePrototype, consumablesStatePrototypeCls=_ConsumablesLoadoutStatePrototype):

    @parentHangarStateCls.parentOf
    class GeneratedLoadoutState(loadoutStatePrototypeCls):
        STATE_ID = loadoutStatePrototypeCls.STATE_ID or 'loadout'

        def registerStates(self):
            lsm = self.getMachine()
            lsm.addState(GeneratedShellsLoadoutState(flags=StateFlags.INITIAL))
            lsm.addState(GeneratedEquipmentLoadoutState())
            lsm.addState(GeneratedInstructionsLoadoutState())
            lsm.addState(GeneratedConsumablesLoadoutState())
            lsm.addState(GeneratedLoadoutConfirmState())
            super(GeneratedLoadoutState, self).registerStates()

        def registerTransitions(self):
            lsm = self.getMachine()
            lsm.addNavigationTransitionFromParent(self)
            generatedClasses = (lsm.getStateByCls(GeneratedShellsLoadoutState),
             lsm.getStateByCls(GeneratedEquipmentLoadoutState),
             lsm.getStateByCls(GeneratedInstructionsLoadoutState),
             lsm.getStateByCls(GeneratedConsumablesLoadoutState))
            parent = self.getParent()
            for state in generatedClasses:
                parent.addNavigationTransition(state)
                lsm.addNavigationTransitionFromParent(state)
                state.addNavigationTransition(state, transitionType=TransitionType.EXTERNAL)

            super(GeneratedLoadoutState, self).registerTransitions()

    @TopScopeTopLayerState.parentOf
    class GeneratedLoadoutConfirmState(confirmStatePrototypeCls):
        STATE_ID = confirmStatePrototypeCls.STATE_ID or 'loadoutConfirmLeave'

    class GeneratedLoadoutSectionState(sectionStatePrototypeCls):

        def registerTransitions(self):
            self.addGuardTransition(self._getConfirmationState(), WeakMethodProxy(self._interactorConfirm))

        def _getConfirmationState(self):
            lsm = self.getMachine()
            return lsm.getStateByCls(GeneratedLoadoutConfirmState)

    @GeneratedLoadoutState.parentOf
    class GeneratedShellsLoadoutState(GeneratedLoadoutSectionState, shellsStatePrototypeCls):
        STATE_ID = shellsStatePrototypeCls.STATE_ID or 'shells'

    @GeneratedLoadoutState.parentOf
    class GeneratedEquipmentLoadoutState(GeneratedLoadoutSectionState, equipmentStatePrototypeCls):
        STATE_ID = equipmentStatePrototypeCls.STATE_ID or 'equipment'

    @GeneratedLoadoutState.parentOf
    class GeneratedInstructionsLoadoutState(GeneratedLoadoutSectionState, instructionsStatePrototypeCls):
        STATE_ID = instructionsStatePrototypeCls.STATE_ID or 'instructions'

    @GeneratedLoadoutState.parentOf
    class GeneratedConsumablesLoadoutState(GeneratedLoadoutSectionState, consumablesStatePrototypeCls):
        STATE_ID = consumablesStatePrototypeCls.STATE_ID or 'consumables'

    return (GeneratedLoadoutState,
     GeneratedLoadoutConfirmState,
     GeneratedLoadoutSectionState,
     GeneratedShellsLoadoutState,
     GeneratedEquipmentLoadoutState,
     GeneratedInstructionsLoadoutState,
     GeneratedConsumablesLoadoutState)


def generateBasicHangarStateClasses(parentStateCls, hangarResource, hangarPrototypeCls=_HangarStatePrototype, defaultHangarPrototypeCls=_DefaultHangarStatePrototype, allVehiclesPrototypeCls=_AllVehiclesStatePrototype):

    @parentStateCls.parentOf
    class GeneratedHangarState(hangarPrototypeCls):
        STATE_ID = hangarPrototypeCls.STATE_ID or 'hangar'

        def __init__(self, flags=StateFlags.UNDEFINED):
            super(GeneratedHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

        def registerStates(self):
            lsm = self.getMachine()
            lsm.addState(GeneratedDefaultHangarState(flags=StateFlags.INITIAL))
            lsm.addState(GeneratedAllVehiclesState())
            super(GeneratedHangarState, self).registerStates()

        def registerTransitions(self):
            lsm = self.getMachine()
            lsm.addNavigationTransitionFromParent(lsm.getStateByCls(GeneratedDefaultHangarState))
            lsm.addNavigationTransitionFromParent(lsm.getStateByCls(GeneratedAllVehiclesState))
            super(GeneratedHangarState, self).registerTransitions()

    @GeneratedHangarState.parentOf
    class GeneratedDefaultHangarState(defaultHangarPrototypeCls):
        STATE_ID = defaultHangarPrototypeCls.STATE_ID or '{root}'

        def __init__(self, flags=StateFlags.UNDEFINED):
            super(GeneratedDefaultHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

    @GeneratedHangarState.parentOf
    class GeneratedAllVehiclesState(allVehiclesPrototypeCls):
        STATE_ID = allVehiclesPrototypeCls.STATE_ID or 'allVehicles'

    return (GeneratedHangarState, GeneratedDefaultHangarState, GeneratedAllVehiclesState)
