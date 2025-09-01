# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/equipments_presenter.py
from __future__ import absolute_import
from functools import partial
import typing
import SoundGroups
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.loadout.equipments.equipments_model import EquipmentsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.hangar.presenters.loadout_presenter_base import LoadoutPresenterBase, LoadoutEntityProvider
from gui.impl.lobby.tank_setup.array_providers.base import BaseVehSectionContext
from gui.impl.lobby.tank_setup.array_providers.opt_device import SimpleOptDeviceProvider, TrophyOptDeviceProvider, ModernisedOptDeviceProvider, DeluxeOptDeviceProvider
from gui.impl.lobby.tank_setup.configurations.opt_device import OptDeviceTabs
from gui.impl.lobby.tank_setup.interactors.opt_device import OptDeviceInteractor
from gui.impl.lobby.tank_setup.tank_setup_sounds import TankSetupSoundEvents
from gui.impl.lobby.tank_setup.tooltips.setup_tab_tooltip_view import SetupTabTooltipView
from gui.shared.event_dispatcher import showDeconstructionDeviceWindow
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IWotPlusController
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from gui.impl.lobby.tank_setup.interactors.base import InteractingItem

class EquipmentsPresenter(LoadoutPresenterBase[EquipmentsModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def __init__(self, interactingItem):
        super(EquipmentsPresenter, self).__init__(interactingItem, model=EquipmentsModel)
        self._sectionName = TankSetupConstants.OPT_DEVICES
        self._guiItemType = GUI_ITEM_TYPE.OPTIONALDEVICE

    def createSlotActions(self):
        actions = {BaseSetupModel.DEMOUNT_SLOT_ACTION: self.__onDemountItem,
         BaseSetupModel.DEMOUNT_SLOT_FROM_SETUP_ACTION: partial(self.__onDemountItem, everywhere=False),
         BaseSetupModel.DEMOUNT_SLOT_FROM_SETUPS_ACTION: self.__onDemountItem,
         BaseSetupModel.DESTROY_SLOT_ACTION: partial(self.__onDemountItem, isDestroy=True),
         BaseSetupModel.DECONSTRUCT_SLOT_ACTION: partial(self.__onDemountItem, isDestroy=True),
         BaseSetupModel.UPGRADE_SLOT_ACTION: self.__onUpgradeItem}
        actions.update(super(EquipmentsPresenter, self).createSlotActions())
        return actions

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tanksetup.tooltips.SetupTabTooltipView():
            name = event.getArgument('name', '')
            return SetupTabTooltipView(name)
        return super(EquipmentsPresenter, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return super(EquipmentsPresenter, self)._getEvents() + ((self.getViewModel().onGetMoreCurrency, self.__onGetMoreCurrency), (self.__wallet.onWalletStatusChanged, self._onCurrencyUpdate), (self.__wotPlusCtrl.onEnabledStatusChanged, self.__onWotPlusStatusChanged))

    def _createProvider(self, vehInteractingItem):
        self._provider = LoadoutEntityProvider(vehInteractingItem, OptDeviceInteractor, {OptDeviceTabs.SIMPLE: SimpleOptDeviceProvider,
         OptDeviceTabs.DELUXE: DeluxeOptDeviceProvider,
         OptDeviceTabs.TROPHY: TrophyOptDeviceProvider,
         OptDeviceTabs.MODERNIZED: ModernisedOptDeviceProvider})

    def _getCallbacks(self):
        return (('stats.{}'.format(Currency.EQUIP_COIN), self._onCurrencyUpdate),
         ('stats.{}'.format(Currency.GOLD), self._onCurrencyUpdate),
         ('stats.{}'.format(Currency.CREDITS), self._onCurrencyUpdate),
         ('stats.{}'.format(Currency.CRYSTAL), self._onCurrencyUpdate))

    def _updateModel(self, recreate=True):
        hasEquipmentSlots = self._vehInteractingItem.getItem().optDevices.layoutCapacity != 0
        if not hasEquipmentSlots or not self._provider:
            return
        dataProviders = self._provider.dataProviders
        simpleEquipmentsProvider = dataProviders[OptDeviceTabs.SIMPLE]
        deluxEquipmentsProvider = dataProviders[OptDeviceTabs.DELUXE]
        trophyEquipmentsProvider = dataProviders[OptDeviceTabs.TROPHY]
        modernizedEquipmentsProvider = dataProviders[OptDeviceTabs.MODERNIZED]
        with self.getViewModel().transaction() as equipmentsModel:
            equipCoinCount = int(self.__itemsCache.items.stats.actualMoney.get(Currency.EQUIP_COIN, 0))
            equipmentsModel.setEquipCoinCount(equipCoinCount)
            equipmentsModel.setHasModernizedEquipmentToDisassemble(bool(modernizedEquipmentsProvider.hasUnfitItems()) or bool(modernizedEquipmentsProvider.getItems()))
            if recreate:
                simpleEquipmentsProvider.fillArray(equipmentsModel.getSimpleEquipments(), BaseVehSectionContext(self._currentSlotIndex))
                deluxEquipmentsProvider.fillArray(equipmentsModel.getDeluxEquipments(), BaseVehSectionContext(self._currentSlotIndex))
                trophyEquipmentsProvider.fillArray(equipmentsModel.getTrophyEquipments(), BaseVehSectionContext(self._currentSlotIndex))
                modernizedEquipmentsProvider.fillArray(equipmentsModel.getModernizedEquipments(), BaseVehSectionContext(self._currentSlotIndex))
            else:
                simpleEquipmentsProvider.updateArray(equipmentsModel.getSimpleEquipments(), BaseVehSectionContext(self._currentSlotIndex))
                deluxEquipmentsProvider.updateArray(equipmentsModel.getDeluxEquipments(), BaseVehSectionContext(self._currentSlotIndex))
                trophyEquipmentsProvider.updateArray(equipmentsModel.getTrophyEquipments(), BaseVehSectionContext(self._currentSlotIndex))
                modernizedEquipmentsProvider.updateArray(equipmentsModel.getModernizedEquipments(), BaseVehSectionContext(self._currentSlotIndex))
        self._updateDealPanel()

    def _onRevertItem(self, args):
        SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.EQUIPMENT_DEMOUNT)
        super(EquipmentsPresenter, self)._onRevertItem(args)

    def __onGetMoreCurrency(self):
        showDeconstructionDeviceWindow(onDeconstructedCallback=self.__onDeconstructed)

    def __onWotPlusStatusChanged(self, _):
        self._updateModel()

    @wg_async
    def __onDemountItem(self, args, isDestroy=False, everywhere=True):
        itemIntCD = int(args.get('intCD'))
        result = yield wg_await(self._interactor.demountItem(itemIntCD, everywhere=everywhere, isDestroy=isDestroy))
        if result:
            if isDestroy:
                SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.EQUIPMENT_DESTROY)
            else:
                SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.EQUIPMENT_DEMOUNT_KIT)
        self._provider.updateDataProviderItems()
        self._updateModel()

    @wg_async
    def __onUpgradeItem(self, args):
        itemIntCD = int(args.get('intCD'))
        result = yield wg_await(self._asyncActionLock.tryAsyncCommandWithCallback(self._interactor.upgradeModule, itemIntCD, self.__onDeconstructed))
        if result:
            self._updateModel()

    def __onDeconstructed(self, deconstructedItemsOnVehicle, upgradItemPair):
        for item in deconstructedItemsOnVehicle:
            slotID = self._interactor.getCurrentLayout().index(item)
            if slotID is not None:
                self._revertItem(slotID)

        if upgradItemPair:
            upgradDevice = upgradItemPair[0]
            upgradedIntCD = upgradDevice.descriptor.upgradeInfo.upgradedCompDescr
            slotID = self._interactor.getCurrentLayout().index(upgradDevice)
            if slotID is not None:
                self._selectItem(slotID, upgradedIntCD)
        self._updateModel()
        return
