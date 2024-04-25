# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/shop_view.py
import logging
import time
from collections import namedtuple
import BigWorld
import nations
from adisp import adisp_process
from wg_async import wg_await
from gui import GUI_NATIONS_ORDER_INDICES
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.server_events.awards_formatters import AwardsPacker, getDefaultFormattersMap, ItemsBonusFormatter, GoodiesBonusFormatter, CrewBooksBonusFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions.factory import asyncDoAction
from gui.shared.money import Currency, Money
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE
from gui.impl.pub.lobby_window import LobbyWindow
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from historical_battles.gui.impl.gen.view_models.views.common.simple_price_view_model import SimplePriceViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_item_view_model import BundleItemViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.money_item_view_model import MoneyItemViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.shop_item_view_model import ShopItemViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.shop_view_model import ShopViewModel, ShopTabs
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.gui.impl.lobby.shop_views.shop_buy_dialog_view import ShopBuyDialogView
from historical_battles.gui.impl.lobby.shop_views.utils import hasEnoughMoney, getSortedPriceList
from historical_battles.gui.impl.lobby.tooltips.general_hb_coin_tooltip import GeneralHbCoinTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_coin_exchange_tooltip import HbCoinExchangeTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.impl.lobby.widgets.coin_widget import CoinWidget
from historical_battles.gui.shared.event_dispatcher import showHBHangar
from historical_battles.gui.shared.gui_items.items_actions.hb_shop import HBShopBuyBundleAction
from historical_battles.gui.sounds.sound_constants import SHOP_SOUND_SPACE
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.helpers_common import EventShopBundlePrice, Discount
from historical_battles_common.helpers_common import getVehicleBonus
_logger = logging.getLogger(__name__)
ShopBonusItemInfo = namedtuple('ShopBonusItemInfo', ('bonusItem',
 'iconName',
 'nationName',
 'inventoryCount',
 'description',
 'dialogDescription'))
ShopBonusItemInfo.__new__.__defaults__ = (None,
 None,
 '',
 None,
 '',
 '')
COLOR_TAG_OPEN = '{green_Open}'
COLOR_TAG_CLOSE = '{green_Close}'
GOODIES_ORDER = [GOODIE_RESOURCE_TYPE.XP,
 GOODIE_RESOURCE_TYPE.FL_XP,
 GOODIE_RESOURCE_TYPE.CREW_XP,
 GOODIE_RESOURCE_TYPE.FREE_XP,
 GOODIE_RESOURCE_TYPE.GOLD,
 GOODIE_RESOURCE_TYPE.CREDITS]
BATTLE_BOOSTERS_ORDER = ['equipmentBattleBooster', 'crewSkillBattleBooster']

def formatValueToColorTag(value):
    return COLOR_TAG_OPEN + value + COLOR_TAG_CLOSE


def getBonusItem(preformattedBonus):
    return preformattedBonus.images.bonusItem


def tabDefaultComparator(a, b):
    return cmp(a.userName, b.userName)


def crewBookTabComparator(preformattedBonusA, preformattedBonusB):
    a = getBonusItem(preformattedBonusA)
    b = getBonusItem(preformattedBonusB)

    def nationComparator(item1, item2):
        isNoNation = lambda item: item.getNationID() == nations.NONE_INDEX
        return 0 if isNoNation(item1) and isNoNation(item2) else -cmp(isNoNation(item1), isNoNation(item2)) or cmp(GUI_NATIONS_ORDER_INDICES[item1.getNationID()], GUI_NATIONS_ORDER_INDICES[item2.getNationID()])

    def orderComparator(item1, item2):
        return cmp(item1.getBookTypeOrder(), item2.getBookTypeOrder())

    return nationComparator(a, b) or orderComparator(a, b) or tabDefaultComparator(a, b)


def equipmentsTabComparator(preformattedBonusA, preformattedBonusB):
    a = getBonusItem(preformattedBonusA)
    b = getBonusItem(preformattedBonusB)

    def getNation(item):
        compatibleNations = item.descriptor.compatibleNations()
        return nations.ALL_NATIONS_INDEX if not compatibleNations or len(compatibleNations) == len(nations.INDICES) else GUI_NATIONS_ORDER_INDICES[min(compatibleNations)]

    def nationComparator(item1, item2):
        nations1 = item1.descriptor.compatibleNations()
        nations2 = item2.descriptor.compatibleNations()
        nationsLen = lambda n: len(n) or len(nations.INDICES)
        return -cmp(nationsLen(nations1), nationsLen(nations2)) or cmp(getNation(item1), getNation(item2))

    return nationComparator(a, b) or tabDefaultComparator(a, b)


