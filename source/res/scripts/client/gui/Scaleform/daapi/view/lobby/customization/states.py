# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/states.py
import logging
import math
import typing
import BigWorld
import adisp
from BWUtil import AsyncReturn
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags, visitor
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey, ViewKeyDynamic
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl import backport
from gui.lobby_state_machine.states import LobbyState, SFViewLobbyState, GuiImplViewLobbyState, UntrackedState, SubScopeSubLayerState, SubScopeTopLayerState, TopScopeTopLayerState, LobbyStateDescription
from gui.lobby_state_machine.transitions import NavigationTransition, GuardTransition
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import ResPureDialogBuilder
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showHangar
from gui.shared.events import NavigationEvent, LoadGuiImplViewEvent
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, SubhangarStateGroups, SubhangarStateGroupConfig
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.stricted_loading import makeCallbackWeak
from wg_async import wg_await, wg_async, BrokenPromiseError
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
_logger = logging.getLogger(__name__)

def registerStates(machine):
    machine.addState(CustomizationState())
    machine.addState(_CustomizationMidState())
    machine.addState(_CustomizationTopState())


def registerTransitions(machine):
    customization = machine.getStateByCls(CustomizationState)
    machine.addNavigationTransitionFromParent(customization)


@SubScopeSubLayerState.parentOf
class CustomizationState(LobbyState, EventsHandler, SubhangarStateGroupConfigProvider):
    STATE_ID = 'customization'
    __CAMERA_NAME = 'Customization'
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __c11n = dependency.descriptor(ICustomizationService)

    @classmethod
    def goTo(cls, vehInvID=None, callback=None, season=None, modeId=None, tabId=None, itemCD=None):
        super(CustomizationState, cls).goTo(vehInvID=vehInvID, callback=callback, season=season, modeId=modeId, tabId=tabId, itemCD=itemCD)

    def registerStates(self):
        self.addChildState(_LoadingState(StateFlags.INITIAL))
        self.addChildState(_MainState())
        self.addChildState(_ExitState())

    def registerTransitions(self):
        machine = self.getMachine()
        loading = machine.getStateByCls(_LoadingState)
        main = machine.getStateByCls(_MainState)
        loading.addNavigationTransition(main)

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((SubhangarStateGroups.Customization,))

    def makeTransition(self, transitionType, record):
        return _CustomizationTransition(transitionType, record)

    def serializeParams(self):
        ctx = self.__c11n.getCtx()
        return {'season': ctx.season,
         'modeId': ctx.modeId,
         'tabId': ctx.mode.tabId,
         'source': ctx.mode.source,
         'itemCD': ctx.mode.selectedItem,
         'callback': None}

    def _onEntered(self, event):
        super(CustomizationState, self)._onEntered(event)
        self._subscribe()

    def _onExited(self):
        self._unsubscribe()
        super(CustomizationState, self)._onExited()
        if self.__hangarSpace.spaceInited:
            self.__hangarSpace.space.turretAndGunAngles.reset()

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params}

    def _getListeners(self):
        return ((events.CustomizationEvent.CLOSE, self.__showHangar, EVENT_BUS_SCOPE.LOBBY),)

    @staticmethod
    def __showHangar(event):
        showHangar()


class _CustomizationTransition(NavigationTransition):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def execute(self, event):
        if super(_CustomizationTransition, self).execute(event):
            vehInvID = event.params.get('vehInvID')
            vehGuiItem = self.__itemsCache.items.getVehicle(vehInvID) if vehInvID is not None else None
            vehCustomizationEnabled = vehGuiItem.isCustomizationEnabled() if vehGuiItem else True
            return self.__lobbyContext.isHeaderNavigationPossible() and vehCustomizationEnabled
        else:
            return


