# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_lootbox_open_view.py
import logging
import typing
import BigWorld
import ScaleformFileLoader
from async import async, await, AsyncReturn
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from adisp import process
from gui.impl.dialogs.dialogs import showExchangeToRerollDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_lootbox_open_view_model import WtEventLootboxOpenViewModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_reroll_tooltip_view import WtEventLootboxRerollTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.events import LobbySimpleEvent
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.event_dispatcher import showWtEventStorageBoxesWindow, showWtEventBoxRewardWindow, showWtEventConfirmReRollWindow, showWtEventConfirmOutOfTheBoxWindow, showWtEventErrorLootBoxWindow, isViewLoaded
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor, LootBoxRerollProcessor, LootBoxReRollRecordsProcessor
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.shared.money import Currency
from gui.shop import showBuyGoldForLootBoxReRoll, showLootBoxBuyWindow
from gui.sounds.filters import switchHangarFilteredFilter
from gui.wt_event.wt_event_award import WTEventLootBoxAwardsManager
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.Scaleform.Waiting import Waiting
from gui.wt_event.wt_event_helpers import backportTooltipDecorator, fillStatsModel, vehCompCreateToolTipContentDecorator, stripLootBoxFromRewards
from gui.wt_event.wt_event_notification_helpers import pushReRollSuccessNotification, pushReRollFailedNotification, pushLootBoxRewardsNotification
from shared_utils import findFirst
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IGameEventController, IEventLootBoxesController, IWalletController
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
_LOCK_SOURCE_NAME = 'eventLootBoxOpenView'
_HIDE_DEFAULT_LOOTBOX_TIMER = 1.0
_BLUE_IDLE = 'gui/flash/videos/wt_event/LootBox_Blue-Idle.usm'
_BLUE_OPEN = 'gui/flash/videos/wt_event/LootBox_Blue-Open.usm'
_BLUE_LOOP = 'gui/flash/videos/wt_event/LootBox_Blue-Loop.usm'
_RED_IDLE = 'gui/flash/videos/wt_event/LootBox_Red-Idle.usm'
_RED_OPEN = 'gui/flash/videos/wt_event/LootBox_Red-Open.usm'
_RED_LOOP = 'gui/flash/videos/wt_event/LootBox_Red-Loop.usm'
_YELLOW_IDLE = 'gui/flash/videos/wt_event/LootBox_Yellow-Idle.usm'
_YELLOW_OPEN = 'gui/flash/videos/wt_event/LootBox_Yellow-Open.usm'
_YELLOW_LOOP = 'gui/flash/videos/wt_event/LootBox_Yellow-Loop.usm'

def _getStreamURLs(boxType):
    return {'wt_special': [_YELLOW_IDLE, _YELLOW_OPEN, _YELLOW_LOOP],
     'wt_boss': [_RED_IDLE, _RED_OPEN, _RED_LOOP],
     'wt_hunter': [_BLUE_IDLE, _BLUE_OPEN, _BLUE_LOOP]}.get(boxType, [])


def _getAnimationTypeForReroll(isFirstOpen, needToShowRewards):
    if isFirstOpen:
        if needToShowRewards:
            return 'openBoxAndShow'
        return 'openBox'
    return 'rerollBoxAndShow' if needToShowRewards else 'rerollBox'


