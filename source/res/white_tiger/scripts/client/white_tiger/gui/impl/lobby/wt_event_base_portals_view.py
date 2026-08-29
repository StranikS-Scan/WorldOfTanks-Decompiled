# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_base_portals_view.py
from constants import IS_LOOT_BOXES_ENABLED
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_base_portals_view_model import WtBasePortalsViewModel
from white_tiger.gui.impl.lobby.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_event_buy_lootboxes_tooltip_view import WtEventBuyLootBoxesTooltipView
from white_tiger.gui.impl.lobby.tooltips.main_prize_discount_tooltip_view import MainPrizeDiscountTooltipView
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shop import showBuyLootboxOverlay
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IWhiteTigerController, ILootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class WtEventBasePortalsView(ViewImpl):
    __slots__ = ()
    _eventCtrl = dependency.descriptor(IWhiteTigerController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)
    _lootBoxesCtrl = dependency.descriptor(ILootBoxesController)
    _appLoader = dependency.descriptor(IAppLoader)

    @property
    def viewModel(self):
        return super(WtEventBasePortalsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.white_tiger.lobby.tooltips.LootBoxTooltipView():
            return WtEventLootBoxTooltipView(isHunterLootBox=event.getArgument('isHunterLootBox'))
        if contentID == R.views.white_tiger.lobby.tooltips.MainPrizeDiscountTooltipView():
            discount = int(event.getArgument('discount'))
            return MainPrizeDiscountTooltipView(discount=discount)
        return WtEventBuyLootBoxesTooltipView() if contentID == R.views.white_tiger.lobby.tooltips.BuyLootBoxesTooltipView() else super(WtEventBasePortalsView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WtEventBasePortalsView, self)._onLoading()
        self._addListeners()
        self._updateModel()

    def _onLoaded(self, *args, **kwargs):
        super(WtEventBasePortalsView, self)._onLoaded(*args, **kwargs)
        self._eventCtrl.getLootBoxAreaSoundMgr().enter()

    def _finalize(self):
        self._removeListeners()
        super(WtEventBasePortalsView, self)._finalize()

    def _addListeners(self):
        app = self._appLoader.getApp()
        self.viewModel.onBuyLootBoxes += self.__onBuyLootBoxes
        self.viewModel.onClose += self._onClosedByUser
        self._itemsCache.onSyncCompleted += self._onCacheResync
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._eventCtrl.onEventPrbChanged += self.__onEventPrbChanged
        self._eventCtrl.onUpdated += self._onEventUpdated
        if app:
            app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_VEHICLE_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        app = self._appLoader.getApp()
        self.viewModel.onClose -= self._onClosedByUser
        self.viewModel.onBuyLootBoxes -= self.__onBuyLootBoxes
        self._itemsCache.onSyncCompleted -= self._onCacheResync
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self._eventCtrl.onEventPrbChanged -= self.__onEventPrbChanged
        self._eventCtrl.onUpdated -= self._onEventUpdated
        if app:
            app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_VEHICLE_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)

    def _updateModel(self):
        self.viewModel.setIsBoxesEnabled(self._lootBoxesCtrl.isEnabled())

    def _onPortalAwardsViewClose(self, _):
        pass

    def _onEventUpdated(self):
        pass

    def _onClosedByUser(self):
        self._eventCtrl.getLootBoxAreaSoundMgr().leave()

    def _onCacheResync(self, *_):
        self._updateModel()

    def __onServerSettingsChange(self, diff):
        if IS_LOOT_BOXES_ENABLED in diff:
            self.viewModel.setIsBoxesEnabled(self._lootBoxesCtrl.isEnabled())

    def __onBuyLootBoxes(self, *args, **kwargs):
        Waiting.show('updating')
        showBuyLootboxOverlay(self.getParentWindow(), alias=VIEW_ALIAS.OVERLAY_WEB_STORE)

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.alias == VIEW_ALIAS.OVERLAY_WEB_STORE:
            if Waiting.isOpened('updating'):
                Waiting.hide('updating')

    def __onEventPrbChanged(self, isActive):
        if not isActive:
            self.destroyWindow()