@CustomizationState.parentOf
class _LoadingState(LobbyState, EventsHandler):
    STATE_ID = 'loading'
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_LoadingState, self).__init__(flags=flags)
        self.__params = {}

    def _onEntered(self, event):
        super(_LoadingState, self)._onEntered(event)
        self.__params = dict(**event.params)
        Waiting.show('loadContent')
        vehInvID = event.params.get('vehInvID')
        shouldSelectVehicle = vehInvID is not None and (g_currentVehicle.invID != vehInvID or g_currentPreviewVehicle.isPresent())
        if not self.__hangarSpace.spaceInited or not self.__hangarSpace.isModelLoaded or shouldSelectVehicle:
            self._subscribe()
            if shouldSelectVehicle:
                if g_currentPreviewVehicle.isPresent():
                    g_currentPreviewVehicle.selectNoVehicle()
                BigWorld.callback(0.0, makeCallbackWeak(g_currentVehicle.selectVehicle, vehInvID=vehInvID))
        else:
            self.__goToMain()
        return

    def _onExited(self):
        super(_LoadingState, self)._onExited()
        self._unsubscribe()
        self.__params.clear()
        Waiting.hide('loadContent')

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onVehicleChanged), (g_currentPreviewVehicle.onChanged, self.__onVehicleChanged), (self.__hangarSpace.onSpaceChanged, self.__onSpaceChanged))

    def __onVehicleChanged(self):
        self.__goToMain()

    def __onSpaceChanged(self):
        if self.__hangarSpace.spaceInited and self.__hangarSpace.isModelLoaded:
            self.__goToMain()

    def __goToMain(self):
        BigWorld.callback(0.0, lambda : _MainState.goTo(**self.__params))


@CustomizationState.parentOf
class _MainState(SFViewLobbyState, EventsHandler):
    STATE_ID = 'main'
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION)
    __CAMERA_NAME = 'Customization'
    __GUN_PITCH_ANGLE = 0.0
    __TURRET_YAW_ANGLE = 0.0
    __RESTRICTED_EVENTS = [events.PrbInvitesEvent.ACCEPT,
     events.PrbActionEvent.SELECT,
     events.PrbActionEvent.LEAVE,
     events.TrainingEvent.RETURN_TO_TRAINING_ROOM]
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __c11n = dependency.descriptor(ICustomizationService)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_MainState, self).__init__(flags=flags)
        self.proceedWithoutSave = False

    def registerTransitions(self):
        machine = self.getMachine()
        edit = machine.getStateByCls(_CustomizationEditState)
        confirm = machine.getStateByCls(_ConfirmLeaveState)
        self.addGuardTransition(confirm, WeakMethodProxy(self.mustConfirmExit))
        self.addNavigationTransition(edit)

    def mustConfirmExit(self, event):
        ctx = self.__c11n.getCtx()
        return False if self.proceedWithoutSave or not ctx or ctx.applyingItems else ctx.isOutfitsModified()

    def getNavigationDescription(self):
        return None

    def getBackNavigationDescription(self, params):
        return None if self.getMachine().getStateByCls(_CustomizationMidState).isEntered() else backport.text(R.strings.pages.titles.customization())

    def _onEntered(self, event):
        super(_MainState, self)._onEntered(event)
        self.__hangarSpace.space.turretAndGunAngles.set(gunPitch=self.__GUN_PITCH_ANGLE, turretYaw=self.__TURRET_YAW_ANGLE)
        vEntity = self.__hangarSpace.space.getVehicleEntity()
        if vEntity is not None:
            vEntity.appearance.rotateTurretForAnchor(None, None)
            vEntity.appearance.rotateGunToDefault()
        ClientSelectableCameraObject.deselectAll()
        self.__hangarSpace.space.getVehicleEntity().onSelect(True)
        self.__setupTankTransformation()
        self.__c11n.onVisibilityChanged(True)
        self.__c11n.createCtx(**{k:event.params.get(k) for k in ('season', 'modeId', 'tabId', 'itemCD')})
        self._subscribe()
        self.__lobbyContext.addPlatoonCreationConfirmator(self.__confirmatorWrapper)
        self.__lobbyContext.addHeaderNavigationConfirmator(self.__confirmatorWrapper)
        _CustomizationEditState.goTo()
        if event.params['callback']:
            event.params['callback']()
        return

    def _onExited(self):
        self._unsubscribe()
        self.__lobbyContext.deletePlatoonCreationConfirmator(self.__confirmatorWrapper)
        self.__lobbyContext.deleteHeaderNavigationConfirmator(self.__confirmatorWrapper)
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__c11n.onVisibilityChanged(False)
        super(_MainState, self)._onExited()

    def _getRestrictions(self):
        return ((event, self.__handleRestrictedEvent, EVENT_BUS_SCOPE.LOBBY) for event in self.__RESTRICTED_EVENTS)

    def _onViewExternallyDestroyed(self):
        self.__cleanup()
        super(_MainState, self)._onViewExternallyDestroyed()

    def __cleanup(self, _=None):
        if self.__c11n.getCtx():
            _logger.debug('Destroying c11n context')
            self.__c11n.saveLastWrittenDataFromCtx()
            self.__c11n.destroyCtx()

    def __setupTankTransformation(self):
        from gui.ClientHangarSpace import customizationHangarCFG
        cfg = customizationHangarCFG()
        isForwardPipeline = BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 1
        targetPos = cfg['v_start_pos']
        yaw = math.radians(cfg['v_start_angles'][0])
        pitch = math.radians(cfg['v_start_angles'][1])
        roll = math.radians(cfg['v_start_angles'][2])
        shadowYOffset = cfg['shadow_forward_y_offset'] if isForwardPipeline else cfg['shadow_deferred_y_offset']
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.CHANGE_VEHICLE_MODEL_TRANSFORM, ctx={'targetPos': targetPos,
         'rotateYPR': (yaw, pitch, roll),
         'shadowYOffset': shadowYOffset}), scope=EVENT_BUS_SCOPE.LOBBY)

    @wg_async
    def __handleRestrictedEvent(self, event=None):
        if not self.mustConfirmExit(event):
            raise AsyncReturn(True)
        _ConfirmLeaveState.goTo()
        try:
            confirmState = self.getMachine().getStateByCls(_ConfirmLeaveState)
            self.proceedWithoutSave = yield confirmState.waitForResult()
            if self.proceedWithoutSave:
                self.goBack()
            else:
                confirmState.goBack()
        except BrokenPromiseError:
            self.proceedWithoutSave = False

        raise AsyncReturn(self.proceedWithoutSave)

    @adisp.adisp_async
    @wg_async
    def __confirmatorWrapper(self, callback):
        result = yield wg_await(self.__handleRestrictedEvent())
        callback(result)


