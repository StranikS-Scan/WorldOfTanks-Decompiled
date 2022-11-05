# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/deconstruction_device_view.py
import logging
from collections import namedtuple
from copy import deepcopy
from itertools import chain
import adisp
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.deconstruction_device_view_model import DeconstructionDeviceViewModel
from gui.impl.lobby.tank_setup.array_providers.opt_device import DeconstructOptDeviceOnVehicleProvider, DeconstructOptDeviceStorageProvider
from gui.impl.lobby.tank_setup.backports.tooltips import OptDeviceTooltipBuilder
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.items_actions.actions import ItemSellSpec, ItemDeconstructSpec
from gui.shared.money import Currency
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
ItemDeconstructContext = namedtuple('ItemDeconstructContext', ('cart', 'upgradedPair'))
Cart = namedtuple('Cart', ('onVehicle', 'storage'))

class DeconstructionDeviceView(ViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_upgradedItemPair', '_storageProvider', '_onVehicleProvider', '_cart', '__deconstructedCallback')

    def __init__(self, upgradedItemPair=None, onDeconstructedCallback=None):
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.DeconstructionDeviceView(), model=DeconstructionDeviceViewModel())
        self._upgradedItemPair = upgradedItemPair
        self._storageProvider = DeconstructOptDeviceStorageProvider()
        self._onVehicleProvider = DeconstructOptDeviceOnVehicleProvider()
        self._cart = Cart({}, {})
        self.__deconstructedCallback = onDeconstructedCallback
        super(DeconstructionDeviceView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DeconstructionDeviceView, self).getViewModel()

    def createPopOverContent(self, event):
        return BackportPopOverContent(createPopOverData(VIEW_ALIAS.VEHICLES_FILTER_POPOVER))

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self._getBackportTooltipData(event)
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(DeconstructionDeviceView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(DeconstructionDeviceView, self)._onLoading()
        self._updateView(True)

    def _initialize(self, *args, **kwargs):
        super(DeconstructionDeviceView, self)._initialize()
        selectableVM = self.viewModel
        selectableVM.onOkClick += self._onOkClick
        selectableVM.onCloseClick += self._onCloseClick
        selectableVM.onModuleAdd += self._onModuleAdd
        selectableVM.onModuleReduce += self._onModuleReduce
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)

    def _finalize(self):
        selectableVM = self.viewModel
        selectableVM.onOkClick -= self._onOkClick
        selectableVM.onCloseClick -= self._onCloseClick
        selectableVM.onModuleAdd -= self._onModuleAdd
        selectableVM.onModuleReduce -= self._onModuleReduce
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._cart = None
        self._storageProvider = None
        self._onVehicleProvider = None
        super(DeconstructionDeviceView, self)._finalize()
        return

    def _updateView(self, fullUpdate=False):
        ctx = ItemDeconstructContext(deepcopy(self._cart), self._upgradedItemPair)
        self._updateSlots(ctx, fullUpdate)
        self._updateCounters(ctx)
        self._fillVehicle()
        self._fillUpgradedItem()

    def _fillUpgradedItem(self):
        if self._upgradedItemPair:
            upgradedItem, _ = self._upgradedItemPair
            ctx = ItemDeconstructContext(deepcopy(self._cart), self._upgradedItemPair)
            with self.viewModel.transaction() as tx:
                tx.setDeviceForUpgradeName(upgradedItem.userName)
                upgradePrice = upgradedItem.getUpgradePrice(self.itemsCache.items).price.equipCoin
                coinsOnAccount = self.itemsCache.items.stats.actualMoney.get(Currency.EQUIP_COIN, 0)
                totalIncome = self._storageProvider.getTotalPrice(ctx) + self._onVehicleProvider.getTotalPrice(ctx)
                neededCoins = max(upgradePrice - (coinsOnAccount + totalIncome.equipCoin), 0)
                tx.setEquipCoinsNeededForUpgrade(neededCoins)

    def _fillVehicle(self):
        with self.viewModel.transaction() as tx:
            vehicle = g_currentVehicle.item
            if not vehicle:
                return
            tx.currentVehicleInfo.setVehicleName(vehicle.shortUserName)
            tx.currentVehicleInfo.setVehicleType(vehicle.type)
            tx.currentVehicleInfo.setVehicleLvl(vehicle.level)

    def _updateSlots(self, ctx=None, fullUpdate=True, updateData=True):
        if self._storageProvider is None or self._onVehicleProvider is None:
            return
        else:
            if ctx is None:
                ctx = ItemDeconstructContext(deepcopy(self._cart), self._upgradedItemPair)
            if updateData:
                self._storageProvider.updateItems()
                self._onVehicleProvider.updateItems()
            if fullUpdate:
                self._storageProvider.fillArray(self.viewModel.getModulesInStorage(), ctx, self._storageProvider.getFilterFunc(self._upgradedItemPair))
                self._onVehicleProvider.fillArray(self.viewModel.getModulesOnVehicles(), ctx, self._onVehicleProvider.getFilterFunc(self._upgradedItemPair))
                self._updateItemByFilter()
            else:
                self._storageProvider.updateArray(self.viewModel.getModulesInStorage(), ctx)
                self._onVehicleProvider.updateArray(self.viewModel.getModulesOnVehicles(), ctx)
                self._updateItemByFilter()
            self._updateCounters(ctx)
            return

    def _updateCounters(self, ctx):
        totalIncome = self._storageProvider.getTotalPrice(ctx) + self._onVehicleProvider.getTotalPrice(ctx)
        coinsOnAccount = self.itemsCache.items.stats.actualMoney.get(Currency.EQUIP_COIN, 0)
        self.viewModel.setEquipCoinsForDeconstruction(int(totalIncome.equipCoin))
        self.viewModel.setEquipCoinsOnAccount(int(coinsOnAccount))

    def _updateItemByFilter(self):
        pass

    def __fillModules(self):
        self._updateSlots()

    def _onOkClick(self):
        self.__makeAction()

    def _onCloseClick(self):
        self.destroyWindow()

    def _onModuleAdd(self, event):
        intCD = int(event.get('deviceID', -1))
        vehCD = int(event.get('vehicleID', 0))
        if intCD == -1:
            return
        itemSellSpecs = self._cart.storage
        vehiclesLists = self._cart.onVehicle

        def getLimit(intCD, upgradedPair):
            item = self.itemsCache.items.getItemByCD(intCD)
            return item.inventoryCount - 1 if upgradedPair and not upgradedPair[1] and upgradedPair[0] == item else item.inventoryCount

        if not vehCD:
            spec = ItemSellSpec(GUI_ITEM_TYPE.OPTIONALDEVICE, intCD, 1)
            if intCD in itemSellSpecs:
                limitCount = getLimit(intCD, self._upgradedItemPair)
                prevSpec = itemSellSpecs[intCD]
                if prevSpec.count >= limitCount:
                    _logger.warning('Wrong event, intCD itemSell count equal to limit')
                spec = prevSpec._replace(count=prevSpec.count + 1)
            itemSellSpecs.update({intCD: spec})
        else:
            vehicleList = vehiclesLists.setdefault(vehCD, [])
            if not any((spec.intCD == intCD for spec in vehicleList)):
                vehicleList.append(ItemDeconstructSpec(GUI_ITEM_TYPE.OPTIONALDEVICE, intCD, vehCD))
            else:
                _logger.warning('Wrong event, intCD already in vehicleList')
        self._updateSlots()

    def _onModuleReduce(self, event):
        intCD = int(event.get('deviceID', -1))
        vehCD = int(event.get('vehicleID', 0))
        if intCD == -1:
            return
        itemSellSpecs = self._cart.storage
        vehiclesLists = self._cart.onVehicle
        if not vehCD:
            if intCD in itemSellSpecs:
                prevSpec = itemSellSpecs[intCD]
                if prevSpec.count == 1:
                    itemSellSpecs.pop(intCD)
                else:
                    spec = prevSpec._replace(count=prevSpec.count - 1)
                    itemSellSpecs.update({intCD: spec})
            else:
                _logger.warning('Wrong event, dont have intCD in cart')
        elif vehCD in vehiclesLists:
            vehicleList = vehiclesLists[vehCD]
            for spec in vehicleList:
                if spec.intCD == intCD:
                    vehicleList.remove(spec)
                    break
            else:
                _logger.warning('Wrong event, intCD not in vehicleList')

        else:
            _logger.warning('Wrong event, dont have vehicleCD in cart')
        self._updateSlots()

    @adisp.adisp_process
    def __makeAction(self, callback=None):
        itemSellSpecs = self._cart.storage.values()
        itemDeconstractSpecs = list(chain(*self._cart.onVehicle.values()))
        if not itemSellSpecs and not itemDeconstractSpecs:
            return
        else:
            ctx = ItemDeconstructContext(deepcopy(self._cart), self._upgradedItemPair)
            action = ItemsActionsFactory.getAction(ItemsActionsFactory.DECONSTRUCT_MULT_OPT_DEVICE, ctx)
            result = yield ItemsActionsFactory.asyncDoAction(action)
            if result:
                if self.__deconstructedCallback is not None:
                    self.__deconstructedCallback(itemDeconstractSpecs, self._upgradedItemPair)
                self.destroyWindow()
            return

    def _getBackportTooltipData(self, event):
        intCD = event.getArgument('deviceID')
        if intCD:
            tooltipBuilder = OptDeviceTooltipBuilder
            return tooltipBuilder.getTooltipData(None, 0, int(intCD))
        else:
            return None

    def __onMoneyUpdated(self, _):
        ctx = ItemDeconstructContext(deepcopy(self._cart), self._upgradedItemPair)
        self._updateCounters(ctx)
        self._fillUpgradedItem()


class DeconstructionDeviceWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, upgradedPair=None, parent=None, onDeconstructedCallback=None):
        super(DeconstructionDeviceWindow, self).__init__(WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=DeconstructionDeviceView(upgradedPair, onDeconstructedCallback), parent=parent)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.WINDOW)

    def _finalize(self):
        self.__blur.fini()
        super(DeconstructionDeviceWindow, self)._finalize()
