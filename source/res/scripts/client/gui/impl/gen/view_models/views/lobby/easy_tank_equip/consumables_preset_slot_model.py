# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/consumables_preset_slot_model.py
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.slot_info_model import SlotInfoModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot

class ConsumablesPresetSlotModel(BaseAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(ConsumablesPresetSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def info(self):
        return self._getViewModel(13)

    @staticmethod
    def getInfoType():
        return SlotInfoModel

    def _initialize(self):
        super(ConsumablesPresetSlotModel, self)._initialize()
        self._addViewModelProperty('info', SlotInfoModel())
