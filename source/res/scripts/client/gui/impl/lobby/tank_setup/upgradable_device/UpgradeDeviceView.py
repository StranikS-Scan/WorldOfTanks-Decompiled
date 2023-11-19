# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/upgradable_device/UpgradeDeviceView.py
import logging
from frameworks.wulf import Array
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.device_upgrade_dialog_model import DeviceUpgradeDialogModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.main_content.kpi_item_model import KpiItemModel
from gui.impl.lobby.tank_setup.dialogs.dialog_helpers.balance import initBalance
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import showDeconstructionDeviceWindow
from gui.shared.gui_items import getKpiValueString, GUI_ITEM_TYPE
from gui.shared.money import Currency
from gui.shared.tooltips.common import getSimpleTooltipFactory
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from skeletons.gui.shared import IItemsCache
from skeletons.gui.app_loader import IAppLoader
_logger = logging.getLogger(__name__)

class UpgradableDeviceUpgradeConfirmView(DialogTemplateView):
    __slots__ = ('__currentModule', '__upgradePrice', '__vehicle', '__onDeconstructed')
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)
    VIEW_MODEL = DeviceUpgradeDialogModel
    LAYOUT_ID = R.views.lobby.tanksetup.dialogs.DeviceUpgradeDialog()

    def __init__(self, currentModule, vehicle=None, onDeconstructed=None):
        super(UpgradableDeviceUpgradeConfirmView, self).__init__()
        self.__currentModule = currentModule
        self.__upgradePrice = currentModule.getUpgradePrice(self.__itemsCache.items).price
        self.__vehicle = vehicle
        self.__onDeconstructed = onDeconstructed

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(UpgradableDeviceUpgradeConfirmView, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        self.__itemsCache.onSyncCompleted += self.__optDevicesUpdated
        self.__initBalance()
        self.__setUpgradeCost()
        modules = []
        _getDowngradeInfo(modules, self.__currentModule)
        self.viewModel.setCurrentModuleIdx(len(modules))
        modules.append(self.__currentModule)
        _getUpgradeInfo(modules, self.__currentModule)
        _fillDeviceInfo(modules, self.__currentModule, self.viewModel)
        canGetMoreCurrency = self.__canGetMoreCurrency()
        self.viewModel.setCanGetMoreCurrency(canGetMoreCurrency)
        self.addButton(ConfirmButton(self.__getConfirmButtonTxtRes(), tooltipFactory=self.__getSubmitTooltipFactory(), isDisabled=self.__isSubmitDisabled(canGetMoreCurrency)))
        self.addButton(CancelButton(R.strings.dialogs.equipmentUpgrade.cancelButton()))

    def _finalize(self):
        self.__itemsCache.onSyncCompleted -= self.__optDevicesUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(UpgradableDeviceUpgradeConfirmView, self)._finalize()

    def _setResult(self, result):
        disassemblyRequested = False
        if result == DialogButtons.SUBMIT and not self.__currentModule.mayPurchaseUpgrade(self.__itemsCache.items):
            result = DialogButtons.CANCEL
            disassemblyRequested = True
        super(UpgradableDeviceUpgradeConfirmView, self)._setResult(result)
        if disassemblyRequested:
            vehCD = self.__vehicle.intCD if self.__vehicle is not None else None
            showDeconstructionDeviceWindow(upgradedPair=(self.__currentModule, vehCD), parent=self.getParentWindow(), onDeconstructedCallback=self.__onDeconstructed)
        return

    def __canPurchaseUpgrade(self):
        return self.__currentModule.mayPurchaseUpgrade(self.__itemsCache.items)

    def __canGetMoreCurrency(self):
        return any((item.intCD != self.__currentModule.intCD or item.inventoryCount > 1 for item in self.__itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, REQ_CRITERIA.INVENTORY | REQ_CRITERIA.OPTIONAL_DEVICE.MODERNIZED).values()))

    def __initBalance(self):
        initBalance(self.viewModel.getBalance(), (Currency.EQUIP_COIN,), self.__itemsCache)

    def __setUpgradeCost(self):
        upgradeCurrency = self.__upgradePrice.getCurrency()
        with self.viewModel.prices.transaction() as model:
            model.setName(upgradeCurrency)
            model.setValue(self.__upgradePrice.get(upgradeCurrency))
            model.setIsEnough(self.__currentModule.mayPurchaseUpgrade(self.__itemsCache.items))

    def __onMoneyUpdated(self, _):
        self.__setUpgradeCost()
        self.__updateUpgradeStatus()
        self.__initBalance()

    def __getConfirmButtonTxtRes(self):
        return R.strings.dialogs.equipmentUpgrade.confirmButton() if self.__canPurchaseUpgrade() else R.strings.dialogs.equipmentUpgrade.getMoreCurrencyButton()

    def __optDevicesUpdated(self, _, diff):
        if diff is None or GUI_ITEM_TYPE.OPTIONALDEVICE not in diff:
            return
        else:
            self.__updateUpgradeStatus()
            return

    def __updateUpgradeStatus(self):
        canGetMoreCurrency = self.__canGetMoreCurrency()
        button = self.getButton(DialogButtons.SUBMIT)
        if button is not None:
            button.isDisabled = self.__isSubmitDisabled(canGetMoreCurrency)
            button.tooltipFactory = self.__getSubmitTooltipFactory()
        self.viewModel.setCanGetMoreCurrency(canGetMoreCurrency)
        return

    def __getSubmitTooltipFactory(self):
        body = backport.text(R.strings.dialogs.equipmentUpgrade.getMoreCurrencyButtonTooltip.body())
        return getSimpleTooltipFactory(body=body) if self.__isSubmitDisabled() else None

    def __isSubmitDisabled(self, canGetMoreCurrency=None):
        if canGetMoreCurrency is None:
            canGetMoreCurrency = self.__canGetMoreCurrency()
        return not (canGetMoreCurrency or self.__canPurchaseUpgrade())


