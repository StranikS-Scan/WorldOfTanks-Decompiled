# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/shells_presenter.py
from __future__ import absolute_import
import typing
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen.view_models.views.lobby.loadout.shells.shell_model import ShellModel
from gui.impl.gen.view_models.views.lobby.loadout.shells.shells_model import ShellsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_specification_model import ShellSpecificationModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.hangar.presenters.loadout_presenter_base import LoadoutPresenterBase, LoadoutEntityProvider
from gui.impl.lobby.tank_setup.array_providers.shell import ShellProvider
from gui.impl.lobby.tank_setup.configurations.shell import ShellTabs, ShellDealPanel
from gui.impl.lobby.tank_setup.interactors.shell import ShellInteractor
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared import sound_helpers
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import isAutoReloadGun, params_helper, isTwinGun
from gui.shared.items_parameters.formatters import formatParameter, MEASURE_UNITS
from helpers import i18n, dependency
from post_progression_common import TankSetupGroupsId
from shared_utils import first
from skeletons.gui.game_control import IWalletController, IExchangeRatesWithDiscountsProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.vehicle_modules import Shell
    from gui.impl.lobby.tank_setup.interactors.base import InteractingItem
_SHELLS_INFO_PARAMS = ('avgDamage', 'avgDamagePerSecond', 'avgPiercingPower', 'shotSpeed', 'explosionRadius', 'stunDurationList')

