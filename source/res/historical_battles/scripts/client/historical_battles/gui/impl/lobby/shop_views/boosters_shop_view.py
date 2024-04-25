# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/boosters_shop_view.py
from enum import Enum
from adisp import adisp_process
from wg_async import wg_await
from historical_battles_common.helpers_common import Discount
from constants import PREMIUM_ENTITLEMENTS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.server_events.awards_formatters import AwardsPacker, getDefaultFormattersMap, ItemsBonusFormatter, GoodiesBonusFormatter, PremiumDaysBonusFormatter
from gui.shared.gui_items.items_actions.factory import asyncDoAction
from gui.shared.money import Currency, Money
from gui.shop import showBuyGoldForBundle
from historical_battles.hb_constants import InfoViewKeys
from helpers import dependency
from historical_battles.gui.impl.dialogs.sub_views.content.order_with_bonuses import Order, Bonus
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderType
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.boosters_shop_view_model import BoostersShopViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_bonus_view_model import BundleBonusViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_view_model import BundleViewModel, BundleLayout
from historical_battles.gui.impl.lobby.base_event_view import InfoCommonViewSettings
from historical_battles.gui.impl.lobby.order_info_view import OrderInfoView
from historical_battles.gui.impl.lobby.shop_views.base_shop_group_view import BaseShopGroupView
from historical_battles.gui.impl.lobby.shop_views.booster_buy_dialog_view import BoosterBuyDialogView
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from historical_battles.gui.server_events.hb_awards_formatter import HBQuestsTokenBonusFormatter
from historical_battles.gui.shared.event_dispatcher import showHBHangar
from historical_battles.gui.shared.gui_items.items_actions.hb_shop import HBShopBuyBundleAction
from historical_battles.gui.sounds.sound_constants import BOOSTERS_SHOP_SOUND_SPACE
from ids_generators import SequenceIDGenerator
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.shared import IItemsCache
from gui.impl.pub.lobby_window import LobbyWindow
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

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


