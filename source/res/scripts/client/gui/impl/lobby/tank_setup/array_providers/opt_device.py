# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/opt_device.py
import logging
from functools import partial
from itertools import izip, chain
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specialization_model import SpecializationModel
from gui.impl.gen.view_models.views.lobby.tank_setup.deconstruct_item_model import DeconstructItemModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_device_slot_model import OptDeviceSlotModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider, BaseArrayProvider
from gui.impl.lobby.tank_setup.tank_setup_helper import getCategoriesMask
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import ZERO_MONEY
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.supply_slot_categories import SlotCategories
from shared_utils import first
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.artefacts import OptionalDevice
    from gui.impl.lobby.tank_setup.array_providers.base import BaseVehSectionContext
_logger = logging.getLogger(__name__)

class ListTypes(object):
    STORAGE = 'storage'
    ON_VEHICLE = 'onVehicle'


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getInstalledSet(itemsCache=None):
    invVehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
    return set((optDevice for veh in invVehicles.itervalues() for optDevice in veh.optDevices.setupLayouts.getIntCDs()))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getModernizedInstalledList(itemsCache=None):
    invVehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
    return [ (veh.intCD, optDevice) for veh in invVehicles.itervalues() for optDevice in veh.optDevices.setupLayouts.getUniqueItems() if optDevice.isModernized ]


class ArrayOptDeviceProvider(BaseArrayProvider):

    def updateSlot(self, model, item, ctx):
        model.setDeviceID(item.intCD)
        model.setDeviceName(item.userName)
        model.setDeviceImage(R.images.gui.maps.icons.quests.bonuses.big.dyn(item.descriptor.iconName)())
        model.setDeviceLevel(item.level)
        model.setEquipCoinsForDeconstruction(item.getDeconstructPrice(self._itemsCache.items).price.equipCoin)
        self._fillBonuses(model, item)
        self._fillEffects(model, item)

    def _getItemTypeID(self):
        return (GUI_ITEM_TYPE.OPTIONALDEVICE,)

    def _getItemSortKey(self, item, ctx):
        return (item.level,
         not item.isUpgraded,
         not item.isUpgradable,
         item.getBuyPrice().price,
         item.userName)

    @staticmethod
    def _fillBonuses(model, item):
        bonuses = model.bonuses.getItems()
        for kpi in item.getKpi():
            bonusModel = BonusModel()
            bonusModel.setLocaleName(kpi.name)
            values = bonusModel.getValues()
            value = BonusValueModel()
            value.setValue(kpi.value)
            value.setValueKey(kpi.name)
            value.setValueType(kpi.type)
            values.addViewModel(value)
            bonuses.addViewModel(bonusModel)

        bonuses.invalidate()

    @staticmethod
    def _fillEffects(model, item):
        itemR = R.strings.artefacts.dyn(item.descriptor.groupName)
        effectR = first(itemR.dyn('effect').values(), R.invalid)
        model.setEffect(effectR())

    def _fillVehicle(self, model, vehCD):
        vehicle = self._itemsCache.items.getItemByCD(vehCD)
        if not vehicle:
            _logger.warning('There is invalid vehicle compact descriptor %s', vehCD)
            return
        model.vehicleInfo.setVehicleName(vehicle.descriptor.type.shortUserString)
        model.vehicleInfo.setVehicleType(vehicle.type)
        model.vehicleInfo.setVehicleLvl(vehicle.level)
        model.vehicleInfo.setVehicleID(vehCD)
        model.vehicleInfo.setIsPremiumIGR(vehicle.isPremiumIGR)


class DeconstructOptDeviceStorageProvider(ArrayOptDeviceProvider):

    def getLimit(self, item, upgradedPair):
        return item.inventoryCount - 1 if upgradedPair and not upgradedPair[1] and upgradedPair[0] == item else item.inventoryCount

    def getItemViewModel(self):
        return DeconstructItemModel()

    def updateSlot(self, model, item, ctx):
        super(DeconstructOptDeviceStorageProvider, self).updateSlot(model, item, ctx)
        self._fillStorageCount(model, item, ctx)
        self._fillSelectedCount(model, item, ctx)

    def _fillSelectedCount(self, model, item, ctx):
        storageSpecs = ctx.cart.storage
        selectedCount = storageSpecs[item.intCD].count if item.intCD in storageSpecs else 0
        model.setSelectedCount(selectedCount)

    def _fillStorageCount(self, model, item, ctx):
        upgradedPair = ctx.upgradedPair
        limit = self.getLimit(item, upgradedPair)
        model.setStorageCount(limit)

    def _getCriteria(self):
        return REQ_CRITERIA.CUSTOM(lambda item: item.isModernized and item.isInInventory)

    def getTotalPrice(self, ctx):
        storageSpecs = ctx.cart.storage.values()
        total = ZERO_MONEY
        for itemSpec in storageSpecs:
            item = self._itemsCache.items.getItemByCD(itemSpec.intCD)
            total += item.getDeconstructPrice(self._itemsCache.items).price * itemSpec.count

        return total

    def getFilterFunc(self, upgradedPair):
        if upgradedPair:
            upgradedItem, vehCD = upgradedPair
            if not vehCD:
                return lambda items: (item for item in items if item != upgradedItem or item.inventoryCount > 1)
        return None


