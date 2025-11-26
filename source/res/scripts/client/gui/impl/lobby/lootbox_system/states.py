# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/states.py
import BigWorld
from frameworks.wulf import WindowLayer
from frameworks.state_machine.transitions import TransitionType
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showHangar
from gui.lootbox_system.base.common import getTextResource
from gui.Scaleform.framework.entities.View import ViewKey
from gui.lobby_state_machine.states import StateFlags, LobbyStateFlags, SubScopeSubLayerState, LobbyState, LobbyStateDescription, SFViewLobbyState
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.app_loader import IAppLoader
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

def registerStates(machine):
    machine.addState(LootBoxState())


def registerTransitions(machine):
    lootBox = machine.getStateByCls(LootBoxState)
    machine.addNavigationTransitionFromParent(lootBox)


class _LootBoxBaseState(SFViewLobbyState):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_LootBoxBaseState, self).__init__(flags)
        self._shouldRedirectToHangar = True
        self.__cachedParams = {}

    @classmethod
    def goTo(cls, ctx):
        super(_LootBoxBaseState, cls).goTo(ctx=ctx)

    def getNavigationDescription(self):
        eventName = self.__cachedParams.get('ctx', {}).get('eventName')
        return LobbyStateDescription(title=backport.text(getTextResource('preview/backLabel'.split('/'), eventName)()))

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ConfigurableVehiclePreviewState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(ConfigurableVehiclePreviewState), record=True)

    def serializeParams(self):
        ctx = self.__cachedParams.get('ctx', {})
        ctx.update({'isReopen': True})
        return {'ctx': ctx}

    def isLootBoxesAvailable(self):
        eventName = self.__cachedParams.get('ctx', {}).get('eventName')
        return self.__lootBoxes.isAvailable(eventName) and self.__lootBoxes.getActiveBoxes(eventName)

    def updateCachedCtx(self, params):
        ctx = self.__cachedParams.get('ctx', {})
        ctx.update(params)
        self.__cachedParams['ctx'] = ctx

    def _getEvents(self):
        return ((self.__lootBoxes.onStatusChanged, self.__onStatusChanged), (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onStatusChanged))

    def _subscribe(self):
        for event, handler in self._getEvents():
            event += handler

    def _unsubscribe(self):
        for event, handler in self._getEvents():
            event -= handler

    def _onEntered(self, event):
        super(_LootBoxBaseState, self)._onEntered(event)
        self._subscribe()
        self.__cachedParams = event.params
        if not self.isLootBoxesAvailable() and self._shouldRedirectToHangar:
            showHangar()

    def _onExited(self):
        super(_LootBoxBaseState, self)._onExited()
        self._unsubscribe()

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params.get('ctx', {})}

    def __onStatusChanged(self):
        if not self.isLootBoxesAvailable() and self._shouldRedirectToHangar:
            showHangar()


@SubScopeSubLayerState.parentOf
class LootBoxState(LobbyState):
    __appLoader = dependency.instance(IAppLoader)

    def __init__(self):
        super(LootBoxState, self).__init__()
        self.__previouslyVisibleLayers = []

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(LootBoxMainState(LobbyStateFlags.INITIAL))
        lsm.addState(LootBoxInfoState())
        lsm.addState(LootBoxAutoOpenState())

    def registerTransitions(self):
        for state in self.getChildrenStates():
            self.getParent().addNavigationTransition(state)
            self.addNavigationTransition(state)

    def _onEntered(self, event):
        super(LootBoxState, self)._onEntered(event)
        containerManager = self.__appLoader.getApp().containerManager
        self.__previouslyVisibleLayers = containerManager.getVisibleLayers()
        containerManager.setVisibleLayers(self._getVisibleLayers())
        BigWorld.worldDrawEnabled(False)

    def _onExited(self):
        super(LootBoxState, self)._onExited()
        self.__appLoader.getApp().containerManager.setVisibleLayers(self.__previouslyVisibleLayers)
        BigWorld.worldDrawEnabled(True)

    def _getVisibleLayers(self):
        return [WindowLayer.TOP_WINDOW,
         WindowLayer.FULLSCREEN_WINDOW,
         WindowLayer.TOOLTIP,
         WindowLayer.OVERLAY]


@LootBoxState.parentOf
class LootBoxInfoState(_LootBoxBaseState):
    STATE_ID = 'lootBoxInfoState'
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOOT_BOXES_INFO_VIEW)


@LootBoxState.parentOf
class LootBoxMainState(_LootBoxBaseState):
    STATE_ID = 'lootBoxMainState'
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOOT_BOXES_MAIN_VIEW)

    def _onEntered(self, event):
        super(LootBoxMainState, self)._onEntered(event)
        uiLoader = dependency.instance(IGuiLoader)
        windowsManager = uiLoader.windowsManager
        window = windowsManager.getViewByLayoutID(R.views.mono.lootbox.main())
        ctx = event.params.get('ctx', {})
        if ctx is not None and window is not None:
            window.switchToSubView(**ctx)
        return

    def registerTransitions(self):
        super(LootBoxMainState, self).registerTransitions()
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        machine = self.getMachine()
        info = machine.getStateByCls(LootBoxInfoState)
        shop = machine.getStateByCls(ShopState)
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)
        self.addNavigationTransition(info, record=True)
        self.addNavigationTransition(shop, record=True)


@LootBoxState.parentOf
class LootBoxAutoOpenState(_LootBoxBaseState):
    STATE_ID = 'lootBoxAutoOpenState'
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOOT_BOXES_AUTO_OPEN_VIEW)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LootBoxAutoOpenState, self).__init__(flags)
        self._shouldRedirectToHangar = False
