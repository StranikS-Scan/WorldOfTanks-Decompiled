# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/order_view.py
import BigWorld
import typing
from enum import Enum
from adisp import adisp_process
from gui.shared.gui_items.items_actions.factory import asyncDoAction
from wg_async import wg_await
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from constants import PREMIUM_ENTITLEMENTS
from gui.impl.gen import R
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.order_view_model import OrderViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.bundle_bonus_model import BundleBonusModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.bundle_model import BundleModel, BundleLayout
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_tooltips_constants import HbTooltipsConstants
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.money import Currency, Money
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from ids_generators import SequenceIDGenerator
from gui.server_events.awards_formatters import AwardsPacker, getDefaultFormattersMap, ItemsBonusFormatter, GoodiesBonusFormatter, PremiumDaysBonusFormatter
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from historical_battles.gui.server_events.hb_awards_formatter import HBQuestsTokenBonusFormatter
from historical_battles_common.helpers_common import Discount
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from gui.impl.pub.tooltip_window import ToolTipWindow
from gui.shop import showBuyGoldForBundle
from historical_battles.gui.impl.dialogs.sub_views.content.order_with_bonuses import Order, Bonus
from historical_battles.gui.impl.lobby.shop_views.booster_buy_dialog_view import BoosterBuyDialogView
from historical_battles.gui.shared.gui_items.items_actions.hb_shop import HBShopBuyBundleAction
from helpers.func_utils import oncePerPeriod
from debug_utils import LOG_ERROR
from historical_battles.hb_constants import ORDER_TOKEN_NAME_TO_ORDER_TYPE
from historical_battles.gui.shared.event_dispatcher import showOrdersInfoWindow
from historical_battles.gui.sounds.sound_hangar_controller import SoundHangarController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
import logging
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from EventShopAccountComponentBase import ShopBundle
    from HBShopAccountComponent import HBShopAccountComponent

class HBBoostersShopGoodiesBonusFormatter(GoodiesBonusFormatter):

    def _formatBonusLabel(self, count):
        return count

    @classmethod
    def _getImages(cls, item):
        return [item.getFullNameForResource()]


class HBBoostersShopItemsBonusFormatter(ItemsBonusFormatter):

    def _formatBonusLabel(self, count):
        return count

    @classmethod
    def _getImages(cls, item):
        return [item.getGUIEmblemID()]


class HBBoostersShopPremiumDaysBonusFormatter(PremiumDaysBonusFormatter):

    @classmethod
    def _getImages(cls, bonus):
        return ['{}_{}'.format(bonus.getName(), bonus.getValue())]


def getHBBoostersShopFormatterMap():
    formattersMap = getDefaultFormattersMap()
    formattersMap.update({PREMIUM_ENTITLEMENTS.BASIC: HBBoostersShopPremiumDaysBonusFormatter(),
     PREMIUM_ENTITLEMENTS.PLUS: HBBoostersShopPremiumDaysBonusFormatter(),
     'HBCoupon': HBQuestsTokenBonusFormatter(),
     'goodies': HBBoostersShopGoodiesBonusFormatter(),
     'items': HBBoostersShopItemsBonusFormatter()})
    return formattersMap


def getHBBoostersShopAwardFormatter():
    return AwardsPacker(getHBBoostersShopFormatterMap())


class BonusGroups(Enum):
    PREMIUM = 'premium_plus'
    TOKENS = 'battleToken'
    HB_TOKENS = 'HBCoupon'
    CUSTOMIZATIONS = 'customizations'
    OTHER = 'other'

    @classmethod
    def valueToEnum(cls, value):
        try:
            return cls(value)
        except ValueError:
            return None

        return None


