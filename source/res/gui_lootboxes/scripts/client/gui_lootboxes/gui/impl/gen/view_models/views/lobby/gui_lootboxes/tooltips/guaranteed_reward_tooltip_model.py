# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/guaranteed_reward_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class GuaranteedRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(GuaranteedRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLevelsRange(self):
        return self._getArray(0)

    def setLevelsRange(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLevelsRangeType():
        return int

    def getGuaranteedFrequencies(self):
        return self._getArray(1)

    def setGuaranteedFrequencies(self, value):
        self._setArray(1, value)

    @staticmethod
    def getGuaranteedFrequenciesType():
        return int

    def getGuaranteedBoxNameKeys(self):
        return self._getArray(2)

    def setGuaranteedBoxNameKeys(self, value):
        self._setArray(2, value)

    @staticmethod
    def getGuaranteedBoxNameKeysType():
        return unicode

    def getVehiclesOnly(self):
        return self._getBool(3)

    def setVehiclesOnly(self, value):
        self._setBool(3, value)

    def getMultipleStages(self):
        return self._getBool(4)

    def setMultipleStages(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(GuaranteedRewardTooltipModel, self)._initialize()
        self._addArrayProperty('levelsRange', Array())
        self._addArrayProperty('guaranteedFrequencies', Array())
        self._addArrayProperty('guaranteedBoxNameKeys', Array())
        self._addBoolProperty('vehiclesOnly', True)
        self._addBoolProperty('multipleStages', False)
