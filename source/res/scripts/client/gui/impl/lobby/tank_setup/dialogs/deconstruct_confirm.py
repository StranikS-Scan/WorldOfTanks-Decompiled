# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/deconstruct_confirm.py
from itertools import chain
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CustomSoundButtonPresenter, getConfirmButton, CancelButton
from gui.impl.gen import R
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.confirm_actions_with_equipment_dialog_model import ConfirmActionsWithEquipmentDialogModel, DialogType as LocationDialogType
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.deconstruct_confirm_model import DeconstructConfirmModel, DialogType as ActionDialogType
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.main_content.deconstruct_confirm_item_model import DeconstructConfirmItemModel
from gui.impl.lobby.tank_setup.array_providers.opt_device import DeconstructOptDeviceStorageProvider, DeconstructOptDeviceOnVehicleProvider, ListTypes
from gui.impl.lobby.tank_setup.dialogs.dialog_helpers.balance import initBalance
from gui.impl.lobby.tank_setup.dialogs.dialog_helpers.model_formatters import initItemInfo
from gui.impl.lobby.tank_setup.tooltips.deconstruct_from_inventory_tooltip import DeconstructFromInventoryTooltip
from gui.impl.lobby.tank_setup.tooltips.deconstruct_from_vehicle_tooltip import DeconstructFromVehicleTooltip
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_SUBMIT_CLICK_SOUND = 'mod_equipment_disassemble'

class DeconstructMultConfirm(DialogTemplateView):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('storageItems', 'vehicleItems', 'upgradeModulePair', 'ctx', '__tooltipCache', '_storageProvider', '_onVehicleProvider')
    LAYOUT_ID = R.views.lobby.tanksetup.dialogs.DeconstructConfirm()
    VIEW_MODEL = DeconstructConfirmModel

    def __init__(self, ctx):
        self.ctx = ctx
        self.storageItems = ctx.cart.storage.values()
        self.vehicleItems = chain(*ctx.cart.onVehicle.values())
        self.upgradeModulePair = ctx.upgradedPair
        self.__tooltipCache = {}
        self._storageProvider = DeconstructOptDeviceStorageProvider()
        self._onVehicleProvider = DeconstructOptDeviceOnVehicleProvider()
        super(DeconstructMultConfirm, self).__init__()

    @property
    def viewModel(self):
        return self.getViewModel()

    def updateArray(self, array, items, isInventory=False):
        totalCount = 0
        array.clear()
        tooltipItems = self.__tooltipCache.setdefault(ListTypes.STORAGE if isInventory else ListTypes.ON_VEHICLE, {})
        itemsDict = dict()
        for itemSpec in items:
            itemsList = itemsDict.setdefault(itemSpec.intCD, [])
            itemsList.append(itemSpec)

        for intCD, itemSpecs in sorted(itemsDict.items(), key=self._sortItemsKey):
            itemModel = DeconstructConfirmItemModel()
            item = self.itemsCache.items.getItemByCD(intCD)
            count = sum(((itemSpec.count if isInventory else 1) for itemSpec in itemSpecs))
            if isInventory:
                tooltipItems[intCD] = count
            else:
                vehiclesNames = []
                for itemSpec in itemSpecs:
                    vehCD = itemSpec.vehicleCD
                    vehicle = self.itemsCache.items.getItemByCD(vehCD)
                    if vehicle:
                        vehiclesNames.append(vehicle.userName)

                tooltipItems.update({intCD: vehiclesNames})
            totalCount += count
            itemModel.setIntCD(intCD)
            itemModel.setName('')
            itemModel.setValue(str(count))
            itemModel.setIcon(item.descriptor.iconName)
            itemModel.setLevel(item.level)
            array.addViewModel(itemModel)

        array.invalidate()
        return totalCount

    def createToolTipContent(self, event, contentID):
        intCD = int(event.getArgument('intCD'))
        if not intCD:
            return None
        else:
            item = self.itemsCache.items.getItemByCD(intCD)
            title = item.userName
            if contentID == R.views.lobby.tanksetup.tooltips.DeconstructFromInventoryTooltip():
                tooltipItems = self.__tooltipCache.get(ListTypes.STORAGE, {})
                if intCD in tooltipItems:
                    value = tooltipItems[intCD]
                    return DeconstructFromInventoryTooltip(title, value)
            if contentID == R.views.lobby.tanksetup.tooltips.DeconstructFromVehicleTooltip():
                tooltipItems = self.__tooltipCache.get(ListTypes.ON_VEHICLE, {})
                if intCD in tooltipItems:
                    value = tooltipItems[intCD]
                    return DeconstructFromVehicleTooltip(title, value)
            return None

    def _onLoading(self, *args, **kwargs):
        super(DeconstructMultConfirm, self)._onLoading(*args, **kwargs)
        self._update()
        self.__initBalance()
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        if self.upgradeModulePair:
            _item, _ = self.upgradeModulePair
            self.viewModel.setDialogType(ActionDialogType.UPGRADE)
            self.viewModel.setDeviceName(_item.name)
            upgradePrice = _item.getUpgradePrice(self.itemsCache.items).price
            self.viewModel.setEquipUpgradeCost(upgradePrice.equipCoin)
            confirmButton = R.strings.dialogs.equipmentDeconstruction.confirmAndUpgradeButton()
        else:
            self.viewModel.setDialogType(ActionDialogType.DECONSTRUCT)
            confirmButton = R.strings.dialogs.equipmentDeconstruction.confirmButton()
        self.addButton(getConfirmButton(CustomSoundButtonPresenter, label=confirmButton, soundClick=_SUBMIT_CLICK_SOUND))
        self.addButton(CancelButton(R.strings.dialogs.equipmentUpgrade.cancelButton()))
        self.viewModel.onClose += self._closeClickHandler

    def _finalize(self):
        self.viewModel.onClose -= self._closeClickHandler
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(DeconstructMultConfirm, self)._finalize()

    def _sortItemsKey(self, item):
        itemCD, _ = item
        item = self.itemsCache.items.getItemByCD(itemCD)
        return (-item.level, item.userName)

    def _update(self):
        self._storageProvider.updateItems()
        self._onVehicleProvider.updateItems()
        with self.viewModel.transaction() as model:
            totalCount = sum((item.inventoryCount for item in self._storageProvider.getItems())) + len(self._onVehicleProvider.getItems())
            totalIncome = self._storageProvider.getTotalPrice(self.ctx) + self._onVehicleProvider.getTotalPrice(self.ctx)
            model.setDeconstructingEquipCoinsAmount(totalIncome.equipCoin)
            storageCount = self.updateArray(model.getInventoryEquipment(), self.storageItems, True)
            vehicleCount = self.updateArray(model.getVehicleEquipment(), self.vehicleItems)
            countLeft = totalCount - (storageCount + vehicleCount)
            model.setIsLastVehicleEquipment(countLeft == 0)

    def __initBalance(self):
        initBalance(self.viewModel.getBalance(), (Currency.EQUIP_COIN,), self.itemsCache)

    def __onMoneyUpdated(self, _):
        self.__initBalance()


