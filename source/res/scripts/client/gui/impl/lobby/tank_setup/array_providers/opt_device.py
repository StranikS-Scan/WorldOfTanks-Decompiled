# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/opt_device.py
from itertools import izip
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.common.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.bonus_value_model import BonusValueModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_device_slot_model import OptDeviceSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specialization_model import SpecializationModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider
from gui.impl.lobby.tank_setup.tank_setup_helper import getCategoriesMask
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.supply_slot_categories import SlotCategories
from shared_utils import first
from skeletons.gui.lobby_context import ILobbyContext

class BaseOptDeviceProvider(VehicleBaseArrayProvider):
    __slots__ = ()

    def getItemViewModel(self):
        return OptDeviceSlotModel()

    def createSlot(self, item, ctx):
        model = super(BaseOptDeviceProvider, self).createSlot(item, ctx)
        model.setName(backport.text(R.strings.artefacts.dyn(item.descriptor.tierlessName).name()))
        model.setImageName(item.descriptor.iconName)
        self._fillEffects(model, item)
        self._fillBonuses(model, item, ctx.slotID)
        self._fillSpecializations(model, item, ctx.slotID)
        self._fillBuyPrice(model, item)
        return model

    def updateSlot(self, model, item, ctx):
        super(BaseOptDeviceProvider, self).updateSlot(model, item, ctx)
        isInstalledOrMounted = item in self._getCurrentLayout() or item in self._getInstalledLayout()
        self._fillStatus(model, item, ctx.slotID, isInstalledOrMounted)
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
        return self._getEquipment().slots[appropriateSlotID].categories


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

    def updateSlot(self, model, item, ctx):
        super(DeluxeOptDeviceProvider, self).updateSlot(model, item, ctx)
        if self._lobbyCtx.getServerSettings().isTrophyDevicesEnabled():
            model.setIsUpgradable(item.isUpgradable)
        else:
            model.setIsUpgradable(False)

    @staticmethod
    def _fillHighlight(model, item):
        if item.isUpgradable:
            model.setOverlayType(ItemHighlightTypes.TROPHY_BASIC)
            model.setHighlightType(ItemHighlightTypes.TROPHY)
        elif item.isUpgraded:
            model.setOverlayType(ItemHighlightTypes.TROPHY_UPGRADED)
            model.setHighlightType(ItemHighlightTypes.TROPHY)
        else:
            model.setOverlayType(ItemHighlightTypes.EQUIPMENT_PLUS)
            model.setHighlightType(ItemHighlightTypes.EQUIPMENT_PLUS)

    def _getItemCriteria(self):
        invVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
        trophySet = set()
        for veh in invVehicles.itervalues():
            for optDevice in veh.optDevices.installed.getItems():
                if optDevice.isTrophy:
                    trophySet.add(optDevice.intCD)

        return REQ_CRITERIA.CUSTOM(lambda item: item.isTrophy and (item.isInInventory or item.intCD in trophySet)) ^ REQ_CRITERIA.OPTIONAL_DEVICE.DELUXE