@CustomizationState.parentOf
class _ExitState(LobbyState):
    STATE_ID = 'exit'

    def _onEntered(self, event):
        super(_ExitState, self)._onEntered(event)
        self.getParent().goBack()
        self.getMachine().post(event)


class _ExitTransition(GuardTransition):

    def getPriority(self):
        return super(_ExitTransition, self).getPriority() - 1


@TopScopeTopLayerState.parentOf
class _CustomizationTopState(LobbyState):
    STATE_ID = 'customization'

    def registerStates(self):
        self.addChildState(_ConfirmLeaveState(StateFlags.INITIAL))


@_CustomizationTopState.parentOf
class _ConfirmLeaveState(LobbyState):
    STATE_ID = 'confirmLeave'
    __c11n = dependency.descriptor(ICustomizationService)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_ConfirmLeaveState, self).__init__(flags)
        self.__dialog = None
        self.__waitFuture = None
        return

    def getNavigationDescription(self):
        return None

    @wg_async
    def waitForResult(self):
        self.__waitFuture = self.__dialog.wait()
        result = yield self.__waitFuture
        raise AsyncReturn(result.result in dialogs.DialogButtons.ACCEPT_BUTTONS)

    @wg_async
    def _onEntered(self, event):
        super(_ConfirmLeaveState, self)._onEntered(event)
        message = R.strings.dialogs.customization.close
        if UntrackedState.LOAD_PARAMS_KEY in event.params:
            loadParams = event.params[UntrackedState.LOAD_PARAMS_KEY].loadParams
            if loadParams.viewKey.alias == VIEW_ALIAS.LOBBY_STORE:
                message = R.strings.dialogs.customization.exitToShop
        builder = ResPureDialogBuilder()
        builder.setMessagesAndButtons(message, focused=DialogButtons.CANCEL)
        self.__dialog = builder.build()
        self.__dialog.load()
        self.__c11n.getCtx().events.onCloseDialogShown(ViewKeyDynamic(self.__dialog.decorator.layoutID))
        if event.targetStateID != self.getStateID():
            try:
                proceed = yield self.waitForResult()
                if proceed:
                    machine = self.getMachine()
                    mainState = machine.getStateByCls(_MainState)
                    mainState.proceedWithoutSave = True
                    mainState.goBack()
                    self.getMachine().post(event)
                else:
                    self.goBack()
            except BrokenPromiseError:
                _logger.debug('%s dialog closed without user decision.', self.__class__.__name__)

    def _onExited(self):
        super(_ConfirmLeaveState, self)._onExited()
        self.__waitFuture.cancel()
        self.__waitFuture = None
        self.__dialog.destroy()
        self.__dialog = None
        ctx = self.__c11n.getCtx()
        if ctx:
            ctx.events.onCloseDialogClosed()
        return