class DeconstructConfirm(DialogTemplateView):
    __slots__ = ('__device', '__currency', '__fromVehicle', '__curCount')
    LAYOUT_ID = R.views.lobby.tanksetup.dialogs.ConfirmActionsWithEquipmentDialog()
    VIEW_MODEL = ConfirmActionsWithEquipmentDialogModel
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemIntCD, fromVehicle=False):
        super(DeconstructConfirm, self).__init__()
        self.__device = self.__itemsCache.items.getItemByCD(itemIntCD)
        self.__currency = self.__device.sellPrices.itemPrice.price.getCurrency(byWeight=True)
        self.__fromVehicle = fromVehicle
        self.__curCount = self.__device.inventoryCount if not fromVehicle else 1

    @property
    def viewModel(self):
        return super(DeconstructConfirm, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DeconstructConfirm, self)._onLoading(*args, **kwargs)
        if self.__fromVehicle:
            self.viewModel.setDialogType(LocationDialogType.DECONSTRUCTFROMSLOTS)
        else:
            self.viewModel.setDialogType(LocationDialogType.DECONSTRUCTFROMSTORAGE)
        self.viewModel.setAlertText(backport.text(R.strings.tank_setup.dialogs.confirmActionsWithEquipmentDialog.warning()))
        initBalance(self.viewModel.getBalance(), (self.__currency,), self.__itemsCache)
        initItemInfo(self.viewModel, self.__device, self.__currency)
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(DeconstructConfirm, self)._finalize()

    def _getAdditionalData(self):
        return self.__curCount

    def __addListeners(self):
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        self.viewModel.onDeconstruct += self.__onDeconstruct
        self.viewModel.onClose += self.__onClose

    def __removeListeners(self):
        self.viewModel.onDeconstruct -= self.__onDeconstruct
        self.viewModel.onClose -= self.__onClose
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onDeconstruct(self, count):
        self.__curCount = count.get('count', 1)
        self._setResult(DialogButtons.SUBMIT)

    def __onClose(self, *args, **kwargs):
        self._setResult(DialogButtons.CANCEL)

    def __onMoneyUpdated(self, _):
        initBalance(self.viewModel.getBalance(), (self.__currency,), self.__itemsCache)
