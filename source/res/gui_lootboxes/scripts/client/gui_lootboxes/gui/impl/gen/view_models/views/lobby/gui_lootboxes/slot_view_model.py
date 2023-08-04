# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/slot_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import LbBonusTypeModel

class SlotViewModel(LbBonusTypeModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SlotViewModel, self).__init__(properties=properties, commands=commands)

    def getProbability(self):
        return self._getReal(1)

    def setProbability(self, value):
        self._setReal(1, value)

    def getBonuses(self):
        return self._getArray(2)

    def setBonuses(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(SlotViewModel, self)._initialize()
        self._addRealProperty('probability', 0.0)
        self._addArrayProperty('bonuses', Array())
