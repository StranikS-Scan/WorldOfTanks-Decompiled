# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/lootboxes/new_year_toy_icon_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class NewYearToyIconBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(NewYearToyIconBonusModel, self).__init__(properties=properties, commands=commands)

    def getBigIcon(self):
        return self._getString(8)

    def setBigIcon(self, value):
        self._setString(8, value)

    def getRankIcon(self):
        return self._getString(9)

    def setRankIcon(self, value):
        self._setString(9, value)

    def getRankValue(self):
        return self._getNumber(10)

    def setRankValue(self, value):
        self._setNumber(10, value)

    def getToyID(self):
        return self._getNumber(11)

    def setToyID(self, value):
        self._setNumber(11, value)

    def getIsNew(self):
        return self._getBool(12)

    def setIsNew(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NewYearToyIconBonusModel, self)._initialize()
        self._addStringProperty('bigIcon', '')
        self._addStringProperty('rankIcon', '')
        self._addNumberProperty('rankValue', 0)
        self._addNumberProperty('toyID', 0)
        self._addBoolProperty('isNew', False)