def reservesTabComparator(preformattedBonusA, preformattedBonusB):
    a = getBonusItem(preformattedBonusA)
    b = getBonusItem(preformattedBonusB)
    typeCmp = cmp(GOODIES_ORDER.index(a.boosterType), GOODIES_ORDER.index(b.boosterType))
    return typeCmp or -cmp(a.effectValue, b.effectValue) or cmp(b.effectTime, a.effectTime) or tabDefaultComparator(a, b)


def instructionTabComparator(preformattedBonusA, preformattedBonusB):
    a = getBonusItem(preformattedBonusA)
    b = getBonusItem(preformattedBonusB)

    def battleBossterOrder(item):
        for i, tag in enumerate(BATTLE_BOOSTERS_ORDER):
            if tag in item.descriptor.tags:
                return i

    return cmp(battleBossterOrder(a), battleBossterOrder(b)) or tabDefaultComparator(a, b)


def getNationName(nationIndex):
    if nationIndex is None:
        return ''
    else:
        return nations.NAMES[nationIndex] if nationIndex != nations.NONE_INDEX else ''


class HBShopGoodiesBonusFormatter(GoodiesBonusFormatter):

    def _formatBonusLabel(self, count):
        return count

    @classmethod
    def _getUserName(cls, item):
        return backport.text(R.strings.hb_shop.booster.bonus.dyn(item.boosterGuiType)(), effectValue=item.getFormattedValue(), effectTime=backport.text(R.strings.hb_shop.common.timeLeft.hours(), hour=str(time.gmtime(item.effectTime).tm_hour)))

    @classmethod
    def _getImages(cls, item):
        return ShopBonusItemInfo(bonusItem=item, iconName=item.boosterGuiType, inventoryCount=item.count, description=item.fullUserName, dialogDescription=item.userName)


class HBShopCrewBooksBonusFormatter(CrewBooksBonusFormatter):

    @classmethod
    def _getImages(cls, item):
        return ShopBonusItemInfo(bonusItem=item, iconName=item.icon, nationName=getNationName(item.nationID), inventoryCount=item.inventoryCount, description=item.shortDescription)


class HBShopItemsBonusFormatter(ItemsBonusFormatter):

    def _formatBonusLabel(self, count):
        return count

    @classmethod
    def _getOverlayType(cls, item):
        return '{}_{}'.format(item.getOverlayType(), 'overlay')

    @classmethod
    def _getImages(cls, item):
        return ShopBonusItemInfo(bonusItem=item, iconName=item.getGUIEmblemID(), nationName=cls._getNationName(item), inventoryCount=item.inventoryCount, description=cls._getItemDescription(item))

    @staticmethod
    def _getItemDescription(item):
        if item.itemTypeName == FITTING_TYPES.BOOSTER:
            if item.isCrewBooster():
                description = item.getCrewBoosterDescription(True, {'colorTagOpen': COLOR_TAG_OPEN,
                 'colorTagClose': COLOR_TAG_CLOSE})
            else:
                description = item.getOptDeviceBoosterDescription(None, formatValueToColorTag)
            return description
        else:
            return item.shortDescriptionSpecial

    @staticmethod
    def _getNationName(item):
        compatibleNations = item.descriptor.compatibleNations()
        nation = compatibleNations[0] if len(compatibleNations) == 1 else nations.NONE_INDEX
        return getNationName(nation)


def getHBShopFormatterMap():
    formattersMap = getDefaultFormattersMap()
    formattersMap.update({'goodies': HBShopGoodiesBonusFormatter(),
     'items': HBShopItemsBonusFormatter(),
     'crewBooks': HBShopCrewBooksBonusFormatter()})
    return formattersMap


def getHBShopAwardFormatter():
    return AwardsPacker(getHBShopFormatterMap())


