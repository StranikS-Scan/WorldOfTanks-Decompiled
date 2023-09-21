# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_portal_awards.py
import logging
from functools import partial
from BWUtil import AsyncReturn
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_LAUNCH_ANIMATED
from wg_async import wg_await, wg_async
from constants import Configs
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
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_awards_model import WtEventPortalAwardsModel, currencyTooltipTypes
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.wt_event.wt_event_base_portal_awards_view import WtEventBasePortalAwards
from gui.impl.lobby.wt_event.tooltips.wt_guaranteed_reward_tooltip_view import WtGuaranteedRewardTooltipView
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.lobby.wt_event.wt_event_portal import WTEventPortalView
from gui.impl.lobby.wt_event.wt_event_sound import playLootBoxPortalExit, WTEventAwardsScreenVideoSound
from gui.impl.lobby.wt_event.wt_event_vehicle_portal import ReRollButton
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.lobby_window import LobbyWindow
from gui.game_control.loot_boxes_controller import LootBoxAwardsManager
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.Waiting import Waiting
from gui.shared import event_dispatcher, g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.money import Currency
from gui.wt_event.wt_event_simple_bonus_packers import sortBonuses, HUNTER_BONUSES_ORDER
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker, BOSS_ALL_BONUSES_ORDER
from gui.wt_event.wt_event_models_helper import setLootBoxesCount, setGuaranteedAward, fillAdditionalAwards, fillVehicleAward
from helpers import dependency, server_settings
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class WtEventPortalAwards(WtEventBasePortalAwards, CallbackDelayer):
    __slots__ = ('__lootBoxType', '__count', '__openedCount', '__allOpenedBoxesCount')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __SPECIAL_TOOLTIPS = {Currency.GOLD: TOOLTIPS_CONSTANTS.GOLD_INFO,
     Currency.CREDITS: TOOLTIPS_CONSTANTS.CREDITS_INFO,
     Currency.CRYSTAL: TOOLTIPS_CONSTANTS.CRYSTAL_INFO,
     Currency.FREE_XP: TOOLTIPS_CONSTANTS.FREEXP_INFO}

    def __init__(self, lootBoxType, awards, count, openedCount, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WtEventPortalAwards(), model=WtEventPortalAwardsModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventPortalAwards, self).__init__(settings, awards)
        self.__lootBoxType = lootBoxType
        self.__count = count
        self.__openedCount = openedCount
        self.__allOpenedBoxesCount = openedCount
        self.__rerollCost = 0
        self.__wasLootAutoClaimed = False

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return WtGuaranteedRewardTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtGuaranteedRewardTooltipView() else super(WtEventPortalAwards, self).createToolTipContent(event, contentID)

    def _onLoaded(self, *args, **kwargs):
        super(WtEventPortalAwards, self)._onLoaded(*args, **kwargs)
        WTEventAwardsScreenVideoSound.playVideoSound(self.__lootBoxType)
        Waiting.hide('updating')

    def _finalize(self):
        wt_event_sound.playLootBoxAwardsExit()
        super(WtEventPortalAwards, self)._finalize()

    def _updateModel(self):
        super(WtEventPortalAwards, self)._updateModel()
        with self.viewModel.transaction() as model:
            _clearRewardsModels(model)
            self._tooltipItems.clear()
            isBossLootBox = self.__isBossLootBox()
            model.setIsBossLootBox(isBossLootBox)
            model.setOpenedBoxesCount(self.__allOpenedBoxesCount)
            model.setIsLaunchAnimated(AccountSettings.getSettings(IS_LAUNCH_ANIMATED))
            setLootBoxesCount(model.portalAvailability, self.__lootBoxType)
            if isBossLootBox:
                self.__setBossModelParameters(model, EventLootBoxes.WT_BOSS)
            else:
                _fillMainAwards(EventLootBoxes.WT_HUNTER, model.rewards, self._awards, self._tooltipItems)
            self.__setRerollParameters(model, isBossLootBox)
            self.__setCurrentBalanceParameters(model)
            wt_event_sound.playLootBoxAwardsReceived(self.__count)

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
        setGuaranteedAward(model.guaranteedAward)

    def __setRerollParameters(self, model, isBossLootBox):
        boxType = EventLootBoxes.WT_BOSS if isBossLootBox else EventLootBoxes.WT_HUNTER
        reRollPrice = self._boxesCtrl.getReRollPrice(boxType)
        if reRollPrice is not None:
            priceType = self._boxesCtrl.getReRollPriceType(boxType)
            self.__rerollCost = reRollPrice.get(priceType)
            model.setRerollCount(self._boxesCtrl.getReRollAttemptsLeft(boxType))
            model.setIsRerollAffordable(self._boxesCtrl.hasAccountEnoughMoneyForReRoll(boxType))
            tooltipType = currencyTooltipTypes.GOLD if isBossLootBox else currencyTooltipTypes.CREDITS
            model.setCurrencyTooltipType(tooltipType)
            model.setRerollPrice(self.__rerollCost)
        else:
            model.setIsRerollAffordable(False)
            model.setRerollCount(0)
            self.__rerollCost = 0
        return

    def __setCurrentBalanceParameters(self, model):
        for tooltipId in self.__SPECIAL_TOOLTIPS.values():
            self._tooltipItems[tooltipId] = createTooltipData(isSpecial=True, specialAlias=tooltipId)

        model.setCurrentCredits(int(self.__itemsCache.items.stats.money.getSignValue(Currency.CREDITS)))
        model.setCurrentGold(int(self.__itemsCache.items.stats.money.getSignValue(Currency.GOLD)))
        model.setCurrentCrystals(int(self.__itemsCache.items.stats.money.getSignValue(Currency.CRYSTAL)))
        model.setCurrentFreeExperience(self.__itemsCache.items.stats.freeXP)
        model.setIsWalletAvailable(self.__itemsCache.items.stats.mayConsumeWalletResources)

    @server_settings.serverSettingsChangeListener(Configs.LOOTBOX_CONFIG.value)
    def __onServerSettingChanged(self, _):
        self._updateModel()

    def _addListeners(self):
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        self.viewModel.onAnimationEnded += self.__animationEnded
        self.viewModel.onReRoll += self.__reRollLoot
        self.viewModel.onAnimationSettingChange += self.__switchAnimationSetting
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.__onGoldChange)
        super(WtEventPortalAwards, self)._addListeners()

    def _removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync
        self.viewModel.onAnimationEnded -= self.__animationEnded
        self.viewModel.onReRoll -= self.__reRollLoot
        self.viewModel.onAnimationSettingChange -= self.__switchAnimationSetting
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_clientUpdateManager.removeCurrencyCallback(Currency.GOLD, self.__onGoldChange)
        super(WtEventPortalAwards, self)._removeListeners()

    @wg_async
    def _onClose(self):
        isBoxesEnabled = self._lobbyContext.getServerSettings().isLootBoxesEnabled()
        if isBoxesEnabled:
            wasCanceledByDialog = yield wg_await(self.__isCanceledByDialog())
            if wasCanceledByDialog:
                return
            if not self.__wasLootAutoClaimed:
                self._boxesCtrl.claimReRolledReward(self.__lootBoxType, 1, parentWindow=self.getParentWindow())
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL), scope=EVENT_BUS_SCOPE.LOBBY)
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

    @wg_async
    def _goToPortals(self):
        wasCanceledByDialog = yield wg_await(self.__isCanceledByDialog())
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

    @wg_async
    def __reRollLoot(self):
        if not self._boxesCtrl.hasAccountEnoughMoneyForReRoll(self.__lootBoxType):
            shop.showBuyGoldForReroll(self.__rerollCost)
            return
        from gui.shared.money import Money
        dialogTitle = R.strings.dialogs.rerollReward.title()
        dialogContentDescription = R.strings.dialogs.rerollReward.message()
        dialogTemplateView = DialogTemplateView()
        dialogTemplateView.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(dialogTitle))
        if self.__isBossLootBox():
            price = Money(gold=self.__rerollCost)
        else:
            price = Money(credits=self.__rerollCost)
        cost = ItemPrice(price=price, defPrice=price)
        dialogTemplateView.setSubView(DefaultDialogPlaceHolders.CONTENT, SinglePriceContent(dialogContentDescription, cost))
        dialogTemplateView.addButton(ConfirmButton(R.strings.dialogs.rerollReward.confirm()))
        dialogTemplateView.addButton(CancelButton(R.strings.dialogs.rerollReward.cancel()))
        dialog = FullScreenDialogWindowWrapper(dialogTemplateView)
        dialog.load()
        result = yield wg_await(dialog.wait())
        dialog.destroy()
        if result.result == DialogButtons.SUBMIT:
            self.__openMore(ReRollButton.REROLL)

    def _claimReward(self):
        with self.viewModel.transaction() as model:
            portalAvailability = model.portalAvailability
            lootboxesCount = portalAvailability.getLootBoxesCount()
            callback = self.__openNextLootbox if lootboxesCount > 0 else self.__goToPortal
            Waiting.show('updating')
            if self.__wasLootAutoClaimed:
                callback()
            else:
                self._boxesCtrl.claimReRolledReward(self.__lootBoxType, 1, parentWindow=self.getParentWindow(), callbackUpdate=callback, callbackFailure=self.__onRequestFailure)

    def __onGoldChange(self, _):
        self._updateModel()

    def __openNextLootbox(self):
        self.__openMore(ReRollButton.CLAIM_AND_RELAUNCH)

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

    def __updateLimits(self):
        with self.viewModel.transaction() as model:
            setGuaranteedAward(model.guaranteedAward)

    def __animationEnded(self, args):
        isAnimationEnded = args.get('isAnimationEnd')
        if isAnimationEnded:
            event_dispatcher.showVehicleAwardWindow(parent=self.getParentWindow())

    def __switchAnimationSetting(self):
        newState = not self.viewModel.getIsLaunchAnimated()
        AccountSettings.setSettings(IS_LAUNCH_ANIMATED, newState)
        self.viewModel.setIsLaunchAnimated(newState)

    def __openMore(self, reRollButtonUsed):
        parent = self.getParentWindow()
        self._boxesCtrl.requestLootBoxReRoll(self.__lootBoxType, parentWindow=parent, callback=self.__updateData, reRollButtonUsed=reRollButtonUsed, callbackFailure=self.__handleRerollFailure)

    def __updateData(self, data):
        Waiting.hide('updating')
        if data:
            WTEventAwardsScreenVideoSound.playVideoSound(self.__lootBoxType)
            self._awards = data.get('awards', [])
            self.__openedCount = data.get('openedBoxes', 0)
            self.__allOpenedBoxesCount += self.__openedCount
            self._updateModel()

    def __handleRerollFailure(self):
        Waiting.hide('updating')
        self.destroyWindow()

    def __isBossLootBox(self):
        return self.__lootBoxType == EventLootBoxes.WT_BOSS

    @wg_async
    def __isCanceledByDialog(self):
        if not self.__wasLootAutoClaimed:
            builder = ResDialogBuilder()
            builder.setMessagesAndButtons(R.strings.dialogs.confirmReward)
            result = yield wg_await(dialogs.show(builder.build()))
            if result.result != DialogButtons.SUBMIT:
                raise AsyncReturn(True)
        raise AsyncReturn(False)


class WtEventPortalAwardsWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, lootBoxType, awards, count, openedCount, parent=None):
        super(WtEventPortalAwardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtEventPortalAwards(lootBoxType=lootBoxType, awards=awards, count=count, openedCount=openedCount), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)


def _backToAwardView(lootBoxType, awards):
    Waiting.show('updating')
    event_dispatcher.showHangar()
    event_dispatcher.showEventPortalAwardsWindow(lootBoxType, awards)
    Waiting.hide('updating')


def _fillBossAwards(model, bonuses, tooltipItems):
    groupedBonuses = LootBoxAwardsManager.getBossGroupedBonuses(bonuses)
    _fillMainAwards(EventLootBoxes.WT_BOSS, model.rewards, groupedBonuses.main, tooltipItems)
    fillAdditionalAwards(model.additionalRewards, groupedBonuses.additional, tooltipItems)
    fillVehicleAward(model, groupedBonuses.vehicle)


def _fillMainAwards(lootBoxType, model, bonuses, tooltipItems):
    model.clearItems()
    order = BOSS_ALL_BONUSES_ORDER if lootBoxType == EventLootBoxes.WT_BOSS else HUNTER_BONUSES_ORDER
    packBonusModelAndTooltipData(sorted(bonuses, key=lambda bonus: sortBonuses(bonus, order)), model, tooltipItems, getWtEventBonusPacker())


def _clearRewardsModels(model):
    model.rewards.clearItems()
    model.additionalRewards.clearItems()