class DeconstructOptDeviceOnVehicleProvider(ArrayOptDeviceProvider):

    def getItemsList(self):
        return _getModernizedInstalledList()

    def getItemViewModel(self):
        return DeconstructItemModel()

    def updateSlot(self, model, itemPair, ctx):
        vehCD, item = itemPair
        super(DeconstructOptDeviceOnVehicleProvider, self).updateSlot(model, item, ctx)
        self._fillVehicle(model, vehCD)
        self._fillSelectedCount(model, itemPair, ctx)

    def _fillSelectedCount(self, model, itemPair, ctx):
        vehSpecsDict = ctx.cart.onVehicle
        selectedCount = 1 if any((itemPair == (vehCD, item) for vehCD, items in vehSpecsDict.items() for item in items)) else 0
        model.setSelectedCount(selectedCount)

    def getTotalPrice(self, ctx):
        vehSpecs = chain(*ctx.cart.onVehicle.values())
        total = ZERO_MONEY
        for itemSpec in vehSpecs:
            item = self._itemsCache.items.getItemByCD(itemSpec.intCD)
            total += item.getDeconstructPrice(self._itemsCache.items).price

        return total

    def getFilterFunc(self, upgradedPair):
        if upgradedPair:
            upgradedItem, vehCD = upgradedPair
            if vehCD:
                return lambda items: (item for item in items if not (item[1] == upgradedItem and vehCD == item[0]))
        return None

    def _getItemSortKey(self, item, ctx):
        _, item = item
        return super(DeconstructOptDeviceOnVehicleProvider, self)._getItemSortKey(item, ctx)


