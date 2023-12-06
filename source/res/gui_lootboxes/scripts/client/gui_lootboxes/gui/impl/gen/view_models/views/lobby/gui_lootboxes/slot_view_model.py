# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/slot_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import LbBonusTypeModel

class SlotViewModel(LbBonusTypeModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SlotViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getProbabilities(self):
        return self._getArray(2)

    def setProbabilities(self, value):
        self._setArray(2, value)

    @staticmethod
    def getProbabilitiesType():
        return float

    def getBonuses(self):
        return self._getArray(3)

    def setBonuses(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getExtraSlotSettings(self):
        return self._getArray(4)

    def setExtraSlotSettings(self, value):
        self._setArray(4, value)

    @staticmethod
    def getExtraSlotSettingsType():
        return unicode

    def _initialize(self):
        super(SlotViewModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addArrayProperty('probabilities', Array())
        self._addArrayProperty('bonuses', Array())
        self._addArrayProperty('extraSlotSettings', Array())
