# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/cards/opt_devices_card.py
from typing import TYPE_CHECKING
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.opt_devices_preset_model import OptDevicesPresetModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.opt_devices_preset_slot_model import OptDevicesPresetSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specialization_model import SpecializationModel
from gui.impl.lobby.easy_tank_equip.cards.base_card import BasePreset, BaseCard
from gui.impl.lobby.tank_setup.tank_setup_helper import getCategoriesMask
if TYPE_CHECKING:
    from typing import Optional
    from gui.impl.lobby.easy_tank_equip.data_providers.opt_devices_data_provider import OptionalDevicesPresetInfo, OptDevicesPresetSlotInfo
    from gui.shared.gui_items.artefacts import OptionalDevice
    from gui.shared.gui_items.vehicle_equipment import OptDeviceSlotData
    from gui.shared.money import Money

class OptDevicesCard(BaseCard):

    def _getPreset(self):
        return OptDevicesPreset


class OptDevicesPreset(BasePreset):

    @classmethod
    def getPresetModel(cls):
        return OptDevicesPresetModel()

    @classmethod
    def fillPresetModel(cls, model, presetInfo, balance=None):
        super(OptDevicesPreset, cls).fillPresetModel(model, presetInfo, balance)
        model.setType(presetInfo.presetType)
        model.setDemountKitsCount(presetInfo.demountKits)
        cls.__fillPresetItemsModels(model, presetInfo)

    @classmethod
    def __fillPresetItemsModels(cls, model, presetInfo):
        presetItems = model.getItems()
        presetItems.clear()
        for item in presetInfo.items:
            presetSlotModel = OptDevicesPresetSlotModel()
            cls.__fillPresetSlotModel(presetSlotModel, item)
            presetItems.addViewModel(presetSlotModel)

        presetItems.invalidate()

    @classmethod
    def __fillPresetSlotModel(cls, model, presetSlotInfo):
        model.setIntCD(presetSlotInfo.optDevice.intCD)
        model.setId(presetSlotInfo.slotIdx)
        model.setIconName(presetSlotInfo.optDevice.descriptor.iconName)
        model.setIsIncompatible(False)
        model.setImageSource(R.images.gui.maps.icons.artefact.dyn(presetSlotInfo.optDevice.descriptor.iconName)())
        cls.fillSlotInfoModel(model.info, presetSlotInfo.info)
        cls.__updateOverlayAspects(model, presetSlotInfo.optDevice)
        cls.__updateSpecializations(model, presetSlotInfo.optDevice, presetSlotInfo.slotData)

    @classmethod
    def __updateOverlayAspects(cls, model, presetSlotOptDevice):
        model.setLevel(presetSlotOptDevice.level)
        if presetSlotOptDevice.isDeluxe:
            model.setOverlayType(ItemHighlightTypes.EQUIPMENT_PLUS)
        elif presetSlotOptDevice.isModernized:
            model.setOverlayType(ItemHighlightTypes.MODERNIZED)
        elif presetSlotOptDevice.isUpgradable:
            model.setOverlayType(ItemHighlightTypes.TROPHY_BASIC)
        elif presetSlotOptDevice.isUpgraded:
            model.setOverlayType(ItemHighlightTypes.TROPHY_UPGRADED)
        else:
            model.setOverlayType(ItemHighlightTypes.EMPTY)

    @classmethod
    def __updateSpecializations(cls, model, presetSlotOptDevice, slotData):
        optDeviceItem, isDynamic = slotData
        model.specializations.setIsDynamic(isDynamic)
        itemCategories = presetSlotOptDevice.descriptor.categories
        model.setActiveSpecsMask(getCategoriesMask(itemCategories & optDeviceItem.categories))
        isSpecializationClickable = False
        specializations = model.specializations.getSpecializations()
        categories = optDeviceItem.categories
        if len(specializations) != len(categories):
            specializations.clear()
            for category in categories:
                specialization = SpecializationModel()
                specialization.setName(category)
                specialization.setIsClickable(isSpecializationClickable)
                specialization.setIsCorrect(category in itemCategories)
                specializations.addViewModel(specialization)

        else:
            for categoryIdx, category in enumerate(categories):
                specialization = specializations[categoryIdx]
                specialization.setName(category)
                specialization.setIsClickable(isSpecializationClickable)
                specialization.setIsCorrect(category in itemCategories)

        specializations.invalidate()
