# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lb_bonus_type_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class BonusType(IntEnum):
    VEHICLE = 0
    RENTEDVEHICLE = 1
    DEFAULT = 2


class LbBonusTypeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(LbBonusTypeModel, self).__init__(properties=properties, commands=commands)

    def getBonusType(self):
        return BonusType(self._getNumber(0))

    def setBonusType(self, value):
        self._setNumber(0, value.value)

    def _initialize(self):
        super(LbBonusTypeModel, self)._initialize()
        self._addNumberProperty('bonusType')
