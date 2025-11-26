# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/states.py
import typing
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

def registerStates(machine):
    machine.addState(ShopState())


def registerTransitions(_):
    pass


@SubScopeSubLayerState.parentOf
class ShopState(SFViewLobbyState):
    STATE_ID = 'shop'
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_STORE)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(ShopState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def serializeParams(self):
        return self.__cachedParams

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import VehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import HeroTankPreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ConfigurableVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import RentalVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import TradeInVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import MarathonVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import OfferGiftVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleBuyingPreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ShowcaseStyleBuyingPreviewState
        from gui.impl.lobby.lootbox_system.states import LootBoxMainState
        from gui.impl.lobby.lootbox_system.states import LootBoxInfoState
        from gui.impl.lobby.vehicle_hub.states import OverviewState
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)
        self.addNavigationTransition(lsm.getStateByCls(VehiclePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(HeroTankPreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(ConfigurableVehiclePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(RentalVehiclePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(TradeInVehiclePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(MarathonVehiclePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OfferGiftVehiclePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StyleBuyingPreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(ShowcaseStyleBuyingPreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(LootBoxMainState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(LootBoxInfoState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.browser.shop()))

    def _onEntered(self, event):
        super(ShopState, self)._onEntered(event)
        self.__cachedParams = event.params
        browser = self.getMachine().getRelatedView(self).getBrowser()
        if browser:
            browser.navigate(event.params['ctx']['url'])

    def _onExited(self):
        super(ShopState, self)._onExited()
        self.__cachedParams = {}

    def _getViewLoadCtx(self, event):
        ctx = event.params.get('ctx', {})
        ctx.update({'forcedSkipEscape': True})
        return {'ctx': ctx}
