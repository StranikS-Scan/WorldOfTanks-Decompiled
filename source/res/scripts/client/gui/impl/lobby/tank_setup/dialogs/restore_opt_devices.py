# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/restore_opt_devices.py
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.restore_view_model import RestoreViewModel, EquipmentType
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.equipment_price_model import EquipmentPriceModel
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.shared.gui_items.processors.module import OptDeviceRestorer
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.utils import decorators
from gui.shared.money import Currency
from gui import SystemMessages
from gui.impl.gen import R

def _chooseEquipmentType(device):
    if device.isDeluxe:
        return EquipmentType.IMPROVED
    return EquipmentType.TROPHY if device.isTrophy else EquipmentType.MODERNIZED


class RestoreOptDevices(ViewImpl):
    __slots__ = ('__restoreCtx', '__money', '__blur')
    _MIN_EQUIP_COUNT = 1

    def __init__(self, restoreCtx, money):
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.Restore(), model=RestoreViewModel())
        self.__restoreCtx = restoreCtx
        self.__money = money
        self.__blur = None
        super(RestoreOptDevices, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(RestoreOptDevices, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onRestore, self.__onRestore), (self.viewModel.onClose, self.__onClose))

    def _finalize(self):
        self.__blur.fini()
        super(RestoreOptDevices, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(RestoreOptDevices, self)._onLoading(*args, **kwargs)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.WINDOW)
        ctx = self.__restoreCtx
        with self.viewModel.transaction() as model:
            model.setEquipmentType(_chooseEquipmentType(ctx.device))
            model.setMinEquipCount(self._MIN_EQUIP_COUNT)
            model.setMaxEquipCount(self.__getMaxEquipCount(ctx.count, ctx.restorePrice))
            model.equipmentBonus.setItem(ctx.device.getGUIEmblemID())
            model.equipmentBonus.setOverlayType(ctx.device.getOverlayType())
            model.equipmentBonus.setName(ctx.device.name)
            self.__fillEquipmentPriceList(model, ctx.restorePrice)

    def __fillEquipmentPriceList(self, model, restorePrices):
        priceList = model.getEquipmentPriceList()
        priceList.clear()
        for cur, amount in restorePrices:
            price = EquipmentPriceModel()
            price.setType(cur)
            price.setPrice(amount)
            priceList.addViewModel(price)

        priceList.invalidate()

    def __getMaxEquipCount(self, count, restorePrices):
        if count == self._MIN_EQUIP_COUNT:
            return self._MIN_EQUIP_COUNT
        maxN = count
        for cur, amount in restorePrices:
            if amount <= 0:
                continue
            balance = self.__money.get(cur, 0)
            maxN = min(maxN, balance // amount)

        return maxN

    @decorators.adisp_process('restoreItem')
    def __onRestore(self, args):
        ctx = self.__restoreCtx
        amount = int(args.get('amount'))
        pricePerItem = ctx.restorePrice
        totalPrice = tuple(((cur, val * amount) for cur, val in pricePerItem))
        useDemountKit = any((cur == Currency.DEMOUNT_KIT for cur, _ in pricePerItem))
        result = yield OptDeviceRestorer(ctx.device, ctx.reason, amount, useDemountKit, totalPrice).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, priority=result.msgPriority, messageData=result.msgData)
        self.destroyWindow()

    def __onClose(self):
        self.destroyWindow()


class RestoreOptDevicesWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, restoreCtx, money, parent=None):
        super(RestoreOptDevicesWindow, self).__init__(WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=RestoreOptDevices(restoreCtx, money), parent=parent)