def _fillDeviceInfo(modules, currentModule, viewModel):
    with viewModel.transaction() as model:
        model.setDeviceName(currentModule.name)
        model.setDeviceImg(currentModule.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_SMALL))
        model.setOverlayType(ItemHighlightTypes.MODERNIZED)
        kpiArray = model.getKpiItems()
        for i, _ in enumerate(modules):
            moduleKpis = modules[i].getKpi()
            moduleStage = Array()
            for j, _ in enumerate(moduleKpis):
                kpi = modules[i].getKpi()[j]
                kpiName = kpi.name
                kpiValue = kpi.value
                if any((module.getKpi()[j].name != kpiName for module in modules)):
                    _logger.error('KPI in basic and upgraded module dont have same order')
                    continue
                kpiModel = KpiItemModel()
                kpiModel.setName(kpiName)
                kpiModel.setValue(getKpiValueString(kpi, kpiValue, False))
                moduleStage.addViewModel(kpiModel)

            moduleStage.invalidate()
            kpiArray.addArray(moduleStage)

        kpiArray.invalidate()


def _getDowngradeInfo(result, device):
    if device.descriptor.downgradeInfo is None:
        return
    else:
        itemsCache = dependency.instance(IItemsCache)
        downgradedDevice = itemsCache.items.getItemByCD(device.descriptor.downgradeInfo.downgradedCompDescr)
        _getDowngradeInfo(result, downgradedDevice)
        result.append(downgradedDevice)
        return


def _getUpgradeInfo(result, device):
    if not device.isUpgradable:
        return
    itemsCache = dependency.instance(IItemsCache)
    upgradedDevice = itemsCache.items.getItemByCD(device.descriptor.upgradeInfo.upgradedCompDescr)
    result.append(upgradedDevice)
    _getUpgradeInfo(result, upgradedDevice)
