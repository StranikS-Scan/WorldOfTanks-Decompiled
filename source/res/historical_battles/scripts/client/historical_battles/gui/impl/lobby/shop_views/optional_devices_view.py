# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/optional_devices_view.py
import operator
import os
from itertools import imap
from logging import getLogger
import typing
from adisp import adisp_process
from wg_async import wg_await
from frameworks.wulf import ViewSettings, ViewFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions.factory import asyncDoAction
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.common.simple_price_view_model import SimplePriceViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.optional_device_item_view_model import OptionalDeviceItemViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.optional_devices_view_model import OptionalDevicesViewModel
from historical_battles.gui.impl.lobby.shop_views.base_shop_group_view import BaseShopGroupView
from historical_battles.gui.impl.lobby.shop_views.shop_buy_dialog_view import ShopBuyDialogView
from historical_battles.gui.impl.lobby.shop_views.utils import getCurrentCurrencyCount, getSortedPriceList
from historical_battles.gui.impl.lobby.tooltips.general_hb_coin_tooltip import GeneralHbCoinTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_coin_exchange_tooltip import HbCoinExchangeTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.impl.lobby.widgets.coin_widget import CoinWidget
from historical_battles.gui.shared.event_dispatcher import showHBHangar, showShopView
from historical_battles.gui.shared.gui_items.items_actions.hb_shop import HBShopBuyBundleAction
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from shared_utils import first
if typing.TYPE_CHECKING:
    from EventShopAccountComponentBase import ShopBundle
    from gui.shared.gui_items.artefacts import OptionalDevice
    from historical_battles_common.helpers_common import EventShopBundlePrice
_logger = getLogger(__name__)

class OptionalDevicesView(BaseShopGroupView):
    SHOP_GROUP_NAME = 'hb22OptionalDevices'
    __geCtrl = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = OptionalDevicesViewModel()
        super(OptionalDevicesView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(OptionalDevicesView, self).getViewModel()

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
            return super(OptionalDevicesView, self).createToolTipContent(event, contentID)

    def _onLoading(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.onBack += self.__onBack
        self.viewModel.items.onItemClicked += self.__onItemClicked
        self.__geCtrl.coins.onCoinsCountChanged += self.__onMoneyChanged
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyChanged)
        self.__coinWidget = CoinWidget(self.viewModel.coinWidget)
        self.__coinWidget.onLoading()
        super(OptionalDevicesView, self)._onLoading()

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onBack -= self.__onBack
        self.viewModel.items.onItemClicked -= self.__onItemClicked
        if self.__geCtrl.coins:
            self.__geCtrl.coins.onCoinsCountChanged -= self.__onMoneyChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__coinWidget:
            self.__coinWidget.destroy()
        super(OptionalDevicesView, self)._finalize()

    def _fillBundles(self):
        with self.viewModel.transaction() as tx:
            if self.__coinWidget:
                self.__coinWidget.updateModel(tx.coinWidget)
            tx.setPurchasesLeft(self.getGroupPurchasesLeft(default=-1))
            items = tx.items.getItems()
            items.clear()
            bundles = sorted(((bundle, self.__getDevice(bundle)) for bundle in self.bundles), key=lambda (b, d): (-sum(imap(operator.attrgetter('amount'), b.prices)), d.userName if d else ''))
            for bundle, device in bundles:
                if device is None:
                    _logger.error('Cannot find optional device in bundle id = %s', bundle.id)
                    continue
                effect = first(R.strings.artefacts.dyn(device.descriptor.groupName).dyn('effect').values(), R.invalid)
                deviceVM = OptionalDeviceItemViewModel()
                deviceVM.setId(bundle.id)
                deviceVM.setIcon(self.__getIconName(device))
                deviceVM.setBuyCount(device.inventoryCount)
                deviceVM.setOverlayType(device.getOverlayType())
                deviceVM.setEffect(effect())
                bonuses = deviceVM.bonuses.getItems()
                for kpi in device.getKpi():
                    bonusModel = BonusModel()
                    bonusModel.setLocaleName(kpi.name)
                    values = bonusModel.getValues()
                    value = BonusValueModel()
                    value.setValue(kpi.value)
                    value.setValueKey(kpi.name)
                    value.setValueType(kpi.type)
                    values.addViewModel(value)
                    deviceVM.bonuses.setTitle(device.userName)
                    bonuses.addViewModel(bonusModel)

                self.__updatePriceVMs(bundle, deviceVM.price.getPrices())
                items.addViewModel(deviceVM)

            items.invalidate()
        return

    def __onMoneyChanged(self, *_):
        with self.viewModel.transaction() as tx:
            deviceVMs = tx.items.getItems()
            for deviceVM in deviceVMs:
                priceVMs = deviceVM.price.getPrices()
                priceVMs.clear()
                self.__updatePriceVMs(self.shop.getBundle(deviceVM.getId()), priceVMs)

            deviceVMs.invalidate()

    def __updatePriceVMs(self, bundle, priceVMs):
        for price in getSortedPriceList(bundle.prices):
            currencyType, currentCount = getCurrentCurrencyCount(price)
            if currencyType is None:
                _logger.error('Unknown virtual currency = %s', price.currency)
                continue
            priceVM = SimplePriceViewModel()
            priceVM.setType(currencyType)
            priceVM.setValue(price.amount)
            priceVM.setIsEnough(currentCount - price.amount >= 0)
            priceVMs.addViewModel(priceVM)

        return

    @staticmethod
    def __onBack():
        showShopView()

    @staticmethod
    def __onClose():
        showHBHangar()

    @adisp_process
    def __onItemClicked(self, args):
        bundleID = args.get('bundleID')
        if bundleID is None:
            _logger.error('Expected bundleID arg')
            return
        else:
            bundle = self.shop.getBundle(bundleID)
            device = self.__getDevice(bundle)
            iconsRes = R.images.gui.maps.shop.artefacts.c_180x135
            data = {'titleText': backport.text(R.strings.hb_shop.opt_device_buy_dialog.title(), name=device.userName),
             'overlays': [iconsRes.dyn('{}_{}'.format(device.getOverlayType(), 'overlay'))()],
             'backgrounds': [R.images.historical_battles.gui.maps.icons.common.upgrade_bg_enhanced()],
             'icon': iconsRes.dyn(self.__getIconName(device))(),
             'bundle': bundle}
            yield wg_await(asyncDoAction(HBShopBuyBundleAction(bundle, ShopBuyDialogView, data, callback=showShopView)))
            return

    @staticmethod
    def __getDevice(bundle):
        return next((device for bonus in bundle.bonuses for device, count in bonus.getItems().iteritems() if GUI_ITEM_TYPE.OPTIONALDEVICE == device.itemTypeID), (None, None))

    def __getIconName(self, device):
        return os.path.splitext(device.icon)[0]
