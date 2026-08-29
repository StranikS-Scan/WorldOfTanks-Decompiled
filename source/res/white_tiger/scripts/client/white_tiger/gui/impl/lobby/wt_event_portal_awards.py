# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_portal_awards.py
import logging
from functools import partial
import BigWorld
from BWUtil import AsyncReturn
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_LAUNCH_ANIMATED
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes, ReRollButton
from th_async import th_await, th_async
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui import shop
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.backport import createTooltipData
from gui.impl.dialogs import dialogs
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from gui.impl.dialogs.sub_views.content.single_price_content import SinglePriceContent
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_rewards.wt_portal_rewards_model import WtPortalRewardsModel
from white_tiger.gui.impl.lobby.wt_event_base_portal_awards_view import WtEventBasePortalAwards
from white_tiger.gui.impl.lobby.tooltips.wt_guaranteed_reward_tooltip_view import WtGuaranteedRewardTooltipView
from white_tiger.gui.impl.lobby import wt_event_sound
from white_tiger.gui.impl.lobby.wt_event_portal import WTEventPortalView
from white_tiger.gui.impl.lobby.wt_event_sound import playLootBoxPortalExit
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.lobby_window import LobbyWindow
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.Waiting import Waiting
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency
from white_tiger.gui.impl.lobby.packers.wt_event_simple_bonus_packers import sortBonuses, HUNTER_BONUSES_ORDER
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import getWtEventBonusPacker, BOSS_ALL_BONUSES_ORDER
from white_tiger.gui.wt_event_models_helper import setLootBoxesCount, setGuaranteedReward
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.shared import IItemsCache
from frameworks.wulf.gui_constants import ShowingStatus
from white_tiger.gui.shared.event_dispatcher import showEventPortalAwardsWindow
_logger = logging.getLogger(__name__)

