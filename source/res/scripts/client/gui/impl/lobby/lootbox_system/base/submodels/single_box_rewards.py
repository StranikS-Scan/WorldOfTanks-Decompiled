# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/submodels/single_box_rewards.py
from __future__ import absolute_import
import logging
from typing import TYPE_CHECKING
import SoundGroups
import Windowing
from adisp import adisp_async, adisp_process
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen.view_models.views.lobby.lootbox_system.main_view_model import SubViewID
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.single_box_rewards_view_model import SingleBoxRewardsViewModel
from gui.impl.lobby.lootbox_system.base.common import SubViewImpl
from gui.impl.lobby.lootbox_system.base.submodels.common import updateAnimationState
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.base.bonuses_packers import packBonusModelAndTooltipData, splitBonusesToExtra
from gui.lootbox_system.base.common import ViewID, Views
from gui.lootbox_system.base.decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.lootbox_system.base.sound import playVideoPauseSound, playVideoResumeSound
from gui.lootbox_system.base.utils import acceptRerollableBoxRewards, hasStopRerollToken, isShopVisible, openBoxes
from gui.lootbox_system.base.views_loaders import showItemPreview
from gui.server_events.bonuses import SimpleBonus
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.system_factory import collectLootBoxMainView
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shop import showBuyGoldForLootboxReroll
from gui.sounds.filters import StatesGroup, States
from gui.shared.event_dispatcher import showRerollBoxDialog, showExchangeGoldWindow
from gui.shared.money import Currency
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import ILootBoxSystemController
from wg_async import wg_async, wg_await
if TYPE_CHECKING:
    from typing import Dict, List
_logger = logging.getLogger(__name__)

