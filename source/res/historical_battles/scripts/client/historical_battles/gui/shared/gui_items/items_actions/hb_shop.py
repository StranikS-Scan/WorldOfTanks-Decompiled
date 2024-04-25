# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/gui_items/items_actions/hb_shop.py
from collections import namedtuple
import typing
import BigWorld
from wg_async import wg_async, wg_await
from adisp import adisp_async, adisp_process
from frameworks.wulf import WindowLayer
from gui import SystemMessages
from gui.impl.dialogs import dialogs
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.common.fade_manager import FadeManager, waitWindowLoading, showDialog
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions.actions import AsyncGUIItemAction
from gui.shared.gui_items.processors.vehicle import VehicleSlotBuyer
from gui.shared.money import Currency, Money
from gui.shop import showBuyGoldForBundle
from helpers import dependency
from historical_battles.gui.impl.lobby.shop_views.buy_vehicle_dialog_view import BuyVehicleDialogView
from historical_battles.gui.shared.event_dispatcher import showCongratsMainRewardView
from historical_battles_common.helpers_common import getVehicleBonus
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Callable
    from frameworks.wulf import View
    from EventShopAccountComponentBase import ShopBundle

class HBShopAction(AsyncGUIItemAction):

    @property
    def shop(self):
        return getattr(BigWorld.player(), 'HBShopAccountComponent', None)

    @adisp_async
    @wg_async
    def showDialog(self, dialog, callback=None):
        result = yield wg_await(dialogs.show(FullScreenDialogWindowWrapper(dialog)))
        callback(result)


class HBShopBuyBundleAction(HBShopAction):

    def __init__(self, bundle, confirmationDialogFactory, data, callback=None):
        super(HBShopBuyBundleAction, self).__init__()
        self._bundle = bundle
        self._confirmationDialogFactory = confirmationDialogFactory
        self._data = data
        self._callback = callback

    @adisp_async
    @adisp_process
    def doAction(self, callback):
        result = False
        configRevision = self.shop.configRevision
        button, data = yield wg_await(self.showDialog(self._confirmationDialogFactory(data=self._data)))
        if button in DialogButtons.ACCEPT_BUTTONS:
            if self.shop.configRevision == configRevision:
                yield self.shop.processPurchaseBundle(self._bundle.id, (data or {}).get('count', 1))
                if self._callback:
                    self._callback()
            else:
                self.shop.showErrorSystemMessage()
        callback(result)


class HBShopBuyMainPrizeAction(HBShopAction):
    ActionResult = namedtuple('ActionResult', ('success', 'forGold'))
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, bundle, showHangarOnClose=False):
        super(HBShopBuyMainPrizeAction, self).__init__()
        self._bundle = bundle
        self._showHangarOnClose = showHangarOnClose
        self.__configRevision = self.shop.configRevision

    @adisp_async
    @adisp_process
    def doAction(self, callback):
        bundleBonuses = self.shop.getBundleBonusesWithQuests(self._bundle)
        vehicle = getVehicleBonus(bundleBonuses)
        currency = self._bundle.price.currency
        defaultAmount = self._bundle.price.amount
        discountedPrice = self.shop.getBundleDiscountedPrice(self._bundle)
        currentAmount = discountedPrice.amount if discountedPrice else defaultAmount
        if currentAmount == 0:
            with FadeManager(WindowLayer.SERVICE_LAYOUT) as fadeManager:
                yield wg_await(fadeManager.show())
                result = yield self.shop.processPurchaseMainPrizeBundle(self._bundle.id, 0, 0)
                if result.success:
                    yield showCongratsMainRewardView(forGold=False, showHangarOnClose=self._showHangarOnClose)
                yield wg_await(fadeManager.hide())
            callback(self.ActionResult(result.success, False))
            return
        if currency == Currency.GOLD:
            needGoldAmount = int(self.itemsCache.items.stats.money.getSignValue(currency)) - currentAmount
            if needGoldAmount < 0:
                showBuyGoldForBundle(currentAmount, {})
                callback(self.ActionResult(False, False))
                return
        with FadeManager(WindowLayer.SERVICE_LAYOUT) as fadeManager:
            yield wg_await(fadeManager.show())
            dialog = FullScreenDialogWindowWrapper(BuyVehicleDialogView(vehicle, ItemPrice(Money.makeFrom(currency, currentAmount), Money.makeFrom(currency, defaultAmount)), self.buyVehicle))
            yield wg_await(waitWindowLoading(dialog))
            yield wg_await(fadeManager.hide())
            result, _ = yield wg_await(showDialog(dialog))
            yield wg_await(fadeManager.show())
            dialog.destroy()
            success = result.success if result else False
            if success:
                yield showCongratsMainRewardView(forGold=True, showHangarOnClose=self._showHangarOnClose)
            yield wg_await(fadeManager.hide())
        callback(self.ActionResult(success, True))

    @adisp_async
    @adisp_process
    def buyVehicle(self, isWithSlot, isWithAmmo, crewType, callback):
        yield lambda callback: callback(True)
        result = False
        if self.shop.configRevision == self.__configRevision:
            if isWithSlot:
                result = yield VehicleSlotBuyer(showConfirm=False, showWarning=False).request()
                if result.userMsg:
                    SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
                if not result.success:
                    callback(result)
                    return
            result = yield self.shop.processPurchaseMainPrizeBundle(self._bundle.id, crewType, isWithAmmo)
        else:
            self.shop.showErrorSystemMessage()
        callback(result)