class ShopView(BaseEventView):
    OPTIONAL_DEVICES_GROUP_NAME = 'hb22OptionalDevices'
    SHOWCASE_BUNDLES_GROUP_NAME = 'hb22Showcase'
    MAIN_PRIZE_VEHICLE_BUNDLE_ID = 'hb22BundleMainPrizeVehicle'
    _COMMON_SOUND_SPACE = SHOP_SOUND_SPACE
    TAB_TO_SHOP_CATEGORY = {ShopTabs.CREWBOOK: 'hb22CrewBookBundle',
     ShopTabs.EQUIPMENT: 'hb22Consumable',
     ShopTabs.INSTRUCTION: 'hb22BattleBoosters',
     ShopTabs.RESERVES: 'hb22PersonalReserveBundle'}
    TAB_TO_ICON_RES = {ShopTabs.CREWBOOK: R.images.gui.maps.icons.crewBooks.books.s180x135,
     ShopTabs.EQUIPMENT: R.images.gui.maps.shop.artefacts.c_180x135,
     ShopTabs.INSTRUCTION: R.images.gui.maps.shop.artefacts.c_180x135,
     ShopTabs.RESERVES: R.images.gui.maps.shop.boosters.c_180x135}
    TAB_TO_BACKLIGHT = {ShopTabs.CREWBOOK: R.images.historical_battles.gui.maps.icons.common.upgrade_bg_regular,
     ShopTabs.EQUIPMENT: R.images.historical_battles.gui.maps.icons.common.upgrade_bg_regular,
     ShopTabs.INSTRUCTION: R.images.historical_battles.gui.maps.icons.common.upgrade_bg_instruction,
     ShopTabs.RESERVES: R.images.historical_battles.gui.maps.icons.common.upgrade_bg_regular}
    TAB_BONUSES_COMPARATOR = {ShopTabs.CREWBOOK: crewBookTabComparator,
     ShopTabs.EQUIPMENT: equipmentsTabComparator,
     ShopTabs.RESERVES: reservesTabComparator,
     ShopTabs.INSTRUCTION: instructionTabComparator}
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, activeTab=ShopTabs.BEST):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ShopViewModel()
        self.__activeTab = activeTab
        self.__confirmationDialogDataCache = {}
        super(ShopView, self).__init__(settings)

    @property
    def shop(self):
        return getattr(BigWorld.player(), 'HBShopAccountComponent', None)

    @property
    def viewModel(self):
        return super(ShopView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.GeneralHbCoinTooltip():
            return GeneralHbCoinTooltip()
        elif contentID == R.views.historical_battles.lobby.tooltips.HbCoinExchangeTooltip():
            return HbCoinExchangeTooltip()
        elif contentID == R.views.historical_battles.lobby.tooltips.HbCoinTooltip():
            coinType = event.getArgument('coinType')
            itemPrice = event.getArgument('itemPrice')
            if coinType is None:
                _logger.error('HbCoinTooltip must receive a viable coinType param. Received: None')
                return
            return HbCoinTooltip(coinType, itemPrice)
        else:
            if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
                tooltipID = event.getArgument('tooltipID')
                if tooltipID == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
                    return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (int(event.getArgument('value')), event.getArgument('currency')))
                if tooltipID == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                    bundle = self.shop.getBundle(self.MAIN_PRIZE_VEHICLE_BUNDLE_ID)
                    newPrice = self.shop.getBundleDiscountedPrice(bundle)
                    oldPrice = bundle.price
                    if newPrice is None:
                        return
                    return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.ACTION_PRICE, specialArgs=(None,
                     None,
                     self.__convertMoneyToTuple(Money(**{newPrice.currency: newPrice.amount})),
                     self.__convertMoneyToTuple(Money(**{oldPrice.currency: oldPrice.amount})),
                     True,
                     False,
                     None,
                     True))
            return super(ShopView, self).createToolTipContent(event, contentID)

    def _onLoading(self):
        super(ShopView, self)._onLoading()
        coins = self._gameEventController.coins
        fronts = self._gameEventController.frontController.getFronts()
        self.__tokensToCoinsMap = {coins.getTokenName(f.getCoinsName()):f.getCoinsName() for f in fronts.itervalues()}
        self.viewModel.onClose += self.__onClose
        self.viewModel.onTabChange += self.__onTabChange
        self.viewModel.onBack += self.__onBack
        self.viewModel.items.onItemClicked += self.__onItemClicked
        self.viewModel.showcase.onClick += self.__onShowcaseClick
        self.shop.onBundlePurchased += self.__onBundlePurchased
        self.shop.onShopUpdated += self.__onShopUpdated
        coins.onCoinsCountChanged += self.__onMoneyChange
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyChange)
        g_clientUpdateManager.addCallbacks({'inventory': self._onInventoryUpdate})
        self.__coinWidget = CoinWidget(self.viewModel.coinWidget)
        self.__coinWidget.onLoading()
        self.__fillViewModel()

    def _finalize(self):
        self.__confirmationDialogDataCache.clear()
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onTabChange -= self.__onTabChange
        self.viewModel.onBack -= self.__onBack
        self.viewModel.showcase.onClick -= self.__onShowcaseClick
        self.viewModel.items.onItemClicked -= self.__onItemClicked
        if self._gameEventController.coins:
            self._gameEventController.coins.onCoinsCountChanged -= self.__onMoneyChange
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.shop is not None:
            self.shop.onBundlePurchased -= self.__onBundlePurchased
            self.shop.onShopUpdated -= self.__onShopUpdated
        self.__coinWidget.destroy()
        super(ShopView, self)._finalize()
        return

    def _onInventoryUpdate(self, invDiff):
        vehsDiff = invDiff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if 'compDescr' in vehsDiff and self.__getPrizeVehicle().isInInventory:
            self.__fillViewModel()

    def __fillViewModel(self):
        self.__confirmationDialogDataCache.clear()
        with self.viewModel.transaction() as tx:
            self.__fillWallet(tx)
            tx.setSelectedTab(self.__activeTab)
            self.__coinWidget.updateModel(tx.coinWidget)
            if self.__activeTab == ShopTabs.BEST:
                self.__fillShowcaseBundles(tx)
                return
            shopCategory = self.TAB_TO_SHOP_CATEGORY.get(self.__activeTab)
            if shopCategory:
                self.__fillItems(tx, shopCategory)

    def __fillWallet(self, tx):
        moneyLst = tx.wallet.getMoney()
        moneyLst.clear()
        stats = self._itemsCache.items.stats
        credit = MoneyItemViewModel()
        credit.setType(Currency.CREDITS)
        credit.setCount(int(stats.money.getSignValue(Currency.CREDITS)))
        crystal = MoneyItemViewModel()
        crystal.setType(Currency.CRYSTAL)
        crystal.setCount(int(stats.money.getSignValue(Currency.CRYSTAL)))
        gold = MoneyItemViewModel()
        gold.setType(Currency.GOLD)
        gold.setCount(int(stats.money.getSignValue(Currency.GOLD)))
        moneyLst.addViewModel(credit)
        moneyLst.addViewModel(crystal)
        moneyLst.addViewModel(gold)
        for front in self._gameEventController.frontController.getFronts().itervalues():
            coinName = front.getCoinsName()
            money = MoneyItemViewModel()
            money.setType(coinName)
            money.setCount(self._gameEventController.coins.getCount(coinName))
            moneyLst.addViewModel(money)

        moneyLst.invalidate()

    def __onTabChange(self, args):
        tab = args.get('tabKey', None)
        if tab is None:
            return
        else:
            self.__activeTab = ShopTabs(tab)
            self.__fillViewModel()
            return

    def __onClose(self):
        showHBHangar()
        self.destroyWindow()

    def __onBack(self):
        showHBHangar()
        self.destroyWindow()

    def __onShowcaseClick(self, args):
        if args is None:
            _logger.error('args is none. Try fixing JS')
            return
        else:
            itemID = args.get('type', None)
            bundle = self.shop.getBundle(itemID)
            if hasEnoughMoney(bundle.prices):
                self.__purchaseBundle(bundle)
            else:
                account = BigWorld.player()
                _logger.error('There is not enough money on account %s to purchase bundle %s', account.id, bundle.id)
            return

    @adisp_process
    def __purchaseBundle(self, bundle):
        confirmationData = self.__confirmationDialogDataCache[bundle.id]
        yield wg_await(asyncDoAction(HBShopBuyBundleAction(bundle, ShopBuyDialogView, confirmationData)))

    def __onItemClicked(self, args=None):
        if args is None:
            _logger.error('args is none. Try fixing JS')
            return
        else:
            itemID = args.get('id', None)
            bundle = self.shop.getBundle(itemID)
            if hasEnoughMoney(bundle.prices):
                self.__purchaseBundle(bundle)
            else:
                account = BigWorld.player()
                _logger.error('There is not enough money on account %s to purchase bundle %s', account.id, bundle.id)
            return

    def __onBundlePurchased(self, _):
        self.__fillViewModel()

    def __onShopUpdated(self):
        self.__fillViewModel()

    def __getPrizeVehicle(self, prizeVeh=None):
        mainPrizeBundle = prizeVeh
        if prizeVeh is None:
            mainPrizeBundle = self.shop.getBundle(self.MAIN_PRIZE_VEHICLE_BUNDLE_ID)
        bundleBonuses = self.shop.getBundleBonusesWithQuests(mainPrizeBundle)
        vehicle = getVehicleBonus(bundleBonuses)
        if vehicle is None:
            _logger.error('There is no vehicle in bundleBonus bundleID = %s', mainPrizeBundle.id)
        return vehicle

    def __fillShowcaseBundles(self, model):
        showcase = model.showcase
        mainPrizeBundle = self.shop.getBundle(self.MAIN_PRIZE_VEHICLE_BUNDLE_ID)
        self.__fillMainPrizeVehicle(showcase.vehicleBundle, mainPrizeBundle)
        optDeviceBundle = self.shop.getBundlesByGroup(self.OPTIONAL_DEVICES_GROUP_NAME)[0]
        self.__fillOptDeviceBundle(showcase.extraBundle, optDeviceBundle)
        showcaseBundles = self.shop.getBundlesByGroup(self.SHOWCASE_BUNDLES_GROUP_NAME)
        showcaseBundlesVM = showcase.bundles.getItems()
        showcaseBundlesVM.clear()
        for bundle in showcaseBundles:
            bundleVM = BundleItemViewModel()
            discounts = Discount.getDiscountPercent(bundle.price, bundle.oldPrice)
            self.__fillPrice(bundleVM.price, bundle, discounts)
            if discounts:
                bundleVM.setDiscountValue(max(discounts.itervalues()))
            bundleVM.setType(bundle.id)
            purchasesLeft = self.shop.getBundlePurchasesLeft(bundle)
            if purchasesLeft is not None:
                bundleVM.setBuyCount(purchasesLeft)
                bundleVM.setIsBought(purchasesLeft == 0)
            showcaseBundlesVM.addViewModel(bundleVM)
            self.__confirmationDialogDataCache[bundle.id] = {'icon': R.images.historical_battles.gui.maps.icons.shop.bundles.dyn('{}_260x135'.format(bundle.id))(),
             'titleText': backport.text(R.strings.hb_shop.shop.dyn(bundle.id).confirm_dialog_title()),
             'backgrounds': [R.images.historical_battles.gui.maps.icons.common.upgrade_bg_regular()],
             'bundle': bundle}

        showcaseBundlesVM.invalidate()
        return

    def __fillMainPrizeVehicle(self, bundleVM, bundle):
        vehicleBonus = self.__getPrizeVehicle(bundle)
        bundleVM.vehicle.setId(vehicleBonus.intCD)
        bundleVM.vehicle.setType(vehicleBonus.type)
        bundleVM.vehicle.setIsPremium(vehicleBonus.isPremium)
        bundleVM.vehicle.setName(vehicleBonus.userName)
        bundleVM.vehicle.setLevel(vehicleBonus.level)
        bundleVM.vehicle.setNation(vehicleBonus.nationName)
        bundleVM.vehicle.setIcon(replaceHyphenToUnderscore(vehicleBonus.name.replace(':', '-')))
        discounts = {}
        discountedPrice = self.shop.getBundleDiscountedPrice(bundle)
        if discountedPrice:
            discounts = Discount.getDiscountPercent(discountedPrice, bundle.price)
            bundleVM.setDiscountValue(discounts.get(bundle.price.currency, 0))
        self.__fillPrice(bundleVM.price, bundle, discounts)
        isPurchased = self.shop.getBundlePurchasesLeft(bundle) <= 0
        bundleVM.setIsBought(isPurchased and vehicleBonus.isInInventory)
        bundleVM.setIsSold(isPurchased and not vehicleBonus.isInInventory)

    def __fillOptDeviceBundle(self, bundleVM, bundle):
        purchasesLeft = self.shop.getBundlePurchasesLeft(bundle)
        if purchasesLeft is not None:
            bundleVM.setIsBought(purchasesLeft <= 0)
            bundleVM.setBuyCount(purchasesLeft)
        discounts = Discount.getDiscountPercent(bundle.price, bundle.oldPrice)
        self.__fillPrice(bundleVM.price, bundle, discounts)
        if discounts:
            bundleVM.setDiscountValue(max(discounts.itervalues()))
        return

    def __fillPrice(self, priceVM, bundle, discounts):
        prices = priceVM.getPrices()
        prices.clear()
        discountedPrice = self.shop.getBundleDiscountedPrice(bundle)
        if discountedPrice:
            if isinstance(discountedPrice, EventShopBundlePrice.SinglePrice):
                subPrices = [discountedPrice]
            else:
                subPrices = discountedPrice.price.subPrices
            for subPrice in subPrices:
                prices.addViewModel(self.__makePrice(subPrice, discounts.get(subPrice.currency, None), bundle.price.amount))

        else:
            for subPrice in getSortedPriceList(bundle.prices):
                prices.addViewModel(self.__makePrice(subPrice, discounts.get(subPrice.currency, None), bundle.oldPrice.amount if bundle.oldPrice is not None else 0))

        prices.invalidate()
        return

    def __createSimplePrice(self, currencyType, discount=0, isEnought=True, isDiscount=False, value=0, oldValue=0):
        price = SimplePriceViewModel()
        price.setType(currencyType)
        price.setDiscount(discount)
        price.setIsEnough(isEnought)
        price.setIsDiscount(isDiscount)
        price.setValue(value)
        price.setOldValue(oldValue)
        return price

    def __fillItems(self, tx, shopCategory):
        bundles = tx.items.getItems()
        bundles.clear()
        shopBundles = self.shop.getBundlesByGroup(shopCategory)
        bundlesAndBonuses = [ (getHBShopAwardFormatter().format(bundle.bonuses)[0], bundle) for bundle in shopBundles ]
        comparator = self.TAB_BONUSES_COMPARATOR.get(self.__activeTab, tabDefaultComparator)
        for bonus, bundle in sorted(bundlesAndBonuses, key=lambda t: t[0], cmp=comparator):
            bundleVM = self.__createShopItem(bundle, bonus)
            bundles.addViewModel(bundleVM)

        bundles.invalidate()

    def __createShopItem(self, bundle, bonus):
        shopItem = ShopItemViewModel()
        discounts = Discount.getDiscountPercent(bundle.price, bundle.oldPrice)
        self.__fillPrice(shopItem.price, bundle, discounts)
        bonusItemUserData = bonus.images
        shopItem.setId(bundle.id)
        shopItem.setName(bonus.userName)
        shopItem.setDescription(bonusItemUserData.description)
        shopItem.setNation(bonusItemUserData.nationName)
        shopItem.setIconName(bonusItemUserData.iconName)
        shopItem.setCount(bonusItemUserData.inventoryCount or 0)
        shopItem.setIconOverlay(bonus.overlayType or '')
        iconRes = self.TAB_TO_ICON_RES[self.__activeTab]
        self.__confirmationDialogDataCache[bundle.id] = {'icon': iconRes.dyn(bonusItemUserData.iconName)(),
         'overlays': [iconRes.dyn(bonus.overlayType or '')()],
         'titleText': backport.text(R.strings.hb_shop.showcase_confirm_dialog.dyn(self.__activeTab.value).title(), name=bonus.userName),
         'backgrounds': [self.TAB_TO_BACKLIGHT[self.__activeTab]()],
         'bundle': bundle,
         'pickCount': True}
        return shopItem

    def __onMoneyChange(self, _):
        self.__fillViewModel()

    def __makePrice(self, price, discount, oldPrice):
        return self.__createSimplePrice(self.__tokensToCoinsMap.get(price.currency, price.currency), value=price.amount, discount=discount or 0, isDiscount=discount is not None, oldValue=oldPrice)

    @staticmethod
    def __convertMoneyToTuple(money):
        return (money.credits, money.gold, money.crystal)


class HBShop(LobbyWindow):

    def __init__(self, layoutID):
        super(HBShop, self).__init__(wndFlags=WindowFlags.WINDOW, content=ShopView(layoutID=layoutID))