class WtEventLootboxOpenView(ViewImpl):
    __slots__ = ('__boxType', '__box', '__lootBoxRewards', '__lootBoxReRerollRecords', '_tooltipItems', '__goldBonus', '__processingLootbox', '__isOverlayLocked', '__hideLootboxTimerCallback')
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    eventController = dependency.descriptor(IGameEventController)
    lootBoxesController = dependency.descriptor(IEventLootBoxesController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    wallet = dependency.descriptor(IWalletController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wt_event.WtEventLootboxOpenView())
        settings.flags = ViewFlags.OVERLAY_VIEW
        settings.model = WtEventLootboxOpenViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__boxType = kwargs.get('boxType')
        self.__box = self.lootBoxesController.getOwnedLootBoxByType(self.__boxType)
        self.__lootBoxReRerollRecords = {}
        self.__goldBonus = None
        self.__isOverlayLocked = False
        self.__processingLootbox = False
        self._tooltipItems = {}
        self.__hideLootboxTimerCallback = None
        super(WtEventLootboxOpenView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(WtEventLootboxOpenView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(WtEventLootboxOpenView, self)._onLoaded(self, *args, **kwargs)
        if self.viewModel.getBoxState() == 'closed':
            wt_event_sound.playLootBoxSelect()

    def _onLoading(self, *args, **kwargs):
        Waiting.show('loadPage')
        self.__loadInitialLootBoxState(needToUpdateReRollRecords=True)
        self.__updateStats()
        wt_event_sound.setLootBoxState(self.__boxType)
        super(WtEventLootboxOpenView, self)._onLoading()

    def _initialize(self, *args, **kwargs):
        super(WtEventLootboxOpenView, self)._initialize(*args, **kwargs)
        ScaleformFileLoader.enableStreaming(_getStreamURLs(self.__boxType))
        self.viewModel.openBox += self.onOpenBox
        self.viewModel.pickReward += self.onPickReward
        self.viewModel.runPickRewardAnimation += self.onRunPickRewardAnimation
        self.viewModel.showRerollRewardOverlay += self.showRerollRewardOverlay
        self.viewModel.goToStorage += self.onGoToStorage
        self.viewModel.goToBuySpecial += self.onGoToBuySpecial
        self.viewModel.videoReady += self.__onVideoReady
        self.viewModel.close += self.__onClose
        self.viewModel.onShowRewards += self.__onShowRewards
        self.itemsCache.onSyncCompleted += self.__updateStats
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.wallet.onWalletStatusChanged += self.__updateStats
        self.eventController.onEventUpdated += self.__onEventUpdated
        g_eventBus.addListener(events.ShopEvent.SHOP_DEACTIVATED, self.__onShopDeactivated)
        g_eventBus.addListener(events.ShopEvent.SHOP_ACTIVATED, self.__onShopActivated)

    def _finalize(self):
        super(WtEventLootboxOpenView, self)._finalize()
        self.viewModel.openBox -= self.onOpenBox
        self.viewModel.pickReward -= self.onPickReward
        self.viewModel.runPickRewardAnimation -= self.onRunPickRewardAnimation
        self.viewModel.showRerollRewardOverlay -= self.showRerollRewardOverlay
        self.viewModel.goToStorage -= self.onGoToStorage
        self.viewModel.goToBuySpecial -= self.onGoToBuySpecial
        self.viewModel.videoReady -= self.__onVideoReady
        self.viewModel.close -= self.__onClose
        self.viewModel.onShowRewards -= self.__onShowRewards
        self.itemsCache.onSyncCompleted -= self.__updateStats
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.wallet.onWalletStatusChanged -= self.__updateStats
        self.eventController.onEventUpdated -= self.__onEventUpdated
        g_eventBus.removeListener(events.ShopEvent.SHOP_DEACTIVATED, self.__onShopDeactivated)
        g_eventBus.removeListener(events.ShopEvent.SHOP_ACTIVATED, self.__onShopActivated)
        self._tooltipItems = None
        self.__unlockOverlays()
        switchHangarFilteredFilter(False)
        if self.__hideLootboxTimerCallback is not None:
            self.__hideWaiting()
        return

    def __destroyWindow(self, isTransition=False):
        if self.__hideLootboxTimerCallback is not None:
            BigWorld.cancelCallback(self.__hideLootboxTimerCallback)
        ScaleformFileLoader.disableStreaming()
        if not isTransition:
            wt_event_sound.playLootBoxExit()
        self.destroyWindow()
        return

    @async
    def __onClose(self):
        result = yield await(self.__confirmOut())
        if result:
            self.__destroyWindow()

    def __onVideoReady(self):
        Waiting.hide('loadPage')

    def __loadInitialLootBoxState(self, needToUpdateReRollRecords=False):
        self.viewModel.setAccrued(0)
        self.viewModel.setShowAccrued(False)
        self.viewModel.rewardData.clearItems()
        if needToUpdateReRollRecords:
            self.getRollRecords(initialLoad=True, onSuccessCallback=self.fillLootBoxData)

    @vehCompCreateToolTipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return WtEventLootboxRerollTooltipView(self.__boxType) if contentID == R.views.lobby.wt_event.tooltips.WtEventLootboxOpenRerollTooltipView() else super(WtEventLootboxOpenView, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WtEventLootboxOpenView, self).createToolTip(event)

    def onPickReward(self):
        if self.__box is not None:
            self.openBox(self.__box.getID())
        return

    def onRunPickRewardAnimation(self):
        self.viewModel.setAnimationType('collectBox')

    @async
    def showRerollRewardOverlay(self):
        rollCount = self.__lootBoxReRerollRecords.get(self.__boxType, {}).get('count', 0)
        currency, price = self.__box.getReRollPrice(reRolledAttempts=rollCount)
        if currency == Currency.GOLD and self.itemsCache.items.stats.gold < price:
            showBuyGoldForLootBoxReRoll(price)
            return
        if currency == Currency.CREDITS and self.itemsCache.items.stats.credits < price:
            self.setHasChildOverlay(True)
            exchangeResult = yield await(showExchangeToRerollDialog(price, self.__boxType, self.getParentWindow()))
            self.setHasChildOverlay(False)
            if exchangeResult.busy or not exchangeResult.result:
                return
        showWtEventConfirmReRollWindow(parent=self.getParentWindow(), lootBoxType=self.__boxType, price=(currency, price))

    def fillLootBoxData(self, initialLoad=False, rewards=None):
        self.__box = self.lootBoxesController.getOwnedLootBoxByType(self.__boxType)
        if self.__box is None:
            return
        else:
            maxAttempts = self.__box.getReRollCount()
            thisLootBoxRecords = self.__lootBoxReRerollRecords.get(self.__boxType, {})
            wastedAttempts = 0
            if thisLootBoxRecords:
                wastedAttempts = thisLootBoxRecords.get('count', 0)
            with self.viewModel.transaction() as vModelTrx:
                vModelTrx.setBoxType(self.__box.getType()[3:])
                attemptsLeft = 0
                if maxAttempts - wastedAttempts < 0:
                    currency, rollPrice = self.__box.getReRollPrice(reRolledAttempts=maxAttempts)
                else:
                    currency, rollPrice = self.__box.getReRollPrice(reRolledAttempts=wastedAttempts)
                    if wastedAttempts > 0:
                        attemptsLeft = maxAttempts - wastedAttempts + 1
                if attemptsLeft == 0:
                    _logger.debug('No attempts left, only open loot box option is available')
                vModelTrx.setRerollAttempts(attemptsLeft)
                vModelTrx.setRerollCurrency(currency)
                vModelTrx.setRerollPrice(rollPrice)
                isOpenedAfterInitialLoad = initialLoad and wastedAttempts > 0
                vModelTrx.setIsOpenedAfterInitialLoad(isOpenedAfterInitialLoad)
                if isOpenedAfterInitialLoad:
                    self.__lockOverlays()
                    self.viewModel.setBoxState('opened')
                    self.__fillRewards()
            return

    def doDestroy(self):
        self.__destroyWindow()

    def onOpenBox(self):
        if self.__box is not None:
            self.reRollBox(boxID=self.__box.getID(), isFirstOpen=True)
        return

    def onOverlayReopenButton(self):
        if self.__box is not None:
            self.reRollBox(boxID=self.__box.getID())
        return

    @async
    def onGoToStorage(self):
        result = yield await(self.__confirmOut())
        if result:
            showWtEventStorageBoxesWindow(isTransition=True)
            self.__destroyWindow(isTransition=True)

    def onGoToBuySpecial(self):
        if self.viewModel.getAnimationType() != 'collectBox':
            showLootBoxBuyWindow()

    def __fillRewards(self, items=None):
        rewards = self.viewModel.rewardData
        rewards.clearItems()
        rewardItems = None
        if self.__lootBoxReRerollRecords[self.__boxType]:
            rewardItems = self.__lootBoxReRerollRecords[self.__boxType].get('rolledRewards')
        if items is not None:
            rewardItems = items
        if rewardItems is None:
            _logger.error('Got no rewards to draw, box:%d', self.__box.getID())
            return
        else:
            with self.viewModel.transaction() as vModelTrx:
                bonuses = WTEventLootBoxAwardsManager.composeBonuses([rewardItems])
                self.__filterBonuses(bonuses)
                packBonusModelAndTooltipData(bonuses, vModelTrx.rewardData, self._tooltipItems, getWtEventBonusPacker)
            rewards.invalidate()
            self.viewModel.setRewardDataInvalidator((self.viewModel.getRewardDataInvalidator() + 1) % 1000)
            return

    @staticmethod
    def __filterBonuses(bonuses):
        vehicle = findFirst(lambda bonus: bonus.getName() == 'vehicles', bonuses)
        if vehicle is None:
            return
        else:
            slot = findFirst(lambda bonus: bonus.getName() == 'slots', bonuses)
            if slot is None:
                return
            bonuses.remove(slot)
            return

    def onBoxOpenSuccess(self, data):
        if data is None:
            _logger.error('Got empty rewards after opening boxID:%d', self.__box.getID())
            return
        else:
            stripLootBoxFromRewards(data[0], self.__box.getID())
            showWtEventBoxRewardWindow(rewards=data, lootBoxType=self.__boxType, parent=self.getParentWindow())
            return

    def onBoxOpenFail(self):
        showWtEventErrorLootBoxWindow(R.strings.wt_event.WtEventsServerErrorLootboxOpenView)
        self.__destroyWindow()

    @process
    def openBox(self, boxID, onlyRequest=False):
        boxes = self.itemsCache.items.tokens.getLootBoxes().values()
        boxItem = None
        for box in boxes:
            if box.getID() == boxID:
                boxItem = box
                break

        if boxItem is None:
            _logger.warning('No box with ID %d found', boxID)
            return
        elif boxItem.getInventoryCount() <= 0:
            _logger.warning('Can not open box, not enough in inventory, requested count: %d, actual: %d', 1, boxItem.getInventoryCount())
            return
        else:
            result = yield LootBoxOpenProcessor(boxItem, 1).request()
            if onlyRequest:
                return
            if result and result.success:
                _logger.info('Received rewards: %r', result.auxData)
                with self.viewModel.transaction():
                    self.onBoxOpenSuccess(result.auxData)
            else:
                self.__pushReRollFailedNotification()
                _logger.error('Box could not be opened for some reason. boxID:%d', self.__box.getID())
                self.onBoxOpenFail()
                _logger.warning('The box has not been opened, result: %r', result)
            return

    def onReRollBoxSuccess(self, data, isFirstOpen=False):
        rewardItems = data.get('rewards')
        reRollCount = data.get('reRollCount')
        guaranteedBonus = data.get('guaranteedBonus')
        if rewardItems is None:
            _logger.debug('Got no reward items from re-roll, switching to closed state')
            self.__setClosedState()
            self.__loadInitialLootBoxState(needToUpdateReRollRecords=True)
            return
        else:
            stripLootBoxFromRewards(rewardItems, self.__box.getID(), needToCheckCompensation=True)
            self.__lootBoxReRerollRecords[self.__boxType] = {'count': reRollCount,
             'rolledRewards': rewardItems}
            needToShowRewards = reRollCount == 0
            self.viewModel.setAnimationType(_getAnimationTypeForReroll(isFirstOpen=isFirstOpen, needToShowRewards=needToShowRewards))
            if self.__boxType == 'wt_special' and guaranteedBonus:
                self.__goldBonus = guaranteedBonus.get('gold')
                self.viewModel.setShowAccrued(isFirstOpen)
                self.viewModel.setAccrued(self.__goldBonus)
                pushLootBoxRewardsNotification([guaranteedBonus])
            else:
                self.viewModel.setShowAccrued(False)
                self.viewModel.setAccrued(0)
            if needToShowRewards and rewardItems:
                pushLootBoxRewardsNotification([rewardItems])
            _logger.debug('Got items from reroll: %s', rewardItems)
            self.__fillRewards(rewardItems)
            self.__lockOverlays()
            if isFirstOpen:
                self.viewModel.setBoxState('opening')
                wt_event_sound.playOpenLootBox(len(rewardItems))
            else:
                self.viewModel.setBoxState('opened')
                wt_event_sound.playReRollLootBox(len(rewardItems))
            self.fillLootBoxData(initialLoad=False, rewards=rewardItems)
            if reRollCount == 0:
                if self.__box is not None:
                    _logger.debug('Collection item is obtained. Box was opened, further re-rolls forbidden for boxID: %d', self.__box.getID())
                else:
                    _logger.debug('Collection item is obtained. Box was opened, further re-rolls forbidden')
            return

    @process
    def reRollBox(self, boxID, isFirstOpen=False):
        if self.__processingLootbox:
            return
        else:
            boxes = self.itemsCache.items.tokens.getLootBoxes().values()
            boxItem = None
            for box in boxes:
                if box.getID() == boxID:
                    boxItem = box
                    break

            if boxItem is None:
                _logger.warning('No box with ID %d found', boxID)
                return
            if boxItem.getInventoryCount() <= 0:
                _logger.warning('Can not open box, not enough in inventory, requested count: %d, actual: %d', 1, boxItem.getInventoryCount())
                return
            self.__processingLootbox = True
            result = yield LootBoxRerollProcessor(boxItem).request()
            if self.viewModel is None:
                return
            if result and result.success:
                _logger.info('Received rewards: %r', result.auxData)
                if not isFirstOpen:
                    self.__pushReRollSuccessNotification()
                with self.viewModel.transaction():
                    self.onReRollBoxSuccess(data=result.auxData, isFirstOpen=isFirstOpen)
            else:
                self.__pushReRollFailedNotification()
                self.onBoxOpenFail()
                _logger.warning('The box has not been opened, result: %r', result)
            self.__processingLootbox = False
            return

    @process
    def getRollRecords(self, initialLoad=False, onSuccessCallback=None):
        result = yield LootBoxReRollRecordsProcessor().request()
        if result and result.success:
            data = result.auxData
            _logger.info('Received reroll records data: %r', data)
            self.__lootBoxReRerollRecords = data
            if onSuccessCallback is not None:
                onSuccessCallback(initialLoad)
        else:
            self.__setClosedState()
            self.__loadInitialLootBoxState(needToUpdateReRollRecords=True)
            _logger.warning('Could not fetch info about re-roll records, result: %r', result)
        return

    def setHasChildOverlay(self, value):
        self.viewModel.setHasChildOverlay(value)
        switchHangarFilteredFilter(value)

    def resetLootBoxStates(self):
        self.getRollRecords(initialLoad=False)
        with self.viewModel.transaction():
            self.__setClosedState()
            self.__loadInitialLootBoxState()

    def __onShowRewards(self):
        rewards = self.__lootBoxReRerollRecords.get(self.__boxType, {}).get('rolledRewards')
        showWtEventBoxRewardWindow(rewards=rewards, lootBoxType=self.__boxType, parent=self.getParentWindow())

    def __updateStats(self, *_):
        if self.__box is None:
            self.__box = self.lootBoxesController.getOwnedLootBoxByType(self.__boxType)
        with self.viewModel.transaction() as model:
            model.setCurrentBoxCount(self.lootBoxesController.getEventLootBoxesCountByType(self.__boxType))
            model.setBoxCount(self.lootBoxesController.getEventLootBoxesCount())
            fillStatsModel(model.stats)
        return

    def __lockOverlays(self):
        if not self.__isOverlayLocked:
            ctx = {'source': _LOCK_SOURCE_NAME,
             'lock': True}
            g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.LOCK_OVERLAY_SCREEN, ctx), EVENT_BUS_SCOPE.LOBBY)
            self.__isOverlayLocked = True

    def __unlockOverlays(self):
        if self.__isOverlayLocked:
            ctx = {'source': _LOCK_SOURCE_NAME,
             'lock': False}
            g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.LOCK_OVERLAY_SCREEN, ctx), EVENT_BUS_SCOPE.LOBBY)
            self.__isOverlayLocked = False

    @async
    def __confirmOut(self):
        if self.__processingLootbox:
            raise AsyncReturn(False)
        rewards = self.__lootBoxReRerollRecords.get(self.__boxType, {}).get('rolledRewards')
        reRollCount = self.__lootBoxReRerollRecords.get(self.__boxType, {}).get('count')
        result = True
        if rewards and reRollCount != 0:
            self.setHasChildOverlay(True)
            result = yield showWtEventConfirmOutOfTheBoxWindow(rewards, self.getParentWindow())
            self.setHasChildOverlay(False)
            if result:
                self.openBox(self.__box.getID(), onlyRequest=True)
        raise AsyncReturn(result)

    def __setClosedState(self):
        Waiting.show('loadPage')
        self.__hideLootboxTimerCallback = BigWorld.callback(_HIDE_DEFAULT_LOOTBOX_TIMER, self.__hideWaiting)
        self.__unlockOverlays()
        self.viewModel.setAnimationType('default')
        self.viewModel.setBoxState('closed')

    def __hideWaiting(self):
        self.__hideLootboxTimerCallback = None
        Waiting.hide('loadPage')
        return

    def __onShopDeactivated(self, _):
        self.viewModel.setHasChildOverlay(False)

    def __onShopActivated(self, _):
        self.viewModel.setHasChildOverlay(True)

    def __onServerSettingChanged(self, *_):
        if self.lobbyContext.getServerSettings().isLootBoxesEnabled():
            return
        if self.viewModel.getBoxState() == 'closed' or isViewLoaded(R.views.lobby.wt_event.WtEventBoxRewardView()):
            textsR = R.strings.wt_event.WtEventsInClosedErrorLootboxOpenView
        else:
            textsR = R.strings.wt_event.WtEventsSwitcherErrorLootboxOpenView
        showWtEventErrorLootBoxWindow(textsR)
        self.__destroyWindow()

    def __onEventUpdated(self):
        if not self.eventController.isEnabled():
            self.__destroyWindow()

    def __pushReRollSuccessNotification(self):
        maxAttempts = self.__box.getReRollCount()
        thisLootBoxRecords = self.__lootBoxReRerollRecords.get(self.__boxType, {})
        wastedAttempts = 0
        if thisLootBoxRecords:
            wastedAttempts = thisLootBoxRecords.get('count', 0)
        if maxAttempts - wastedAttempts < 0:
            currency, rollPrice = self.__box.getReRollPrice(reRolledAttempts=maxAttempts)
        else:
            currency, rollPrice = self.__box.getReRollPrice(reRolledAttempts=wastedAttempts)
        pushReRollSuccessNotification(currency, rollPrice)

    @staticmethod
    def __pushReRollFailedNotification():
        pushReRollFailedNotification()


class WtEventLootboxOpenWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, boxType, parent=None):
        super(WtEventLootboxOpenWindow, self).__init__(WindowFlags.WINDOW, content=WtEventLootboxOpenView(boxType=boxType), parent=parent, decorator=None)
        return