class ShellsPresenter(LoadoutPresenterBase[ShellsModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __exchangeRates = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def __init__(self, interactingItem):
        super(ShellsPresenter, self).__init__(interactingItem, model=ShellsModel)
        self._sectionName = TankSetupConstants.SHELLS
        self._guiItemType = GUI_ITEM_TYPE.SHELL

    def _getEvents(self):
        return super(ShellsPresenter, self)._getEvents() + ((self.getViewModel().onShellUpdate, self.__onShellUpdate), (self.__wallet.onWalletStatusChanged, self._onCurrencyUpdate), (self.__exchangeRates.goldToCredits.onUpdated, self._onCurrencyUpdate))

    @property
    def isShellState(self):
        from gui.impl.lobby.hangar.states import ShellsLoadoutState
        lsm = getLobbyStateMachine()
        return lsm.getStateByCls(ShellsLoadoutState).isEntered()

    def _getDealPanel(self):
        return ShellDealPanel

    def _onSlotAction(self, args):
        autoloadEnabled = args.get('autoloadEnabled')
        self._setHasChanges(autoloadEnabled)
        super(ShellsPresenter, self)._onSlotAction(args)

    def _setHasChanges(self, autoloadEnabled=None):
        if autoloadEnabled is None:
            autoloadEnabled = self._interactor.getAutoRenewal().getValue()
        hasChanges = self._interactor.hasChanged() or self._interactor.getAutoRenewal().getValue() != autoloadEnabled
        self.getViewModel().setHasChanges(hasChanges)
        return

    def _onSwapSlots(self, actionType, args):
        leftID = int(args.get('leftID'))
        rightID = int(args.get('rightID'))
        self._swapSlots(leftID, rightID, actionType)
        self._updateModel()

    def _createProvider(self, vehInteractingItem):
        self._provider = LoadoutEntityProvider(vehInteractingItem, ShellInteractor, {ShellTabs.SHELLS: ShellProvider})

    def _updateModel(self, recreate=True):
        if not g_currentVehicle.isPresent() or not self._provider:
            return
        else:
            currentVehicle = self._vehInteractingItem.getItem()
            currentSetup = currentVehicle.shells.installed
            ammoMaxSize = currentVehicle.ammoMaxSize
            interactorShells = self._interactor.getCurrentLayout()
            if not self.isShellState:
                interactorShells = self._interactor.getInstalledLayout()
            installedCount = sum((shell.count for shell in interactorShells))
            gun = currentVehicle.gun.descriptor
            clip = self.__setupClipCount(gun)
            with self.getViewModel().transaction() as model:
                model.setAmmoMaxSize(ammoMaxSize)
                model.setInstalledCount(installedCount)
                model.setClip(clip)
                model.setAutoloadEnabled(self._interactor.getAutoRenewal().getLocalValue())
                shells = model.getShells()
                shells.clear()
                for shell in interactorShells:
                    if shell is not None:
                        installedShell = first((s for s in currentSetup if s.intCD == shell.intCD))
                        shellItem = self.__createShellItem(shell, installedShell)
                        self.__updateShellItem(shells, shellItem)

                shells.invalidate()
            self._updateDealPanel()
            return

    def __setupClipCount(self, gun):
        if isAutoReloadGun(gun):
            return 1
        return 2 if isTwinGun(gun) else gun.clip[0]

    def __updateShellItem(self, shellModels, shellModel):
        for index, item in enumerate(shellModels):
            if item.getIntCD() == shellModel.getIntCD():
                shellModels.setViewModel(index, item)
                return

        shellModels.addViewModel(shellModel)

    def __onShellUpdate(self, args):
        intCD = int(args.get('intCD'))
        newCount = int(args.get('newCount'))
        oldCount = self._interactor.getCurrentLayout()[self._interactor.getCurrentShellSlotID(intCD)].count
        currentVehicle = self._vehInteractingItem.getItem()
        gun = currentVehicle.gun.descriptor
        isCassetteClip = gun.clip[0] > 1
        clip = self.__setupClipCount(gun)
        if isCassetteClip or isTwinGun(gun):
            if oldCount % clip != 0:
                if newCount > oldCount:
                    newCount = (oldCount + clip - 1) // clip * clip
                elif newCount < oldCount:
                    newCount = oldCount // clip * clip
        totalCount = oldCount + (self.getViewModel().getAmmoMaxSize() - self.getViewModel().getInstalledCount())
        self._interactor.changeShell(intCD, newCount)
        if totalCount != 0:
            sound_helpers.playSliderUpdateSound(oldCount, newCount, totalCount)
        self._setHasChanges()
        self._updateModel()

    def __createShellItem(self, shell, installedShell):
        vehicle = g_currentVehicle.item
        delta = shell.count - installedShell.count if installedShell is not None else 0
        item = ShellModel()
        inTankCount = 0
        for setupShell in vehicle.shells.setupLayouts:
            if setupShell == shell:
                inTankCount = max(inTankCount, setupShell.count)

        boughtCount = shell.inventoryCount + inTankCount
        buyCount = max(shell.count - boughtCount, 0)
        inTankCount = max(shell.count, self._vehInteractingItem.getItem().shells.setupLayouts.ammoLoadedInOtherSetups(shell.intCD))
        item.setInDepotCount(max(boughtCount - inTankCount, 0))
        if vehicle.isSetupSwitchActive(TankSetupGroupsId.EQUIPMENT_AND_SHELLS):
            item.setItemsCount(inTankCount)
        else:
            item.setItemsCount(-1)
        item.setDelta(delta)
        item.setValue(shell.count - delta)
        item.setCount(shell.count)
        item.setType(shell.descriptor.iconName)
        item.setKind(shell.descriptor.kind)
        item.setIntCD(shell.intCD)
        item.setItemInstalledSetupIdx(vehicle.shells.setupLayouts.layoutIndex)
        item.setIsMounted(shell in self._interactor.getInstalledLayout())
        item.setIsMountedMoreThanOne(vehicle.shells.installed.getIntCDs().count(shell.intCD))
        properties = item.getPropertiesList()
        for paramName in _SHELLS_INFO_PARAMS:
            properties.addViewModel(self.__createShellSpecificationModel(shell, paramName))

        self.__fillShellItemPriceModel(shell.buyPrices.itemPrice.price, item.itemPrice)
        BuyPriceModelBuilder.clearPriceModel(item.price)
        BuyPriceModelBuilder.fillPriceModelByItemPrice(item.price, shell.getBuyPrice(), checkBalanceAvailability=True)
        item.setBuyCount(buyCount)
        BuyPriceModelBuilder.clearPriceModel(item.totalPrice)
        if buyCount:
            BuyPriceModelBuilder.fillPriceModelByItemPrice(item.totalPrice, shell.getBuyPrice() * buyCount, checkBalanceAvailability=True)
        return item

    def __createShellSpecificationModel(self, shell, paramName):
        specificationModel = ShellSpecificationModel()
        specificationModel.setParamName(paramName)
        specificationModel.setMetricValue(i18n.makeString(MEASURE_UNITS.get(paramName, '')))
        shellParam = params_helper.getParameters(shell, g_currentVehicle.item.descriptor)
        specificationModel.setValue(formatParameter(paramName, shellParam.get(paramName)) or '')
        return specificationModel

    def __fillShellItemPriceModel(self, shellItemPrice, itemPriceModel):
        with itemPriceModel.transaction() as model:
            currency = shellItemPrice.getCurrency()
            value = shellItemPrice.get(currency)
            model.setName(currency)
            model.setValue(value)
            money = self.__itemsCache.items.stats.money
            model.setIsEnough(money.get(currency, 0) >= value)
