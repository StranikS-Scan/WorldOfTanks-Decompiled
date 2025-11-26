# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/states.py
from frameworks.state_machine import StateFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import LobbyState, LobbyStateDescription, LobbyStateFlags, SubScopeSubLayerState, ViewLobbyState

def registerStates(machine):
    machine.addState(VehiclePreviewState())
    machine.addState(HeroTankPreviewState())
    machine.addState(RentalVehiclePreviewState())
    machine.addState(TradeInVehiclePreviewState())
    machine.addState(MarathonVehiclePreviewState())
    machine.addState(OfferGiftVehiclePreviewState())
    machine.addState(StyleProgressionPreviewState())
    machine.addState(StyleBuyingPreviewState())
    machine.addState(ShowcaseStyleBuyingPreviewState())
    machine.addState(VehiclePreviewStateWithTopPanel())


def registerTransitions(machine):
    addTransition = machine.addNavigationTransitionFromParent
    addTransition(machine.getStateByCls(VehiclePreviewState))
    addTransition(machine.getStateByCls(HeroTankPreviewState))
    addTransition(machine.getStateByCls(RentalVehiclePreviewState))
    addTransition(machine.getStateByCls(TradeInVehiclePreviewState))
    addTransition(machine.getStateByCls(MarathonVehiclePreviewState))
    addTransition(machine.getStateByCls(OfferGiftVehiclePreviewState))
    addTransition(machine.getStateByCls(StyleProgressionPreviewState))
    addTransition(machine.getStateByCls(StyleBuyingPreviewState))
    addTransition(machine.getStateByCls(ShowcaseStyleBuyingPreviewState))
    addTransition(machine.getStateByCls(VehiclePreviewStateWithTopPanel))


class _VehiclePreviewStateProto(ViewLobbyState):

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_VehiclePreviewStateProto, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
        from gui.Scaleform.daapi.view.lobby.vehicle_compare.states import VehicleCompareState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        machine = self.getMachine()
        self.addNavigationTransition(machine.getStateByCls(VehiclePostProgressionState), record=True)
        self.addNavigationTransition(machine.getStateByCls(VehicleCompareState), record=True)
        self.addNavigationTransition(machine.getStateByCls(ShopState), record=True)

    def serializeParams(self):
        return self.__cachedParams

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.vehicle_preview()))

    def _prepareCamera(self):
        from ClientSelectableCameraObject import ClientSelectableCameraObject
        ClientSelectableCameraObject.switchCamera()

    def _onEntered(self, event):
        super(_VehiclePreviewStateProto, self)._onEntered(event)
        self.__cachedParams = event.params
        self._prepareCamera()

    def _onExited(self):
        super(_VehiclePreviewStateProto, self)._onExited()
        self.__cachedParams = {}

    def _getViewLoadCtx(self, event):
        return {'ctx': {'itemCD': event.params['itemCD'],
                 'previewAlias': event.params.get('previewAlias', None),
                 'vehicleStrCD': event.params.get('vehicleStrCD', None),
                 'itemsPack': event.params.get('itemsPack', None),
                 'offers': event.params.get('offers', None),
                 'price': event.params.get('price', None),
                 'oldPrice': event.params.get('oldPrice', None),
                 'title': event.params.get('title', None),
                 'description': event.params.get('description', None),
                 'endTime': event.params.get('endTime', None),
                 'buyParams': event.params.get('buyParams', None),
                 'obtainingMethod': event.params.get('obtainingMethod', None),
                 'vehParams': event.params.get('vehParams', None),
                 'style': event.params.get('style', None),
                 'resetAppearance': event.params.get('resetAppearance', False),
                 'topPanelData': event.params.get('topPanelData', None)}}


@SubScopeSubLayerState.parentOf
class VehiclePreviewStateWithTopPanel(LobbyState):
    STATE_ID = 'vehiclePreviewWithTopPanel'

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(ConfigurableVehiclePreviewState(LobbyStateFlags.INITIAL))
        lsm.addState(StylePreviewState())

    def registerTransitions(self):
        for state in self.getChildrenStates():
            self.getParent().addNavigationTransition(state)
            self.addNavigationTransition(state)


@SubScopeSubLayerState.parentOf
class VehiclePreviewState(_VehiclePreviewStateProto):
    STATE_ID = VIEW_ALIAS.VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.VEHICLE_PREVIEW)


@SubScopeSubLayerState.parentOf
class HeroTankPreviewState(_VehiclePreviewStateProto):
    STATE_ID = VIEW_ALIAS.HERO_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.HERO_VEHICLE_PREVIEW)

    def _prepareCamera(self):
        from ClientSelectableCameraObject import ClientSelectableCameraObject
        ClientSelectableCameraObject.switchCamera(cameraName='HeroTank')

    def _getViewLoadCtx(self, event):
        params = super(HeroTankPreviewState, self)._getViewLoadCtx(event)
        params['ctx'].update({'previewAppearance': event.params.get('previewAppearance', None),
         'isHeroTank': event.params.get('isHeroTank', True),
         'previousBackAlias': event.params.get('previousBackAlias', None),
         'hangarVehicleCD': event.params.get('hangarVehicleCD', None),
         'backOutfit': event.params.get('backOutfit', None)})
        return params


