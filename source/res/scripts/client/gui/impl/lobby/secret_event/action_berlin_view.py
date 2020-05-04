# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_berlin_view.py
import datetime
import logging
import sys
from zipfile import crc32
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_berlin_model import ActionBerlinModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.lobby.secret_event import EnergyMixin, convertPriceToMoney, RewardListMixin, convertPriceToTuple
from gui.impl.lobby.secret_event.action_view_with_menu import ActionViewWithMenu
from gui.ingame_shop import showBuyGoldForSecretEventItem
from gui.server_events.game_event.shop import ENERGY_TOKEN_PREFIX
from gui.shared.event_dispatcher import showOrderBuyDialog
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from shared_utils import first
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.secret_event.sound_constants import ACTION_BERLIN_SETTINGS
_logger = logging.getLogger(__name__)

class ActionBerlinView(ActionViewWithMenu, EnergyMixin, RewardListMixin):
    gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    MAX_REWARDS_LIST_COUNT = sys.maxint
    _COMMON_SOUND_SPACE = ACTION_BERLIN_SETTINGS

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ActionBerlinModel()
        self._callBack = None
        self._stats = self._itemsCache.items.stats
        self.__orderID = None
        self.__layoutID = layoutID
        super(ActionBerlinView, self).__init__(settings)
        return

    def _initialize(self):
        super(ActionBerlinView, self)._initialize()
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.viewModel.onBuyPack += self.__onBuyPack

    def _finalize(self):
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.viewModel.onBuyPack -= self.__onBuyPack
        if self._callBack:
            self._callBack.destroy()
        super(ActionBerlinView, self)._finalize()

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if 'rewardTooltip' in tooltipId:
                window = RewardListMixin.createToolTip(self, event)
            if tooltipId == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                item = self.gameEventController.getShop().getItem(self.__orderID)
                args = (ACTION_TOOLTIPS_TYPE.ITEM,
                 GUI_ITEM_TYPE.VEHICLE,
                 convertPriceToTuple(*item.getPrice()),
                 convertPriceToTuple(*item.getDefPrice()),
                 True)
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
            if window:
                window.load()
                return window
        return super(ActionBerlinView, self).createToolTip(event)

    def _onLoading(self):
        super(ActionBerlinView, self)._onLoading()
        if not self._callBack:
            self._callBack = CallbackDelayer()
        self.__fillViewModel()

    def _setDaysLeftCallback(self, callbackFunction, td):
        nextCallBack = td - datetime.timedelta(days=1)
        if nextCallBack.days >= 0:
            self._callBack.stopCallback(callbackFunction)
            nextCallbackTime = nextCallBack.seconds + float(nextCallBack.microseconds) / 1000000 + 1
            self._callBack.delayCallback(nextCallbackTime, callbackFunction)

    def _updateBerlinStartTimeLeft(self):
        berlinStartTimeLeft = self.gameEventController.getBerlinStartTimeLeft()
        td = datetime.timedelta(seconds=berlinStartTimeLeft)
        self.viewModel.setCountdownDaysLeft(td.days)
        berlinStartTime = self.gameEventController.getBerlinStartTimeUTC()
        self.viewModel.setCountdownTime(berlinStartTime)
        self._setDaysLeftCallback(self._updateBerlinStartTimeLeft, td)

    def _updateEventTimeLeft(self):
        self.viewModel.setPackTimer(self.gameEventController.getEventFinishTimeUTC())
        td = datetime.timedelta(seconds=self.gameEventController.getEventFinishTimeLeft())
        self.viewModel.setPackDayLeft(td.days)
        self._setDaysLeftCallback(self._updateEventTimeLeft, td)

    def __fillViewModel(self):
        berlinStartTimeLeft = self.gameEventController.getBerlinStartTimeLeft()
        isBerlinStarted = self.gameEventController.isBerlinStarted()
        if not isBerlinStarted:
            self.gameEventController.setBerlinTabShown(False)
            self._callBack.stopCallback(self.__fillViewModel)
            self._callBack.delayCallback(berlinStartTimeLeft, self.__fillViewModel)
        self._updateBerlinStartTimeLeft()
        self.viewModel.setIsStarted(isBerlinStarted)
        self.viewModel.setCurrentView(ActionMenuModel.BERLIN)
        self.__fillMegaPack()
        if isBerlinStarted and not self.gameEventController.istBerlinTabShown():
            for item in self.viewModel.menuItems.getItems():
                if item.getViewId() == ActionMenuModel.BERLIN:
                    item.setIsNotification(False)
                    self.gameEventController.setBerlinTabShown(True)
                    self.viewModel.menuItems.invalidate()
                    break

    def __fillMegaPack(self):
        shopItem = self.gameEventController.getShop().getMegaPack()
        self.viewModel.setShowPack(shopItem is not None)
        if shopItem is None:
            return
        else:
            self._updateEventTimeLeft()
            self.__orderID = shopItem.packID
            cacheKey = crc32(self.__orderID)
            rewards = self.getRewards(shopItem, cacheKey)
            with self.viewModel.transaction() as vm:
                self.fillPriceByShopItem(vm.price, shopItem)
                bonuses = []
                for idx, bonus in enumerate(rewards):
                    energyID = first(bonus['specialArgs'] or [])
                    if not (isinstance(energyID, str) and energyID.startswith(ENERGY_TOKEN_PREFIX)):
                        bonuses.append((idx, bonus))

                self.fillStubRewardListWithIndex(vm.rewardList, bonuses, cacheKey=cacheKey)
            return

    def __onSyncCompleted(self, *_):
        self.__fillViewModel()

    def __onBuyPack(self):
        shopItem = self.gameEventController.getShop().getItem(self.__orderID)
        currency, price = shopItem.getPrice()
        if not bool(self._stats.money.getShortage(convertPriceToMoney(currency, price))):
            showOrderBuyDialog(orderID=self.__orderID, parentID=self.__layoutID)
        else:
            showBuyGoldForSecretEventItem(price)
