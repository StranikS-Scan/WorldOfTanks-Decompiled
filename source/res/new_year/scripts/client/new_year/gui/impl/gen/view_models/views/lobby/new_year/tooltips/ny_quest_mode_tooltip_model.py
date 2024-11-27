# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_quest_mode_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NyQuestModeTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyQuestModeTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMinVehicleLevel(self):
        return self._getNumber(0)

    def setMinVehicleLevel(self, value):
        self._setNumber(0, value)

    def getMaxVehicleLevel(self):
        return self._getNumber(1)

    def setMaxVehicleLevel(self, value):
        self._setNumber(1, value)

    def getBattleModes(self):
        return self._getArray(2)

    def setBattleModes(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBattleModesType():
        return unicode

    def _initialize(self):
        super(NyQuestModeTooltipModel, self)._initialize()
        self._addNumberProperty('minVehicleLevel', 1)
        self._addNumberProperty('maxVehicleLevel', 11)
        self._addArrayProperty('battleModes', Array())