class SingleBoxRewards(SubViewImpl):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, viewModel, parentView):
        super(SingleBoxRewards, self).__init__(viewModel, parentView)
        self.__isReopen = False
        self.__category = ''
        self.__openCount = 0
        self.__bonuses = []
        self.__extraBonuses = []
        self.__hasStopRerollToken = False
        self.__tooltipItems = {}
        self.__isVideoPlaying = False
        self.__eventName = ''
        self.__blur = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SingleBoxRewards, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(SingleBoxRewards, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tooltipItems.get(event.getArgument('tooltipId', 0))

    def initialize(self, *args, **kwargs):
        super(SingleBoxRewards, self).initialize(*args, **kwargs)
        self.__isReopen = kwargs.get('isReopen', False)
        self.__category = kwargs.get('category', '')
        self.__openCount = kwargs.get('count', 0)
        self.__updateBonusesData(first(kwargs.get('bonuses', []), []))
        self.__eventName = kwargs.get('eventName', '')
        with self.viewModel.transaction() as vmTx:
            self.__setWindowAccessible(model=vmTx)
            self.__updateData(model=vmTx)
            self.__updateCounters(model=vmTx)
            self.__updateBonuses(model=vmTx)
            self.__updateAnimationState(model=vmTx)
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def finalize(self):
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(SingleBoxRewards, self).finalize()
        return

    def _getCallbacks(self):
        moneyCallbacks = tuple((('stats.{}'.format(c), self.__onMoneyUpdated) for c in Currency.ALL))
        return super(SingleBoxRewards, self)._getCallbacks() + moneyCallbacks

    def _getEvents(self):
        return ((self.viewModel.onOpen, self.__openNext),
         (self.viewModel.onGoBack, self.__goBack),
         (self.viewModel.onPreview, self.__showPreview),
         (self.viewModel.onBuyBoxes, self.__openShop),
         (self.viewModel.onAnimationStateChanged, self.__updateAnimationState),
         (self.viewModel.onVideoPlaying, self.__setVideoPlaying),
         (self.viewModel.onClose, self.__goBack),
         (self.viewModel.onReroll, self.__rerollBox),
         (self.viewModel.onRerollDialogOpen, self.__rerollDialogOpen),
         (self.__lootBoxes.onBoxesCountChanged, self.__updateCounters),
         (self.__lootBoxes.onBoxesUpdated, self.__updateCounters),
         (self.__lootBoxes.onBoxesConfigUpdated, self.__updateCounters))

    def _getListeners(self):
        return ((events.LootBoxSystemEvent.OPENING_ERROR, self.__onErrorBack, EVENT_BUS_SCOPE.LOBBY),)

    def _getBonusPacker(self):
        return None

    def __setVideoPlaying(self, ctx=None):
        isPlaying = ctx.get('isPlaying')
        self.__isVideoPlaying = isPlaying
        SoundGroups.g_instance.setState(StatesGroup.VIDEO_OVERLAY, States.VIDEO_OVERLAY_ON if isPlaying else States.VIDEO_OVERLAY_OFF)

    @replaceNoneKwargsModel
    def __setWindowAccessible(self, model=None):
        isWindowAccessible = Windowing.isWindowAccessible()
        model.setIsWindowAccessible(isWindowAccessible)

    def __onWindowAccessibilityChanged(self, _):
        isWindowAccessible = Windowing.isWindowAccessible()
        if self.__isVideoPlaying:
            self.__setWindowAccessible()
            if isWindowAccessible:
                playVideoResumeSound(self.__eventName)
            else:
                playVideoPauseSound(self.__eventName)

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        model.setEventName(self.__eventName)
        model.setBoxCategory(self.__category)
        model.setIsReopen(self.__isReopen)
        model.setIsShopVisible(isShopVisible(self.__eventName))

    @replaceNoneKwargsModel
    def __updateCounters(self, model=None):
        model.setBoxesCount(self.__lootBoxes.getBoxesCount(self.__eventName, self.__category))
        model.setBoxesCountToGuaranteed(self.__lootBoxes.getBoxesCountToGuaranteed(self.__category))
        model.setRerollDialogRequired(self.__isRerollDialogRequired())
        self.__updateBoxReroll()

    @replaceNoneKwargsModel
    def __updateBoxReroll(self, model=None):
        with model.reroll.transaction() as rerollModel:
            box = self.__lootBoxes.getBox(self.__eventName, self.__category)
            if box is None or not box.isRerollable():
                rerollModel.setIsAvailable(False)
                return
            boxInfo = self.__lootBoxes.getBoxInfo(box.getID())
            rerollModel.setIsAvailable(True)
            enoughMoney, _, _ = self.__lootBoxes.isEnoughMoneyForReroll(box)
            rerollModel.setIsEnoughMoney(enoughMoney)
            rerollModel.setCurrency(box.getRerollCurrency())
            remainingAttempts = box.getRerollMaxAttempts() - boxInfo.get('rerollAttempts', 0)
            if remainingAttempts > 0:
                rerollModel.setPrice(box.getRerollPrices()[-remainingAttempts])
            rerollModel.setAttemptsLeft(remainingAttempts)
            rerollModel.setHasSpecialReward(self.__hasStopRerollToken)
        return

    @replaceNoneKwargsModel
    def __updateBonuses(self, model=None):
        model.bonuses.clearItems()
        model.extraBonuses.clearItems()
        packBonusModelAndTooltipData(self.__bonuses, model.bonuses, tooltipData=self.__tooltipItems, merge=False, eventName=self.__eventName, showLootboxCompensation=True, packer=self._getBonusPacker())
        packBonusModelAndTooltipData(self.__extraBonuses, model.extraBonuses, tooltipData=self.__tooltipItems, merge=False, eventName=self.__eventName, packer=self._getBonusPacker())
        model.bonuses.invalidate()
        model.extraBonuses.invalidate()

    @replaceNoneKwargsModel
    def __updateAnimationState(self, ctx=None, model=None):
        updateAnimationState(model, ctx, self.__eventName)

    def __processOpenBoxResult(self, bonuses):
        self.viewModel.setIsAwaitingResponse(False)
        self.viewModel.setIsRerollConfirmed(False)
        self.viewModel.setBoxCategory(self.__category)
        self.__updateBonusesData(first(bonuses))
        self.__updateCounters()
        self.__updateBonuses()
        self.__updateStateContext(bonuses=bonuses)

    def __isRerollDialogRequired(self):
        box = self.__lootBoxes.getBox(self.__eventName, self.__category)
        if box is None or not box.isRerollable():
            return False
        else:
            boxInfo = self.__lootBoxes.getBoxInfoByCategory(self.__category)
            rerollAttempts = boxInfo['rerollAttempts']
            prices = box.getRerollPrices()
            if rerollAttempts >= len(prices):
                return False
            price = prices[rerollAttempts]
            return price != 0

    @wg_async
    def __showExchange(self, currencyValue, currencyName):
        if currencyName == Currency.GOLD:
            showBuyGoldForLootboxReroll(currencyValue)
        elif currencyName == Currency.CREDITS:
            self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.TOP_WINDOW)
            yield wg_await(showExchangeGoldWindow(ctx={'gold': currencyValue,
             'blur': None}, layer=WindowLayer.TOP_WINDOW, doBlur=False))
            if self.__blur is not None:
                self.__blur.fini()
            self.__blur = None
        return

    @wg_async
    def __rerollDialogOpen(self):
        box = self.__lootBoxes.getBox(self.__eventName, self.__category)
        enoughMoney, currencyName, currencyAmount = self.__lootBoxes.isEnoughMoneyForReroll(box)
        if not enoughMoney:
            yield wg_await(self.__showExchange(currencyAmount, currencyName))
            return
        boxInfo = self.__lootBoxes.getBoxInfoByCategory(self.__category)
        rerollAttempts = boxInfo['rerollAttempts']
        prices = box.getRerollPrices()
        price = prices[rerollAttempts]
        currency = box.getRerollCurrency()
        shouldSend = True
        if price != 0:
            shouldSend = yield wg_await(showRerollBoxDialog(self.__eventName, price, currency))
            enoughMoney, currencyName, currencyAmount = self.__lootBoxes.isEnoughMoneyForReroll(box)
            if not enoughMoney:
                yield wg_await(self.__showExchange(currencyAmount, currencyName))
                return
        if shouldSend:
            self.viewModel.setIsAwaitingResponse(True)
            self.viewModel.setIsRerollConfirmed(True)

    def __openNext(self, ctx=None):
        category = ctx.get('category') if ctx is not None else ''
        if category:
            self.__category = category
        self.__isReopen = False
        self.viewModel.setIsAwaitingResponse(True)
        openBoxes(self.__eventName, self.__category, self.__openCount, self.__processOpenBoxResult)
        return

    @wg_async
    def __rerollBox(self, ctx=None):
        category = ctx.get('category') if ctx is not None else ''
        if category:
            self.__category = category
        box = first(self.__lootBoxes.getActiveBoxes(self.__eventName, lambda b: b.getCategory() == self.__category))
        enoughMoney, currencyName, currencyAmount = self.__lootBoxes.isEnoughMoneyForReroll(box)
        if not enoughMoney:
            yield wg_await(self.__showExchange(currencyAmount, currencyName))
            return
        else:
            self.__isReopen = False
            self.viewModel.setIsAwaitingResponse(True)
            openBoxes(self.__eventName, self.__category, self.__openCount, self.__processOpenBoxResult, isReroll=True)
            return

    @adisp_process
    def __goBack(self):
        canNavigate = yield self.__ensureRerollRewardsAccepted()
        if canNavigate:
            Views.load(ViewID.MAIN, eventName=self.__eventName)

    def __onErrorBack(self, *_):
        self.viewModel.setIsAwaitingResponse(False)
        box = self.__lootBoxes.getBox(self.__eventName, self.__category)
        if box is None or box.isRerollable():
            self.destroy()
            return
        else:
            Views.load(ViewID.MAIN, eventName=self.__eventName)
            return

    def __showPreview(self, ctx):
        showItemPreview(str(ctx.get('bonusType')), int(ctx.get('bonusId')), int(ctx.get('styleID')))

    @adisp_process
    def __openShop(self):
        canNavigate = yield self.__ensureRerollRewardsAccepted()
        if canNavigate:
            box = self.__lootBoxes.getBox(self.__eventName, self.__category)
            if box is not None and box.isRerollable():
                self.__updateStateContext(subViewID=SubViewID.HOME)
            Views.load(ViewID.SHOP, eventName=self.__eventName)
        return

    def __updateBonusesData(self, bonuses):
        self.__hasStopRerollToken = hasStopRerollToken(bonuses)
        self.__extraBonuses = []
        if len(bonuses) == 1:
            self.__bonuses = bonuses
            return
        self.__bonuses = []
        self.__bonuses, self.__extraBonuses = splitBonusesToExtra(bonuses, eventName=self.__eventName)

    def __updateStateContext(self, **kwargs):
        lsm = getLobbyStateMachine()
        stateViewKey = ViewKey(VIEW_ALIAS.LOOT_BOXES_MAIN_VIEW)
        for validator, viewKey in collectLootBoxMainView():
            if validator():
                stateViewKey = viewKey

        lsm.getStateByViewKey(stateViewKey).updateCachedCtx(kwargs)

    def __onMoneyUpdated(self, _):
        self.__updateBoxReroll()

    @adisp_async
    @adisp_process
    def __ensureRerollRewardsAccepted(self, callback):
        success = True
        if self.__eventName and self.__category:
            if self.__lootBoxes.getPendingRerollRewards(self.__eventName, self.__category) is not None:
                self.viewModel.setIsAwaitingResponse(True)
                success = yield acceptRerollableBoxRewards(self.__eventName, self.__category)
                self.viewModel.setIsAwaitingResponse(False)
                if not success:
                    self.destroy()
        callback(success)
        return