@SubScopeTopLayerState.parentOf
class _CustomizationMidState(LobbyState):
    STATE_ID = 'customization'

    def registerStates(self):
        self.addChildState(_CustomizationEditState(StateFlags.INITIAL))
        self.addChildState(CustomizationCartState())
        self.addChildState(ProgressiveItemsState())

    def registerTransitions(self):
        machine = self.getMachine()
        edit = machine.getStateByCls(_CustomizationEditState)
        cart = machine.getStateByCls(CustomizationCartState)
        progressiveItems = machine.getStateByCls(ProgressiveItemsState)
        exit = machine.getStateByCls(_ExitState)
        edit.addNavigationTransition(cart, record=True)
        edit.addNavigationTransition(progressiveItems, record=True)
        for state in self.getChildrenStates():
            state.addGuardTransition(machine.getStateByCls(_ConfirmLeaveState), WeakMethodProxy(self.mustConfirmExit))

        self.addTransition(_ExitTransition(WeakMethodProxy(self.__shouldRedirectToExit)), exit)

    def mustConfirmExit(self, event):
        machine = self.getMachine()
        if isinstance(event, NavigationEvent):
            targetState = machine.getStateByID(event.targetStateID)
            if visitor.isDescendantOf(targetState, self):
                return False
        main = machine.getStateByCls(_MainState)
        return self.__shouldRedirectToExit(event) and main.mustConfirmExit(event)

    def _onEntered(self, event):
        super(_CustomizationMidState, self)._onEntered(event)
        machine = self.getMachine()
        machine.getStateByCls(_MainState).proceedWithoutSave = False

    def __shouldRedirectToExit(self, event):
        machine = self.getMachine()
        target = machine.getStateByID(event.targetStateID)
        if target is machine.getEmptyStateInSubtreeOf(self):
            return False
        return True if target is machine.findOwningSubtree(self) else machine.findOwningSubtree(target) is not machine.findOwningSubtree(self)


@_CustomizationMidState.parentOf
class _CustomizationEditState(LobbyState):
    STATE_ID = 'edit'

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.customization()))


@_CustomizationMidState.parentOf
class CustomizationCartState(LobbyState):
    STATE_ID = 'cart'
    VIEW_KEY = ViewKey(R.views.lobby.customization.CustomizationCart())

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params.get('ctx')}

    def _onEntered(self, event):
        from gui.impl.lobby.customization.customization_cart.customization_cart_view import CustomizationCartView
        super(CustomizationCartState, self)._onEntered(event)
        uiLoader = dependency.instance(IGuiLoader)
        viewAlias = self.getViewKey().alias
        if uiLoader.windowsManager.getViewByLayoutID(viewAlias):
            return
        else:
            customizationView = event.params.get('ctx', {}).get('c11nView', None)
            parentWindow = None
            if customizationView:
                parentWindow = customizationView.getParentWindow()
            g_eventBus.handleEvent(LoadGuiImplViewEvent(GuiImplViewLoadParams(viewAlias, CustomizationCartView, ScopeTemplates.LOBBY_SUB_SCOPE, parent=parentWindow), **self._getViewLoadCtx(event)), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.customization.cart()))


@_CustomizationMidState.parentOf
class ProgressiveItemsState(GuiImplViewLobbyState):
    STATE_ID = 'progressiveItems'
    VIEW_KEY = ViewKey(R.views.lobby.customization.progressive_items_view.ProgressiveItemsView())

    def __init__(self, flags=StateFlags.UNDEFINED):
        from gui.impl.lobby.customization.progressive_items_view.progressive_items_view import ProgressiveItemsView
        super(ProgressiveItemsState, self).__init__(ProgressiveItemsView, ScopeTemplates.LOBBY_SUB_SCOPE, flags=flags)

    @classmethod
    def goTo(cls, itemIntCD=None):
        super(ProgressiveItemsState, cls).goTo(itemIntCD=itemIntCD)

    def _onExited(self):
        super(ProgressiveItemsState, self)._onExited()
        uiLoader = dependency.instance(IGuiLoader)
        windowsManager = uiLoader.windowsManager
        view = windowsManager.getViewByLayoutID(self.getViewKey().alias)
        if view:
            view.destroy()

    @dependency.replace_none_kwargs(appLoader=IAppLoader)
    def _getViewLoadCtx(self, event, appLoader=None):
        c11nView = appLoader.getApp().containerManager.getViewByKey(_MainState.VIEW_KEY)
        return {'c11nView': c11nView,
         'itemIntCD': event.params.get('itemIntCD')}

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.customization.progressive_items()))