class BoostersShopView(BaseShopGroupView):
    _COMMON_SOUND_SPACE = BOOSTERS_SHOP_SOUND_SPACE
    BONUS_GROUPS = (BonusGroups.PREMIUM, BonusGroups.TOKENS)
    BUNDLES_LAYOUT_ORDER = (BundleLayout.NEWBIE, BundleLayout.SPECIALIST, BundleLayout.MEISTER)
    BONUS_GROUPS_ORDER = (BonusGroups.PREMIUM, BonusGroups.OTHER)
    SHOP_GROUP_NAME = 'hb22FrontCouponsShop'
    layoutID = R.views.historical_battles.lobby.BoostersShopView()
    INFO_VIEW_SETTINGS = InfoCommonViewSettings(layoutID=R.views.historical_battles.lobby.InfoViews.OrderInfoX10View(), viewClass=OrderInfoView, viewKey=InfoViewKeys.ORDER_INFO_X10_VIEW.value)
    _itemsCache = dependency.descriptor(IItemsCache)
    _platoonCtrl = dependency.descriptor(IPlatoonController)
    __hbCtrl = dependency.descriptor(IGameEventController)

    def __init__(self, layoutId=None):
        settings = ViewSettings(layoutId or self.layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, BoostersShopViewModel())
        super(BoostersShopView, self).__init__(settings)
        self.__tooltipIdGen = SequenceIDGenerator()
        self.__bonusCache = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            orderType = event.getArgument('orderType')
            isPreview = event.getArgument('isPreview')
            isUsedInBattle = event.getArgument('isUsedInBattle')
            return OrderTooltip(orderType, isPreview, isUsedInBattle)
        else:
            if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
                tooltipID = event.getArgument('tooltipID')
                if tooltipID == BoostersShopViewModel.TOOLTIP_NOT_ENOUGH_MONEY:
                    return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (int(event.getArgument('value')), event.getArgument('currency')))
                if tooltipID == BoostersShopViewModel.TOOLTIP_MONEY:
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
                if tooltipID == BoostersShopViewModel.TOOLTIP_BONUS:
                    bonus = self.__bonusCache.get(int(event.getArgument('id')))
                    if bonus:
                        return createBackportTooltipContent(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs)
            return super(BoostersShopView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(BoostersShopView, self)._onLoading(*args, **kwargs)
        self.viewModel.onClose += self._closeHandler
        self.viewModel.onBundleBuyClicked += self._buyClickedHandler
        self.viewModel.onInfoIconClicked += self._infoClickHandler
        self._platoonCtrl.onMembersUpdate += self._checkPlatoonStatus
        self.__hbCtrl.onShowBattleQueueView += self.__onShowBattleQueueView
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        g_clientUpdateManager.addCallback('shop.exchangeRate', self._moneyChangeHandler)
        self._updateMoney(self.viewModel)

    def _finalize(self):
        self.__bonusCache.clear()
        self.viewModel.onClose -= self._closeHandler
        self.viewModel.onBundleBuyClicked -= self._buyClickedHandler
        self.viewModel.onInfoIconClicked -= self._infoClickHandler
        self._platoonCtrl.onMembersUpdate -= self._checkPlatoonStatus
        self.__hbCtrl.onShowBattleQueueView -= self.__onShowBattleQueueView
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BoostersShopView, self)._finalize()

    def _closeHandler(self):
        showHBHangar()
        self.destroyWindow()

    def _checkPlatoonStatus(self):
        if self._platoonCtrl.isInQueue():
            showHBHangar()

    def _infoClickHandler(self):
        from historical_battles.gui.shared.event_dispatcher import showInfoWindow
        showInfoWindow((self.INFO_VIEW_SETTINGS.layoutID, self.INFO_VIEW_SETTINGS.viewClass))

    def __onShowBattleQueueView(self):
        self.destroyWindow()

    @adisp_process
    def _buyClickedHandler(self, args):
        idx = int(args.get('idx'))
        count = int(args.get('count'))
        bundleVM = self.viewModel.getBundles()[idx]
        bundle = self.shop.getBundle(bundleVM.getId())
        if bundle.price.amount > int(self._itemsCache.items.stats.money.getSignValue(bundle.price.currency)):
            if bundle.price.currency == Currency.GOLD:
                showBuyGoldForBundle(bundle.price.amount, {})
            return
        else:
            data = {'layout': bundleVM.getLayout(),
             'order': Order(bundleVM.order.getType(), bundleVM.order.getCount()),
             'bonuses': [ Bonus(bonus.getIconName(), bonus.getAmount(), self.__bonusCache[bonus.tooltip.getId()]) for bonus in bundleVM.getBonuses() ],
             'price': Money(**{bundle.price.currency: bundle.price.amount * count}),
             'oldPrice': Money(**{bundle.oldPrice.currency: bundle.oldPrice.amount * count}) if bundle.oldPrice else None,
             'count': count}
            yield wg_await(asyncDoAction(HBShopBuyBundleAction(bundle, BoosterBuyDialogView, data)))
            return

    def _moneyChangeHandler(self, *_):
        with self.viewModel.transaction() as model:
            self._updateMoney(model)

    def _updateMoney(self, model):
        money = self._itemsCache.items.stats.money
        model.setCredits(int(money.getSignValue(Currency.CREDITS)))
        model.setGold(int(money.getSignValue(Currency.GOLD)))
        model.setExchangeRate(self._itemsCache.items.shop.exchangeRate)

    def _fillBundles(self):
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
            vm = BundleViewModel()
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
                vm.order.setType(OrderType.MEDIUM)
                vm.order.setCount(bonusGroups[BonusGroups.TOKENS][0].getCount())
            for group in self.BONUS_GROUPS_ORDER:
                if group not in bonusGroups:
                    continue
                for bonus in getHBBoostersShopAwardFormatter().format(bonusGroups[group]):
                    bonuses.addViewModel(self.__makeBonusVM(bonus))

            return vm

    def __makeBonusVM(self, bonus):
        tooltipId = self.__tooltipIdGen.next()
        self.__bonusCache[tooltipId] = bonus
        vm = BundleBonusViewModel()
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


class HBBoosterShop(LobbyWindow):

    def __init__(self, layoutID):
        super(HBBoosterShop, self).__init__(wndFlags=WindowFlags.WINDOW, content=BoostersShopView(layoutId=layoutID))
