# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/shop_view.py
import WWISE
from async import await, async
from constants import EVENT
from adisp import process
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.dialogs.dialogs import showBuyPackConfirmDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.halloween.event_keys_counter_panel_view_model import VisualTypeEnum
from gui.impl.gen.view_models.views.lobby.halloween.shop_bonus_group_model import ShopBonusGroupModel, BonusGroupTypeEnum
from gui.impl.gen.view_models.views.lobby.halloween.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.halloween.shop_bundle_model import ShopBundleModel
from gui.impl.gen.view_models.views.lobby.halloween.shop_view_model import ShopViewModel, PageTypeEnum
from gui.impl.lobby.halloween.event_keys_counter_panel_view import EventKeysCounterPanelView
from gui.impl.lobby.halloween.hangar_event_view import HangarEventView
from gui.server_events.awards_formatters import AWARDS_SIZES, getEventShopBundlesAwardFormatter
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import EventShopBundleBonusesAwardsComposer
from gui.shared.event_dispatcher import showHangar
from gui.shared.money import Currency
from gui.shared.utils.functions import getAbsoluteUrl
from gui.shop import showBuyGoldForBundle
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.ServerSettingsManager import UIGameEventKeys
from ids_generators import SequenceIDGenerator
from shared_utils import CONST_CONTAINER
from gui.impl.lobby.halloween.sound_constants import EventHangarSound
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class BonusGroups(CONST_CONTAINER):
    VEHICLES = 'vehicles'
    PREMIUM = 'premium_plus'
    TOKENS = 'battleToken'
    SLOTS = 'slots'
    OTHER = 'other'
    CUSTOMIZATIONS = 'customizations'


GROUP_NAME_TO_GROUP_TYPE_MAP = {BonusGroups.VEHICLES: BonusGroupTypeEnum.VEHICLES,
 BonusGroups.CUSTOMIZATIONS: BonusGroupTypeEnum.CUSTOMIZATIONS,
 BonusGroups.PREMIUM: BonusGroupTypeEnum.PREMIUM,
 BonusGroups.TOKENS: BonusGroupTypeEnum.KEYS,
 BonusGroups.OTHER: BonusGroupTypeEnum.BONUS_ITEMS}

