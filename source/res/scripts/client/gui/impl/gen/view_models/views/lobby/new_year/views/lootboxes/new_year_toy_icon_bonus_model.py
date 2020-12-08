# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/lootboxes/new_year_toy_icon_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class NewYearToyIconBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(NewYearToyIconBonusModel, self).__init__(properties=properties, commands=commands)

    def getRankIcon(self):
        return self._getString(6)

    def setRankIcon(self, value):
        self._setString(6, value)

    def getRankValue(self):
        return self._getNumber(7)

    def setRankValue(self, value):
        self._setNumber(7, value)

    def getIsMega(self):
        return self._getBool(8)

    def setIsMega(self, value):
        self._setBool(8, value)

    def getToyID(self):
        return self._getNumber(9)

    def setToyID(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(NewYearToyIconBonusModel, self)._initialize()
        self._addStringProperty('rankIcon', '')
        self._addNumberProperty('rankValue', 0)
        self._addBoolProperty('isMega', False)
        self._addNumberProperty('toyID', 0)
