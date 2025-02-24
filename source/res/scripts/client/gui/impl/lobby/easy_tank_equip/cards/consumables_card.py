# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/cards/consumables_card.py
import typing
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.consumables_preset_model import ConsumablesPresetModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.consumables_preset_slot_model import ConsumablesPresetSlotModel
from gui.impl.lobby.easy_tank_equip.cards.base_card import BasePreset, BaseCard
if typing.TYPE_CHECKING:
    from gui.impl.lobby.easy_tank_equip.data_providers.consumables_data_provider import ConsumablesPresetInfo, ConsumablesPresetSlotInfo
    from gui.shared.money import Money
    from typing import Optional

class ConsumablesCard(BaseCard):

    def _getPreset(self):
        return ConsumablesPreset


class ConsumablesPreset(BasePreset):

    @classmethod
    def getPresetModel(cls):
        return ConsumablesPresetModel()

    @classmethod
    def fillPresetModel(cls, model, presetInfo, balance=None):
        super(ConsumablesPreset, cls).fillPresetModel(model, presetInfo, balance)
        model.setType(presetInfo.presetType)
        cls.__fillPresetItemsModels(model, presetInfo)

    @classmethod
    def __fillPresetItemsModels(cls, model, presetInfo):
        presetItems = model.getItems()
        presetItems.clear()
        for item in presetInfo.items:
            presetSlotModel = ConsumablesPresetSlotModel()
            cls.__fillPresetSlotModel(presetSlotModel, item)
            presetItems.addViewModel(presetSlotModel)

        presetItems.invalidate()

    @classmethod
    def __fillPresetSlotModel(cls, model, presetSlotInfo):
        model.setIntCD(presetSlotInfo.consumable.intCD)
        model.setId(presetSlotInfo.slotIdx)
        model.setIconName(presetSlotInfo.consumable.descriptor.iconName)
        if presetSlotInfo.consumable.isBuiltIn:
            model.setOverlayType(ItemHighlightTypes.BUILT_IN_EQUIPMENT)
        cls.fillSlotInfoModel(model.info, presetSlotInfo.info)