@VehiclePreviewStateWithTopPanel.parentOf
class ConfigurableVehiclePreviewState(_VehiclePreviewStateProto):
    STATE_ID = VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW)

    def _getViewLoadCtx(self, event):
        params = super(ConfigurableVehiclePreviewState, self)._getViewLoadCtx(event)
        params['ctx'].update({'hiddenBlocks': event.params.get('hiddenBlocks', None),
         'heroInteractive': event.params.get('heroInteractive', True),
         'subscriptions': event.params.get('subscriptions', ())})
        return params


@SubScopeSubLayerState.parentOf
class RentalVehiclePreviewState(_VehiclePreviewStateProto):
    STATE_ID = VIEW_ALIAS.RENTAL_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.RENTAL_VEHICLE_PREVIEW)


@SubScopeSubLayerState.parentOf
class TradeInVehiclePreviewState(_VehiclePreviewStateProto):
    STATE_ID = VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW)


@SubScopeSubLayerState.parentOf
class MarathonVehiclePreviewState(_VehiclePreviewStateProto):
    STATE_ID = VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW)

    def _getViewLoadCtx(self, event):
        params = super(MarathonVehiclePreviewState, self)._getViewLoadCtx(event)
        params['ctx'].update({'marathonPrefix': event.params.get('marathonPrefix', ''),
         'previewAppearance': event.params.get('previewAppearance', None),
         'backToHangar': event.params.get('backToHangar', False)})
        return params


@SubScopeSubLayerState.parentOf
class OfferGiftVehiclePreviewState(_VehiclePreviewStateProto):
    STATE_ID = VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW)

    def _getViewLoadCtx(self, event):
        params = super(OfferGiftVehiclePreviewState, self)._getViewLoadCtx(event)
        params['ctx'].update({'offerID': event.params.get('offerID', None),
         'giftID': event.params.get('giftID', None),
         'confirmCallback': event.params.get('confirmCallback', None),
         'customCallbacks': event.params.get('customCallbacks', {})})
        return params


class _StylePreviewStateProto(ViewLobbyState):

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_StylePreviewStateProto, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
        from gui.Scaleform.daapi.view.lobby.vehicle_compare.states import VehicleCompareState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        machine = self.getMachine()
        self.addNavigationTransition(machine.getStateByCls(VehiclePostProgressionState), record=True)
        self.addNavigationTransition(machine.getStateByCls(VehicleCompareState), record=True)
        self.addNavigationTransition(machine.getStateByCls(ShopState), record=True)

    def serializeParams(self):
        return self.__cachedParams

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.style_preview()))

    def _prepareCamera(self):
        from ClientSelectableCameraObject import ClientSelectableCameraObject
        ClientSelectableCameraObject.switchCamera()

    def _onEntered(self, event):
        super(_StylePreviewStateProto, self)._onEntered(event)
        self.__cachedParams = event.params
        self._prepareCamera()

    def _onExited(self):
        super(_StylePreviewStateProto, self)._onExited()
        self.__cachedParams = {}

    def _getViewLoadCtx(self, event):
        return {'ctx': {'itemCD': event.params['itemCD'],
                 'style': event.params.get('style', None),
                 'resetAppearance': event.params.get('resetAppearance', False),
                 'styleDescr': event.params.get('styleDescr', ''),
                 'backPreviewAlias': event.params.get('backPreviewAlias', None),
                 'topPanelData': event.params.get('topPanelData', None),
                 'outfit': event.params.get('outfit', None),
                 'isHeroTank': event.params.get('isHeroTank', False)}}


@VehiclePreviewStateWithTopPanel.parentOf
class StylePreviewState(_StylePreviewStateProto):
    STATE_ID = VIEW_ALIAS.STYLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.STYLE_PREVIEW)


@SubScopeSubLayerState.parentOf
class StyleProgressionPreviewState(_StylePreviewStateProto):
    STATE_ID = VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW)

    def _getViewLoadCtx(self, event):
        params = super(StyleProgressionPreviewState, self)._getViewLoadCtx(event)
        params['ctx'].update({'styleLevel': event.params.get('styleLevel', None),
         'chapterId': event.params.get('chapterId', None)})
        return params


@SubScopeSubLayerState.parentOf
class StyleBuyingPreviewState(_StylePreviewStateProto):
    STATE_ID = VIEW_ALIAS.STYLE_BUYING_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.STYLE_BUYING_PREVIEW)

    def _getViewLoadCtx(self, event):
        params = super(StyleBuyingPreviewState, self)._getViewLoadCtx(event)
        params['ctx'].update({'styleLevel': event.params.get('styleLevel', None),
         'price': event.params.get('price', None),
         'buyParams': event.params.get('buyParams', None)})
        return params


@SubScopeSubLayerState.parentOf
class ShowcaseStyleBuyingPreviewState(_StylePreviewStateProto):
    STATE_ID = VIEW_ALIAS.SHOWCASE_STYLE_BUYING_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.SHOWCASE_STYLE_BUYING_PREVIEW)

    def _getViewLoadCtx(self, event):
        params = super(ShowcaseStyleBuyingPreviewState, self)._getViewLoadCtx(event)
        params['ctx'].update({'price': event.params.get('price', None),
         'originalPrice': event.params.get('originalPrice', None),
         'buyParams': event.params.get('buyParams', None),
         'obtainingMethod': event.params.get('obtainingMethod', None),
         'endTime': event.params.get('endTime', None),
         'discountPercent': event.params.get('discountPercent', None)})
        return params
