# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_level_up_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearLevelUpViewModel(ViewModel):
    __slots__ = ('onClose', 'onToTanks', 'onToTalismans')

    def __init__(self, properties=6, commands=3):
        super(NewYearLevelUpViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    def getContainsTalisman(self):
        return self._getBool(2)

    def setContainsTalisman(self, value):
        self._setBool(2, value)

    def getHasVehicleBranch(self):
        return self._getBool(3)

    def setHasVehicleBranch(self, value):
        self._setBool(3, value)

    def getLevelName(self):
        return self._getString(4)

    def setLevelName(self, value):
        self._setString(4, value)

    def getTalismanSetting(self):
        return self._getString(5)

    def setTalismanSetting(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(NewYearLevelUpViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('containsTalisman', False)
        self._addBoolProperty('hasVehicleBranch', False)
        self._addStringProperty('levelName', '')
        self._addStringProperty('talismanSetting', '')
        self.onClose = self._addCommand('onClose')
        self.onToTanks = self._addCommand('onToTanks')
        self.onToTalismans = self._addCommand('onToTalismans')
