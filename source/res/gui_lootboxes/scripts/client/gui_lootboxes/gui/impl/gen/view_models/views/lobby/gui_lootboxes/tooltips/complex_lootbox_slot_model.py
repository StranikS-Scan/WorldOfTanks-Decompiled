# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/complex_lootbox_slot_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class ComplexLootboxSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ComplexLootboxSlotModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

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
        super(ComplexLootboxSlotModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addRealProperty('probability', 0.0)
        self._addArrayProperty('bonuses', Array())
