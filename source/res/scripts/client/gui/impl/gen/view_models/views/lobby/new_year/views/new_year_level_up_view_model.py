# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_level_up_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearLevelUpViewModel(NyWithRomanNumbersModel):
    __slots__ = ('onClose', 'onToTanks', 'onToTalismans')

    def __init__(self, properties=9, commands=3):
        super(NewYearLevelUpViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def getAdditionalRewards(self):
        return self._getArray(3)

    def setAdditionalRewards(self, value):
        self._setArray(3, value)

    def getContainsTalisman(self):
        return self._getBool(4)

    def setContainsTalisman(self, value):
        self._setBool(4, value)

    def getHasVehicleBranch(self):
        return self._getBool(5)

    def setHasVehicleBranch(self, value):
        self._setBool(5, value)

    def getLevelName(self):
        return self._getString(6)

    def setLevelName(self, value):
        self._setString(6, value)

    def getTalismanSetting(self):
        return self._getString(7)

    def setTalismanSetting(self, value):
        self._setString(7, value)

    def getIsViewReady(self):
        return self._getBool(8)

    def setIsViewReady(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(NewYearLevelUpViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self._addBoolProperty('containsTalisman', False)
        self._addBoolProperty('hasVehicleBranch', False)
        self._addStringProperty('levelName', '')
        self._addStringProperty('talismanSetting', '')
        self._addBoolProperty('isViewReady', False)
        self.onClose = self._addCommand('onClose')
        self.onToTanks = self._addCommand('onToTanks')
        self.onToTalismans = self._addCommand('onToTalismans')