class ShopView(HangarEventView):
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsCache = dependency.descriptor(IItemsCache)
    gameEventController = dependency.descriptor(IGameEventController)
    PAGE_TYPE = PageTypeEnum.KEYS
    SHOP_TYPE_NAME = EVENT.SHOP.TYPE.KEYS
    BONUS_GROUPS = (BonusGroups.PREMIUM, BonusGroups.CUSTOMIZATIONS, BonusGroups.TOKENS)
    BONUS_GROUPS_ORDER = (BonusGroups.PREMIUM,
     BonusGroups.CUSTOMIZATIONS,
     BonusGroups.OTHER,
     BonusGroups.TOKENS)
    MAX_BONUSES_PER_BUNDLE = 4

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ShopViewModel()
        super(ShopView, self).__init__(settings)
        self._shop = self.gameEventController.getShop()
        self.__keysCounterPanel = EventKeysCounterPanelView(VisualTypeEnum.SHOP)
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}
        self.__isClosing = False

    @property
    def viewModel(self):
        return super(ShopView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs), self.getParentWindow())
                window.load()
                return window
        super(ShopView, self).createToolTip(event)

    def close(self):
        self.__onClose()

    def _finalize(self):
        self.__bonusCache.clear()
        self._shop.onShopBundlesChanged -= self.__onShopBundlesChanged
        self._shop.onGoldChanged -= self.__onGoldChanged
        self._shop.onBundleUnlocked -= self.__onBundleUnlocked
        self.viewModel.onBuyClick -= self.__onBuyClick
        self.viewModel.onClose -= self.__onClose
        super(ShopView, self)._finalize()

    def _onLoading(self):
        super(ShopView, self)._onLoading()
        WWISE.WW_eventGlobal(EventHangarSound.KEY_COUNTER_ENTER)
        self.viewModel.onBuyClick += self.__onBuyClick
        self.viewModel.onClose += self.__onClose
        self._shop.onBundleUnlocked += self.__onBundleUnlocked
        self._shop.onGoldChanged += self.__onGoldChanged
        self._shop.onShopBundlesChanged += self.__onShopBundlesChanged
        self.__fillModel()
        self.setChildView(self.__keysCounterPanel.layoutID, self.__keysCounterPanel)

    def _getBundlesAndBonuses(self):
        shopBundles = self._shop.getBundlesByShopType(self.SHOP_TYPE_NAME)
        bonuses = [ self._shop.getShopBundleBonusesWithQuests(bundle) for bundle in shopBundles ]
        return zip(shopBundles, bonuses)

    def _fillBonusesGroup(self, model, groupName, bonuses):
        self.__fillBonuses(model, bonuses)

    def __fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setPageType(self.PAGE_TYPE)
            bundles = vm.getBundles()
            bundles.clear()
            for bundle, bonuses in self._getBundlesAndBonuses():
                bundleModel = ShopBundleModel()
                bundleModel.setId(bundle.id)
                if bundle.purchasesLimit is not None:
                    bundleModel.setAmount(bundle.purchasesLimit - self._shop.getBundlePurchasesCount(bundle.id))
                bundleModel.setCountdownValue(bundle.secondsToUnlock or 0)
                if bundle.secondsToUnlock == 0:
                    self.__showUnlockedBundleAnimation(bundleModel)
                self.__fillPrice(bundleModel.price, bundle.price, bundle.oldPrice)
                self.__fillBonusGroups(bundleModel.getBonusGroups(), bonuses)
                bundles.addViewModel(bundleModel)

            bundles.invalidate()
        return

    def __fillBonusGroups(self, bonusGroupsModel, bonuses):
        bonusGroupsModel.clear()
        bonusesGroups = self.__groupBonuses(bonuses, self.BONUS_GROUPS)
        for groupName in self.BONUS_GROUPS_ORDER:
            if groupName not in bonusesGroups:
                continue
            bonusGroupModel = ShopBonusGroupModel()
            bonusGroupModel.setType(GROUP_NAME_TO_GROUP_TYPE_MAP[groupName])
            bonuses = bonusesGroups[groupName]
            self._fillBonusesGroup(bonusGroupModel.getBonusItems(), groupName, bonuses)
            bonusGroupsModel.addViewModel(bonusGroupModel)

        bonusGroupsModel.invalidate()

    def __fillBonuses(self, model, bonuses):
        formatter = EventShopBundleBonusesAwardsComposer(self.MAX_BONUSES_PER_BUNDLE, getEventShopBundlesAwardFormatter())
        formattedBonuses = formatter.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)
        model.clear()
        for bonus in formattedBonuses:
            bonusModel = BonusModel()
            bonusModel.setLabel(bonus.label or 'x1')
            self.__setImageAndTooltip(bonusModel, bonus)
            model.addViewModel(bonusModel)

        model.invalidate()

    def __fillPrice(self, priceModel, price, oldPrice):
        priceModel.setValue(price.amount)
        priceModel.setIsEnough(self.__getGold() >= price.amount)
        if oldPrice is not None:
            priceModel.setOldValue(oldPrice.amount)
            priceModel.setDiscountValue(self.__calcDiscount(price.amount, oldPrice.amount))
        return

    def __setImageAndTooltip(self, model, bonus):
        tooltipId = '{}'.format(self.__idGen.next())
        self.__bonusCache[tooltipId] = bonus
        model.setIcon(getAbsoluteUrl(bonus.getImage(AWARDS_SIZES.BIG)))
        model.setTooltipId(tooltipId)

    @async
    def __onBuyClick(self, args=None):
        if self.__isClosing:
            return
        if 'id' not in args:
            return
        bundle = self._shop.getBundle(args['id'])
        if bundle.price.amount > self.__getGold():
            showBuyGoldForBundle(bundle.price.amount, {})
            return
        isOk, _ = yield await(showBuyPackConfirmDialog(bundle))
        if isOk:
            self.__processPurchase(bundle)

    @process
    def __processPurchase(self, bundle):
        success = yield self._shop.purchaseShopBundle(bundle.id)
        if not success:
            return
        if self.__isClosing:
            return
        bundles = self.viewModel.getBundles()
        bundleID = bundle.id
        for bundleModel in bundles:
            if bundleModel.getId() == bundleID:
                newAmount = bundleModel.getAmount() - 1
                bundleModel.setAmount(newAmount)
                if newAmount == 0:
                    bundleModel.setShowAnimation(False)

    def __onClose(self):
        self.__isClosing = True
        WWISE.WW_eventGlobal(EventHangarSound.KEY_COUNTER_EXIT)
        showHangar()

    def __getGold(self):
        return self.itemsCache.items.stats.money.get(Currency.GOLD, 0)

    def __showUnlockedBundleAnimation(self, bundleModel):
        bundleID = bundleModel.getId().upper()
        if not hasattr(UIGameEventKeys, bundleID):
            return
        bundleStorageKey = UIGameEventKeys[bundleID]
        if self.settingsCore.serverSettings.getGameEventStorage().get(bundleStorageKey):
            return
        self.settingsCore.serverSettings.saveInGameEventStorage({bundleStorageKey: 1})
        bundleModel.setShowAnimation(True)

    def __onBundleUnlocked(self, bundle):
        with self.viewModel.transaction() as vm:
            for bundleModel in vm.getBundles():
                if bundleModel.getId() == bundle.id:
                    bundleModel.setCountdownValue(0)
                    self.__showUnlockedBundleAnimation(bundleModel)

    def __onGoldChanged(self, value):
        bundles = self.viewModel.getBundles()
        for bundleModel in bundles:
            if bundleModel.getId():
                bundleModel.price.setIsEnough(value >= bundleModel.price.getValue())

    def __onShopBundlesChanged(self):
        self.__bonusCache.clear()
        self.__fillModel()

    @staticmethod
    def __groupBonuses(bonuses, groups):
        result = {}
        for bonus in bonuses:
            bonusName = bonus.getName()
            if bonusName in groups:
                result.setdefault(bonusName, []).append(bonus)
            result.setdefault(BonusGroups.OTHER, []).append(bonus)

        return result

    @staticmethod
    def __calcDiscount(currentPrice, oldPrice):
        return int(float(oldPrice - currentPrice) / float(oldPrice) * 100.0)