class WtEventPortalAwards(WtEventBasePortalAwards, CallbackDelayer):
    __slots__ = ('__lootBoxType', '__boxCount')
    __itemsCache = dependency.descriptor(IItemsCache)
    __SPECIAL_TOOLTIPS = {Currency.GOLD: TOOLTIPS_CONSTANTS.GOLD_INFO,
     Currency.CREDITS: TOOLTIPS_CONSTANTS.CREDITS_INFO,
     Currency.CRYSTAL: TOOLTIPS_CONSTANTS.CRYSTAL_INFO,
     Currency.FREE_XP: TOOLTIPS_CONSTANTS.FREEXP_INFO}

    def __init__(self, lootBoxType, awards, count, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.WtPortalRewardsView(), model=WtPortalRewardsModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventPortalAwards, self).__init__(settings, awards)
        self.__lootBoxType = lootBoxType
        self.__boxCount = count
        self.__rerollCost = 0
        self.__wasLootAutoClaimed = False
        self.__priceType = None
        self.__animationState = AccountSettings.getSettings(IS_LAUNCH_ANIMATED)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return WtGuaranteedRewardTooltipView() if contentID == R.views.white_tiger.lobby.tooltips.GuaranteedRewardTooltipView() else super(WtEventPortalAwards, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WtEventPortalAwards, self)._onLoading()
        self._setSelectedBoxCount(self.__boxCount)
        self._updateBoxCount()

    def _onLoaded(self, *args, **kwargs):
        super(WtEventPortalAwards, self)._onLoaded(*args, **kwargs)
        Waiting.hide('updating')
        wt_event_sound.playLootBoxAwardsReceived(self.__boxCount)

    def _finalize(self):
        wt_event_sound.playLootBoxAwardsExit()
        super(WtEventPortalAwards, self)._finalize()

    def _updateBoxCount(self):
        pendingBoxes = self._boxesCtrl.getPendingBoxesCount(self.__lootBoxType)
        self._boxesCtrl.updateLastViewedCount()
        with self.viewModel.transaction() as model:
            setLootBoxesCount(model, self.__lootBoxType, pendingBoxes)

    def _setSelectedBoxCount(self, boxCount):
        with self.viewModel.transaction() as model:
            model.setSelectedLootBoxesCount(boxCount)

    def _updateModel(self):
        super(WtEventPortalAwards, self)._updateModel()
        with self.viewModel.transaction() as model:
            model.getRewards().clear()
            self._tooltipItems.clear()
            isBossLootBox = self.__isBossLootBox()
            model.setIsBossLootBox(isBossLootBox)
            model.setIsLaunchAnimated(AccountSettings.getSettings(IS_LAUNCH_ANIMATED))
            if isBossLootBox:
                self.__setBossModelParameters(model, WhiteTigerLootBoxes.WT_BOSS)
            else:
                _fillMainAwards(WhiteTigerLootBoxes.WT_HUNTER, model.getRewards(), self._awards, self._tooltipItems)
            self.__setRerollParameters(model.reroll, isBossLootBox)
            self.__setCurrencyBalanceParameters(model.currencyBalance)

    def __setBossModelParameters(self, model, boxType):
        self.__wasLootAutoClaimed = self._boxesCtrl.isStopTokenAmongRewardList(self._awards, boxType)
        rerollCount = self._boxesCtrl.getReRollAttemptsCount(self.__lootBoxType)
        if self.__wasLootAutoClaimed:
            model.setIsFirstLaunch(not self._boxesCtrl.isEngineerReroll())
        else:
            model.setIsFirstLaunch(rerollCount == 1)
        extra = self._boxesCtrl.getExtraRewards(self.__lootBoxType, count=0)
        model.setFirstLaunchReward(extra.get('gold', 0) if extra else 0)
        _fillBossAwards(model, self._awards, self._tooltipItems)
        setGuaranteedReward(model.guaranteedReward)

    def __setRerollParameters(self, rerollModel, isBossLootBox):
        boxType = WhiteTigerLootBoxes.WT_BOSS if isBossLootBox else WhiteTigerLootBoxes.WT_HUNTER
        reRollPrice = self._boxesCtrl.getReRollPrice(boxType)
        if reRollPrice is not None:
            self.__priceType = self._boxesCtrl.getReRollPriceType(boxType)
            self.__rerollCost = reRollPrice.get(self.__priceType) * self.__boxCount
            rerollModel.setCount(self._boxesCtrl.getReRollAttemptsLeft(boxType))
            rerollModel.setIsAffordable(self._boxesCtrl.hasAccountEnoughMoneyForReRoll(boxType))
            rerollModel.setCurrency(self.__priceType)
            rerollModel.setPrice(self.__rerollCost)
        else:
            rerollModel.setIsAffordable(False)
            rerollModel.setCount(0)
            self.__rerollCost = 0
        return

    def __setCurrencyBalanceParameters(self, currencyBalanceModel):
        for tooltipId in self.__SPECIAL_TOOLTIPS.values():
            self._tooltipItems[tooltipId] = createTooltipData(isSpecial=True, specialAlias=tooltipId)

        currencyBalanceModel.setIsWalletAvailable(self.__itemsCache.items.stats.mayConsumeWalletResources)
        currencyBalanceModel.setCredits(int(self.__itemsCache.items.stats.money.getSignValue(Currency.CREDITS)))
        currencyBalanceModel.setGold(int(self.__itemsCache.items.stats.money.getSignValue(Currency.GOLD)))
        currencyBalanceModel.setCrystal(int(self.__itemsCache.items.stats.money.getSignValue(Currency.CRYSTAL)))
        currencyBalanceModel.setFreeXp(self.__itemsCache.items.stats.freeXP)

    def _onServerSettingsChange(self, diff):
        super(WtEventPortalAwards, self)._onServerSettingsChange(diff)
        self._updateModel()

    def _addListeners(self):
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        self.viewModel.onClaimReward += self._claimReward
        self.viewModel.onReroll += self.__reRollLoot
        self.viewModel.onAnimationSettingChange += self.__switchAnimationSetting
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.__onGoldChange)
        super(WtEventPortalAwards, self)._addListeners()

    def _removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync
        self.viewModel.onClaimReward -= self._claimReward
        self.viewModel.onReroll -= self.__reRollLoot
        self.viewModel.onAnimationSettingChange -= self.__switchAnimationSetting
        g_clientUpdateManager.removeCurrencyCallback(Currency.GOLD, self.__onGoldChange)
        super(WtEventPortalAwards, self)._removeListeners()

    @th_async
    def _onClose(self, args=None):
        self.viewModel.setIsViewActive(False)
        isBoxesEnabled = self._boxesCtrl.isEnabled()
        if isBoxesEnabled:
            if self.__isBossLootBox():
                wasCanceledByDialog = yield th_await(self.__isCanceledByDialog())
                if wasCanceledByDialog:
                    self.viewModel.setIsViewActive(True)
                    return
            if not self.__wasLootAutoClaimed:
                self._boxesCtrl.claimReRolledReward(self.__lootBoxType, 1, parentWindow=self.getParentWindow())
        selectedBoxNumber = self.__boxCount
        if args:
            selectedBoxNumber = args.get('runCounter', self.__boxCount)
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, ctx={'runCounter': selectedBoxNumber}), scope=EVENT_BUS_SCOPE.LOBBY)
        super(WtEventPortalAwards, self)._onClose()

    def _getBoxType(self):
        return self.__lootBoxType

    def _goToPreview(self, args):
        intCD = int(args.get('intCD', 0))
        if intCD == 0:
            _logger.error('Invalid intCD to preview the bonus')
            return
        else:
            item = self.__itemsCache.items.getItemByCD(intCD)
            if item is None:
                _logger.error('Invalid intCD to preview the bonus vehicle')
                return
            itemType = item.itemTypeID
            if itemType == GUI_ITEM_TYPE.VEHICLE:
                self._showVehiclePreview(intCD)
            elif itemType == GUI_ITEM_TYPE.STYLE:
                vehicleCD = getVehicleCDForStyle(item)
                event_dispatcher.showStylePreview(vehicleCD, item, item.getDescription(), partial(_backToAwardView, self.__lootBoxType, self._awards), backBtnDescrLabel=backport.text(R.strings.event.awardView.backToAwards()))
            return

    @th_async
    def _goToPortals(self):
        wasCanceledByDialog = yield th_await(self.__isCanceledByDialog())
        if wasCanceledByDialog:
            return
        if not self.__wasLootAutoClaimed:
            self._boxesCtrl.claimReRolledReward(self.__lootBoxType, 1, parentWindow=self.getParentWindow())
        playLootBoxPortalExit()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        event_dispatcher.showEventStorageWindow()

    def __goToPortal(self):
        Waiting.hide('updating')
        self.__returnProperSoundEnvironment()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroyWindow()

    @th_async
    def __reRollLoot(self):
        if not self._boxesCtrl.hasAccountEnoughMoneyForReRoll(self.__lootBoxType):
            shop.showBuyGoldForReroll(self.__rerollCost)
            return
        self.viewModel.setIsViewActive(False)
        Waiting.show('lootboxReroll')
        from gui.shared.money import Money
        dialogTitle = R.strings.dialogs.rerollReward.title()
        dialogContentDescription = R.strings.dialogs.rerollReward.message()
        dialogTemplateView = DialogTemplateView()
        dialogTemplateView.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(dialogTitle))
        if self.__priceType == 'credits':
            price = Money(credits=self.__rerollCost)
        else:
            price = Money(gold=self.__rerollCost)
        cost = ItemPrice(price=price, defPrice=price)
        dialogTemplateView.setSubView(DefaultDialogPlaceHolders.CONTENT, SinglePriceContent(dialogContentDescription, cost))
        dialogTemplateView.addButton(ConfirmButton(R.strings.dialogs.rerollReward.confirm()))
        dialogTemplateView.addButton(CancelButton(R.strings.dialogs.rerollReward.cancel()))
        if self.__isLowPreset():
            dialogTemplateView.setBackgroundDimmerAlpha(0.9)
        doBlur = False if self.__isLowPreset() else True
        dialog = FullScreenDialogWindowWrapper(dialogTemplateView, doBlur=doBlur)
        dialog.onShowingStatusChanged += self.__dialogShowingStatusChanged
        dialog.load()
        result = yield th_await(dialog.wait())
        dialog.onShowingStatusChanged -= self.__dialogShowingStatusChanged
        dialog.destroy()
        self.viewModel.setIsViewActive(True)
        if result.result == DialogButtons.SUBMIT:
            self.__openMore(ReRollButton.REROLL)

    def __dialogShowingStatusChanged(self, newStatus):
        if newStatus == ShowingStatus.SHOWN:
            Waiting.hide('lootboxReroll')

    def _claimReward(self, args=None):
        Waiting.hide('updating')
        with self.viewModel.transaction() as model:
            lootboxesCount = model.getLootBoxesCount()
            callback = self.__openNextLootbox if lootboxesCount > 0 else self.__goToPortal
            Waiting.show('updating')
            boxes = args.get('runCounter', 0)
            self.__boxCount = lootboxesCount if boxes > lootboxesCount else boxes
            self._setSelectedBoxCount(self.__boxCount)
            if self.__wasLootAutoClaimed:
                callback()
            else:
                self._boxesCtrl.claimReRolledReward(self.__lootBoxType, self.__boxCount, parentWindow=self.getParentWindow(), callbackUpdate=callback, callbackFailure=self.__onRequestFailure)
            self.viewModel.setIsViewActive(True)

    def __onGoldChange(self, _):
        self._updateModel()

    def __openNextLootbox(self):
        self.__openMore(None)
        return

    def __onRequestFailure(self):
        Waiting.hide('updating')

    def __returnProperSoundEnvironment(self):
        parent = self.getParentWindow()
        if parent and parent.parent:
            portalView = parent.parent.content
            if isinstance(portalView, WTEventPortalView):
                wt_event_sound.changePortalState(portalView.portalType)
                return
        _logger.error("Couldn't play proper sound event, because parent environment is unavailable")

    def __onCacheResync(self, _, diff):
        self.__updateLimits()
        self._updateModel()
        self._updateBoxCount()

    def __updateLimits(self):
        with self.viewModel.transaction() as model:
            setGuaranteedReward(model.guaranteedReward)

    def __switchAnimationSetting(self):
        self.__animationState = not self.__animationState
        AccountSettings.setSettings(IS_LAUNCH_ANIMATED, self.__animationState)

    def __openMore(self, reRollButtonUsed):
        parent = self.getParentWindow()

        def update(data):
            if not self._boxesCtrl.isEngineerReroll():
                self._updateBoxCount()
            self.__updateData(data)

        self._boxesCtrl.requestLootBoxRoll(self.__lootBoxType, boxCount=self.__boxCount, parentWindow=parent, callback=update, reRollButtonUsed=reRollButtonUsed, callbackFailure=self.__handleRerollFailure)

    def __updateData(self, data):
        Waiting.hide('updating')
        if data:
            self._awards = data.get('awards', [])
            self._updateModel()
            wt_event_sound.playLootBoxAwardsReceived(self.__boxCount)

    def __handleRerollFailure(self):
        Waiting.hide('updating')
        self.destroyWindow()

    def __isBossLootBox(self):
        return self.__lootBoxType == WhiteTigerLootBoxes.WT_BOSS

    @staticmethod
    def __isLowPreset():
        presetIndex = BigWorld.detectGraphicsPresetFromSystemSettings()
        medPresetIndex = BigWorld.getSystemPerformancePresetIdFromName('MEDIUM')
        return presetIndex > medPresetIndex

    @th_async
    def __isCanceledByDialog(self):
        if not self.__wasLootAutoClaimed:
            builder = ResDialogBuilder()
            builder.setMessagesAndButtons(R.strings.dialogs.confirmReward)
            builder.setShowBalance(True)
            if self.__isLowPreset():
                builder.setDimmerAlpha(0.9)
                builder.setBlur(False)
            result = yield th_await(dialogs.show(builder.build()))
            if result.result != DialogButtons.SUBMIT:
                raise AsyncReturn(True)
        raise AsyncReturn(False)


class WtEventPortalAwardsWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, lootBoxType, awards, count, parent=None):
        super(WtEventPortalAwardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtEventPortalAwards(lootBoxType=lootBoxType, awards=awards, count=count), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)


def _backToAwardView(lootBoxType, awards):
    Waiting.show('updating')
    event_dispatcher.showHangar()
    showEventPortalAwardsWindow(lootBoxType, awards)
    Waiting.hide('updating')


def _fillBossAwards(model, bonuses, tooltipItems):
    rewardsModel = model.getRewards()
    rewardsModel.clear()
    packBonusModelAndTooltipData(bonuses, rewardsModel, tooltipItems, getWtEventBonusPacker())
    rewardsModel.invalidate()


def _fillMainAwards(lootBoxType, model, bonuses, tooltipItems):
    model.clear()
    order = BOSS_ALL_BONUSES_ORDER if lootBoxType == WhiteTigerLootBoxes.WT_BOSS else HUNTER_BONUSES_ORDER
    packBonusModelAndTooltipData(sorted(bonuses, key=lambda bonus: sortBonuses(bonus, order)), model, tooltipItems, getWtEventBonusPacker())
    model.invalidate()
