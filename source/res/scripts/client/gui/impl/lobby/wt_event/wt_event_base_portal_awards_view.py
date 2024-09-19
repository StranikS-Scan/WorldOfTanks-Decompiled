# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_base_portal_awards_view.py
import logging
from constants import IS_CHINA, IS_LOOT_BOXES_ENABLED
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_awards_base_model import WtEventPortalAwardsBaseModel
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_buy_lootboxes_tooltip_view import WtEventBuyLootBoxesTooltipView
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher
from gui.shop import showBuyLootboxOverlay
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.Waiting import Waiting
from gui.wt_event.wt_event_helpers import backportTooltipDecorator
from gui.wt_event.wt_event_models_helper import setLootBoxesCount
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEventBattlesController, IWTLootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class WtEventBasePortalAwards(ViewImpl):
    __slots__ = ('_awards', '_tooltipItems')
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _eventCtrl = dependency.descriptor(IEventBattlesController)
    _boxesCtrl = dependency.descriptor(IWTLootBoxesController)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings, awards, *args, **kwargs):
        super(WtEventBasePortalAwards, self).__init__(settings)
        self._awards = awards
        self._tooltipItems = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WtEventBasePortalAwards, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventLootBoxTooltipView():
            return WtEventLootBoxTooltipView(isHunterLootBox=event.getArgument('isHunterLootBox'))
        return WtEventBuyLootBoxesTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtEventBuyLootBoxesTooltipView() else super(WtEventBasePortalAwards, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WtEventBasePortalAwards, self)._onLoading()
        self._addListeners()
        self._updateModel()

    def _onLoaded(self, *args, **kwargs):
        super(WtEventBasePortalAwards, self)._onLoaded(*args, **kwargs)
        self._eventCtrl.getLootBoxAreaSoundMgr().enter()

    def _finalize(self):
        self._removeListeners()
        self._awards = None
        self._tooltipItems = None
        super(WtEventBasePortalAwards, self)._finalize()
        return

    def _updateModel(self):
        self.viewModel.setIsBoxesEnabled(self._lobbyContext.getServerSettings().isLootBoxesEnabled())
        if IS_CHINA:
            self.viewModel.setAvailableLootBoxesPurchase(self._boxesCtrl.getAvailableForPurchaseLootBoxesCount())

    def _updateLootBoxesCount(self, *args, **kwargs):
        setLootBoxesCount(self.viewModel.portalAvailability, self._getBoxType())

    def _addListeners(self):
        app = self._appLoader.getApp()
        self.viewModel.onClose += self._onClose
        self.viewModel.onBuy += self.__goToShop
        self.viewModel.onPreview += self._goToPreview
        self.viewModel.onClaimReward += self._claimReward
        self._boxesCtrl.onUpdated += self._updateLootBoxesCount
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._eventCtrl.onEventPrbChanged += self.__onEventPrbChanged
        if app:
            app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer

    def _removeListeners(self):
        app = self._appLoader.getApp()
        self.viewModel.onClose -= self._onClose
        self.viewModel.onBuy -= self.__goToShop
        self.viewModel.onPreview -= self._goToPreview
        self.viewModel.onClaimReward -= self._claimReward
        self._boxesCtrl.onUpdated -= self._updateLootBoxesCount
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self._eventCtrl.onEventPrbChanged -= self.__onEventPrbChanged
        if app:
            app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer

    def _getBoxType(self):
        raise NotImplementedError

    def _goToPreview(self, args):
        intCD = int(args.get('intCD', 0))
        if intCD == 0:
            _logger.error('Invalid intCD to preview the bonus vehicle')
            return
        self._eventCtrl.getLootBoxAreaSoundMgr().leave()
        self._showVehiclePreview(intCD)

    def _claimReward(self):
        pass

    def _showVehiclePreview(self, intCD):
        event_dispatcher.selectVehicleInHangar(intCD)
        self.destroyWindow()

    def _onClose(self):
        self.destroyWindow()

    def __goToShop(self):
        Waiting.show('updating')
        showBuyLootboxOverlay(self.getParentWindow(), alias=VIEW_ALIAS.OVERLAY_WEB_STORE)

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.alias == VIEW_ALIAS.OVERLAY_WEB_STORE:
            if Waiting.isOpened('updating'):
                Waiting.hide('updating')

    def __onEventPrbChanged(self, isActive):
        if not isActive:
            self.destroyWindow()

    def __onServerSettingsChange(self, diff):
        if IS_LOOT_BOXES_ENABLED in diff:
            self.viewModel.setIsBoxesEnabled(self._lobbyContext.getServerSettings().isLootBoxesEnabled())
