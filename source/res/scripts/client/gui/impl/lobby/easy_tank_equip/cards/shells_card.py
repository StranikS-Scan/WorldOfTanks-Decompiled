# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/cards/shells_card.py
import typing
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.shells_preset_slot_model import ShellsPresetSlotModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.shells_preset_model import ShellsPresetModel
from gui.impl.lobby.easy_tank_equip.cards.base_card import BasePreset, BaseCard
if typing.TYPE_CHECKING:
    from gui.impl.lobby.easy_tank_equip.data_providers.shells_data_provider import ShellsPresetInfo, ShellsPresetSlotInfo
    from gui.shared.money import Money
    from typing import Optional

class ShellsCard(BaseCard):

    def _getPreset(self):
        return ShellsPreset


class ShellsPreset(BasePreset):

    @classmethod
    def getPresetModel(cls):
        return ShellsPresetModel()

    @classmethod
    def fillPresetModel(cls, model, presetInfo, balance=None):
        super(ShellsPreset, cls).fillPresetModel(model, presetInfo, balance)
        model.setType(presetInfo.presetType)
        cls.__fillPresetItemsModels(model, presetInfo)

    @classmethod
    def __fillPresetItemsModels(cls, model, presetInfo):
        presetItems = model.getItems()
        presetItems.clear()
        for item in presetInfo.items:
            presetSlotModel = ShellsPresetSlotModel()
            cls.__fillPresetSlotModel(presetSlotModel, item)
            presetItems.addViewModel(presetSlotModel)

        presetItems.invalidate()

    @classmethod
    def __fillPresetSlotModel(cls, model, presetSlotInfo):
        model.setIntCD(presetSlotInfo.shell.intCD)
        model.setId(presetSlotInfo.slotIdx)
        model.setCount(presetSlotInfo.shell.count)
        model.setIconName(presetSlotInfo.shell.descriptor.iconName)
        cls.fillSlotInfoModel(model.info, presetSlotInfo.info)