class OrderView(SubModelPresenter):
    __slots__ = ('__tooltipIdGen', '__bonusCache')
    BONUS_GROUPS = (BonusGroups.PREMIUM, BonusGroups.TOKENS)
    BUNDLES_LAYOUT_ORDER = (BundleLayout.NEWBIE, BundleLayout.SPECIALIST, BundleLayout.MEISTER)
    BONUS_GROUPS_ORDER = (BonusGroups.PREMIUM, BonusGroups.OTHER)
    SHOP_GROUP_NAME = 'hb25FrontCouponsShop'
    _itemsCache = dependency.descriptor(IItemsCache)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, viewModel, parentView):
        super(OrderView, self).__init__(viewModel, parentView)
        self.__tooltipIdGen = None
        self.__bonusCache = None
        return

    @property
    def viewModel(self):
        return super(OrderView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            orderType = event.getArgument('orderType')
            showStatus = event.getArgument('showStatus')
            return OrderTooltip(orderType, showStatus)
        else:
            if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
                tooltipID = event.getArgument('tooltipID')
                if tooltipID == HbTooltipsConstants.TOOLTIP_NOT_ENOUGH_MONEY:
                    return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (int(event.getArgument('value')), event.getArgument('currency')))
                if tooltipID == HbTooltipsConstants.TOOLTIP_MONEY:
                    bundle = self.shop.getBundle(event.getArgument('bundleID'))
                    if bundle.oldPrice is None:
                        return
                    price, oldPrice = bundle.price, bundle.oldPrice
                    return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.ACTION_PRICE, specialArgs=(None,
                     None,
                     self.__convertMoneyToTuple(Money(**{price.currency: price.amount})),
                     self.__convertMoneyToTuple(Money(**{oldPrice.currency: oldPrice.amount})),
                     True,
                     False,
                     None,
                     True))
                if tooltipID == HbTooltipsConstants.TOOLTIP_BONUS:
                    bonus = self.__bonusCache.get(int(event.getArgument('id')))
                    if bonus:
                        return createBackportTooltipContent(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs)
            return

    def createToolTip(self, event):
        window = None
        content = self.createToolTipContent(event, event.contentID)
        if content is not None:
            window = ToolTipWindow(event, content, self.getParentWindow())
        if window is not None:
            window.load()
            window.move(event.mouse.positionX, event.mouse.positionY)
        return window

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    def initialize(self, *args, **kwargs):
        super(OrderView, self).initialize(args, kwargs)
        self.__tooltipIdGen = SequenceIDGenerator()
        self.__bonusCache = {}
        self.shop.onBundlePurchased += self.__onBundlePuchased
        self.shop.onShopUpdated += self.__onShopUpdated
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        g_clientUpdateManager.addCallback('shop.exchangeRate', self._moneyChangeHandler)
        with self.viewModel.transaction() as model:
            front = self.__gameEventController.frontController.getSelectedFront()
            model.setFrontName(front.getName())
        self.__updateMoney(self.viewModel)
        self.__fillBundles()
        SoundHangarController.onEnterOrdersView()

    def finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.shop.onBundlePurchased -= self.__onBundlePuchased
        self.shop.onShopUpdated -= self.__onShopUpdated
        self.__tooltipIdGen.clear()
        self.__tooltipIdGen = None
        self.__bonusCache = None
        super(OrderView, self).finalize()
        return

    @property
    def shop(self):
        return getattr(BigWorld.player(), 'HBShopAccountComponent', None)

    @property
    def bundles(self):
        return self.shop.getBundlesByGroup(self.SHOP_GROUP_NAME)

    def _getEvents(self):
        return ((self.viewModel.onBundleBuyClick, self.__onBundleBuyClick), (self.viewModel.onInfoClick, self.__onInfoClick))

    def _moneyChangeHandler(self, *_):
        with self.viewModel.transaction() as vm:
            self.__updateMoney(vm)

    def __updateMoney(self, model):
        money = self._itemsCache.items.stats.money
        model.setCredits(int(money.getSignValue(Currency.CREDITS)))
        model.setGold(int(money.getSignValue(Currency.GOLD)))

    def __onBundlePuchased(self, _):
        self.__fillBundles()

    def __onShopUpdated(self):
        self.__fillBundles()

    def __fillBundles(self):
        self.__bonusCache.clear()
        with self.viewModel.transaction() as vm:
            bundles = vm.getBundles()
            bundles.clear()
            for i, bundle in enumerate(self.bundles):
                if i >= len(self.BUNDLES_LAYOUT_ORDER):
                    break
                bundleVM = self.__makeBundleVM(self.BUNDLES_LAYOUT_ORDER[i], bundle)
                if not bundleVM:
                    continue
                bundles.addViewModel(bundleVM)

            bundles.invalidate()

    def __makeBundleVM(self, layout, bundle):
        purchasesLeft = self.shop.getBundlePurchasesLeft(bundle)
        if purchasesLeft is not None and purchasesLeft <= 0:
            return
        else:
            vm = BundleModel()
            vm.setId(bundle.id)
            vm.setLayout(layout)
            vm.setTitle(R.strings.hb_shop.bundles.dyn(bundle.id).title())
            vm.setCurrencyType(bundle.price.currency)
            vm.setPrice(bundle.price.amount)
            vm.setBuyCount(purchasesLeft or 0)
            discounts = Discount.getDiscountPercent(bundle.price, bundle.oldPrice)
            if bundle.price.currency in discounts:
                vm.setDiscount(discounts[bundle.price.currency])
            bonuses = vm.getBonuses()
            bonusGroups = self.__groupBonuses(bundle.bonuses, self.BONUS_GROUPS)
            if BonusGroups.TOKENS in bonusGroups:
                bonusData = bonusGroups.get(BonusGroups.TOKENS)
                if bonusData is None:
                    return
                bonus = bonusData[0]
                bonusName = self.__getBonusName(bonus)
                if not bonusName:
                    return
                vm.order.setType(ORDER_TOKEN_NAME_TO_ORDER_TYPE[bonusName])
                vm.order.setCount(bonus.getCount())
            for group in self.BONUS_GROUPS_ORDER:
                if group not in bonusGroups:
                    continue
                for bonus in getHBBoostersShopAwardFormatter().format(bonusGroups[group]):
                    bonuses.addViewModel(self.__makeBonusVM(bonus))

            return vm

    def __getBonusName(self, bonus):
        keys = bonus.getValue().keys()
        if not keys:
            return None
        else:
            bonusName = keys[0]
            return bonusName

    def __makeBonusVM(self, bonus):
        tooltipId = self.__tooltipIdGen.next()
        self.__bonusCache[tooltipId] = bonus
        vm = BundleBonusModel()
        vm.setIconName(bonus.images[0])
        vm.setAmount(1 if bonus.label is None else int(bonus.label[1:]))
        vm.tooltip.setId(tooltipId)
        return vm

    @staticmethod
    def __groupBonuses(bonuses, groups):
        result = {}
        for bonus in bonuses:
            bonusType = BonusGroups.valueToEnum(bonus.getName())
            if bonusType == BonusGroups.HB_TOKENS:
                bonusType = BonusGroups.TOKENS
            if bonusType is not None and bonusType in groups:
                result.setdefault(bonusType, []).append(bonus)
            result.setdefault(BonusGroups.OTHER, []).append(bonus)

        return result

    @staticmethod
    def __convertMoneyToTuple(money):
        return (money.credits, money.gold, money.crystal)

    @oncePerPeriod(1)
    @adisp_process
    def __onBundleBuyClick(self, args):
        idx = int(args.get('idx'))
        count = int(args.get('count'))
        bundleViewModels = self.viewModel.getBundles()
        if not bundleViewModels:
            LOG_ERROR('__onBundleBuyClick invoked, but there is no bundles')
            return
        else:
            bundleVM = bundleViewModels[idx]
            bundle = self.shop.getBundle(bundleVM.getId())
            if bundle.price.amount > int(self._itemsCache.items.stats.money.getSignValue(bundle.price.currency)):
                if bundle.price.currency == Currency.GOLD:
                    showBuyGoldForBundle(bundle.price.amount, {})
                return
            data = {'layout': bundleVM.getLayout(),
             'order': Order(bundleVM.order.getType(), bundleVM.order.getCount()),
             'bonuses': [ Bonus(bonus.getIconName(), bonus.getAmount(), self.__bonusCache[bonus.tooltip.getId()]) for bonus in bundleVM.getBonuses() ],
             'price': Money(**{bundle.price.currency: bundle.price.amount * count}),
             'oldPrice': Money(**{bundle.oldPrice.currency: bundle.oldPrice.amount * count}) if bundle.oldPrice else None,
             'count': count}
            bundleID = bundle.id
            bundleVM = None
            bundle = None
            yield wg_await(asyncDoAction(HBShopBuyBundleAction(bundleID, BoosterBuyDialogView, data)))
            return

    def __onInfoClick(self):
        showOrdersInfoWindow()
