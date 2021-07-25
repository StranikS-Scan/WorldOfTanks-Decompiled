# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/perk_bonus_model.py
from frameworks.wulf import ViewModel

class PerkBonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PerkBonusModel, self).__init__(properties=properties, commands=commands)

    def getBonus(self):
        return self._getNumber(0)

    def setBonus(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIsOvercapped(self):
        return self._getBool(2)

    def setIsOvercapped(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PerkBonusModel, self)._initialize()
        self._addNumberProperty('bonus', 0)
        self._addStringProperty('name', '')
        self._addBoolProperty('isOvercapped', False)