class BaseOptDeviceProvider(VehicleBaseArrayProvider):
    _wotPlusController = dependency.descriptor(IWotPlusController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def getItemViewModel(self):
        return OptDeviceSlotModel()

    def _fillWotPlusStatus(self, model, item):
        model.setIsFreeToDemount(self._wotPlusController.isFreeToDemount(item))
        if item.isModernized:
            model.setDestroyTooltipBodyPath('destroy_modernized')
            return
        if item.isRegular and self._lobbyContext.getServerSettings().isFreeEquipmentDemountingEnabled():
            model.setDestroyTooltipBodyPath('destroy_without_wotplus_demount')
            return
        model.setDestroyTooltipBodyPath('destroy')

    def createSlot(self, item, ctx):
        model = super(BaseOptDeviceProvider, self).createSlot(item, ctx)
        model.setName(backport.text(R.strings.artefacts.dyn(item.descriptor.tierlessName).name()))
        model.setImageName(item.descriptor.iconName)
        self._fillEffects(model, item)
        self._fillBonuses(model, item, ctx.slotID)
        self._fillSpecializations(model, item, ctx.slotID)
        self._fillBuyPrice(model, item)
        self._fillWotPlusStatus(model, item)
        return model

    def updateSlot(self, model, item, ctx):
        super(BaseOptDeviceProvider, self).updateSlot(model, item, ctx)
        self._fillStatus(model, item, ctx.slotID)
        self._fillWotPlusStatus(model, item)
        if not model.getIsDisabled():
            isInstalledOrMounted = item in self._getCurrentLayout() or self._getSetupLayout().containsIntCD(item.intCD)
            self._fillBuyStatus(model, item, isInstalledOrMounted)
        appropriateCategories = self.__getAppropriateCategories(item, ctx.slotID)
        activeCategories = appropriateCategories & item.descriptor.categories
        for bonusModel, kpi in izip(model.bonuses.getItems(), item.getKpi(self._getVehicle())):
            value = bonusModel.getValues()[0]
            if activeCategories and kpi.specValue is not None:
                value.setValue(kpi.specValue)
            value.setValue(kpi.value)

        model.setActiveSpecsMask(getCategoriesMask(activeCategories))
        for specializationModel in model.specializations.getSpecializations():
            specializationModel.setIsCorrect(specializationModel.getName() in appropriateCategories)

        return

    def _fillSpecializations(self, model, item, slotID):
        specializations = model.specializations.getSpecializations()
        appropriateCategories = self.__getAppropriateCategories(item, slotID)
        for category in SlotCategories.ORDER:
            if category not in item.descriptor.categories:
                continue
            specialization = SpecializationModel()
            specialization.setName(category)
            specialization.setIsCorrect(category in appropriateCategories)
            specializations.addViewModel(specialization)

        specializations.invalidate()

    def _fillBonuses(self, model, item, slotID):
        isSpec = bool(self.__getAppropriateCategories(item, slotID) & item.descriptor.categories)
        bonuses = model.bonuses.getItems()
        for kpi in item.getKpi(self._getVehicle()):
            bonusModel = BonusModel()
            bonusModel.setLocaleName(kpi.name)
            values = bonusModel.getValues()
            value = BonusValueModel()
            value.setValue(kpi.specValue if isSpec and kpi.specValue is not None else kpi.value)
            value.setValueKey(kpi.name)
            value.setValueType(kpi.type)
            values.addViewModel(value)
            bonuses.addViewModel(bonusModel)

        bonuses.invalidate()
        return

    @staticmethod
    def _fillEffects(model, item):
        itemR = R.strings.artefacts.dyn(item.descriptor.groupName)
        effectR = first(itemR.dyn('effect').values(), R.invalid)
        model.setEffect(effectR())

    @classmethod
    def _getItemTypeID(cls):
        return (GUI_ITEM_TYPE.OPTIONALDEVICE,)

    def _getEquipment(self):
        return self._getVehicle().optDevices

    def _getItemSortKey(self, item, ctx):
        return (not item.isUpgraded,
         not item.isUpgradable,
         [ category not in item.descriptor.categories for category in SlotCategories.ORDER ],
         item.getBuyPrice().price,
         item.userName)

    def __getAppropriateCategories(self, item, slotID):
        installedSlotID = self._getEquipment().layout.index(item)
        appropriateSlotID = installedSlotID if installedSlotID is not None else slotID
        return self._getEquipment().getSlot(appropriateSlotID).item.categories


class SimpleOptDeviceProvider(BaseOptDeviceProvider):
    __slots__ = ()

    def _getItemCriteria(self):
        return REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | ~REQ_CRITERIA.HIDDEN ^ REQ_CRITERIA.INVENTORY


class DeluxeOptDeviceProvider(BaseOptDeviceProvider):
    _lobbyCtx = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def createSlot(self, item, ctx):
        model = super(DeluxeOptDeviceProvider, self).createSlot(item, ctx)
        self._fillHighlight(model, item)
        model.setIsTrophy(item.isTrophy)
        return model

    def _getItemSortKey(self, item, ctx):
        return (item.getBuyPrice().price, item.userName)

    @staticmethod
    def _fillHighlight(model, item):
        model.setOverlayType(ItemHighlightTypes.EQUIPMENT_PLUS)
        model.setHighlightType(ItemHighlightTypes.EQUIPMENT_PLUS)

    def _getItemCriteria(self):
        installSet = _getInstalledSet()
        return REQ_CRITERIA.CUSTOM(lambda item: item.isDeluxe and (not item.isHidden or item.isInInventory or item.intCD in installSet))


class ModernisedOptDeviceProvider(DeluxeOptDeviceProvider):
    __slots__ = ()

    def createSlot(self, item, ctx):
        model = super(ModernisedOptDeviceProvider, self).createSlot(item, ctx)
        model.setIsModernized(item.isModernized)
        model.setLevel(item.level)
        return model

    def updateSlot(self, model, item, ctx):
        super(ModernisedOptDeviceProvider, self).updateSlot(model, item, ctx)
        model.setIsUpgradable(item.isUpgradable)

    @staticmethod
    def _fillHighlight(model, item):
        model.setOverlayType(ItemHighlightTypes.MODERNIZED)
        model.setHighlightType(ItemHighlightTypes.MODERNIZED)

    def _getItemSortKey(self, item, ctx):
        return (-item.level, item.userName)

    def _sortItems(self, items, ctx):
        items.sort(key=partial(self._getItemSortKey, ctx=ctx))

    def _getItemCriteria(self):
        installSet = _getInstalledSet()
        return REQ_CRITERIA.CUSTOM(lambda item: item.isModernized and (item.isInInventory or item.intCD in installSet))


class TrophyOptDeviceProvider(DeluxeOptDeviceProvider):

    def _getItemSortKey(self, item, ctx):
        return (-item.level,
         item.userName,
         not item.isUpgraded,
         not item.isUpgradable)

    def _sortItems(self, items, ctx):
        items.sort(key=partial(self._getItemSortKey, ctx=ctx))

    @staticmethod
    def _fillHighlight(model, item):
        if item.isUpgradable:
            model.setOverlayType(ItemHighlightTypes.TROPHY_BASIC)
            model.setHighlightType(ItemHighlightTypes.TROPHY)
        elif item.isUpgraded:
            model.setOverlayType(ItemHighlightTypes.TROPHY_UPGRADED)
            model.setHighlightType(ItemHighlightTypes.TROPHY)

    def updateSlot(self, model, item, ctx):
        super(TrophyOptDeviceProvider, self).updateSlot(model, item, ctx)
        if self._lobbyCtx.getServerSettings().isTrophyDevicesEnabled():
            model.setIsUpgradable(item.isUpgradable)
        else:
            model.setIsUpgradable(False)

    def _getItemCriteria(self):
        installSet = _getInstalledSet()
        return REQ_CRITERIA.CUSTOM(lambda item: item.isTrophy and (item.isInInventory or item.intCD in installSet))

    def _isInstallAllowed(self, item):
        return self._lobbyCtx.getServerSettings().isTrophyDevicesEnabled() and item.isTrophy and self._getSetupLayout().isInSetup(item)
