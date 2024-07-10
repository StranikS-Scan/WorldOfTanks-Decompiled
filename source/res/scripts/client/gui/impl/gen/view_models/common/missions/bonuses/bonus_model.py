# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/bonus_model.py
from frameworks.wulf import ViewModel

class BonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(BonusModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(0)

    def setIndex(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getString(2)

    def setValue(self, value):
        self._setString(2, value)

    def getIsCompensation(self):
        return self._getBool(3)

    def setIsCompensation(self, value):
        self._setBool(3, value)

    def getTooltipId(self):
        return self._getString(4)

    def setTooltipId(self, value):
        self._setString(4, value)

    def getTooltipContentId(self):
        return self._getString(5)

    def setTooltipContentId(self, value):
        self._setString(5, value)

    def getLabel(self):
        return self._getString(6)

    def setLabel(self, value):
        self._setString(6, value)

    def getProbability(self):
        return self._getNumber(7)

    def setProbability(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(BonusModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
        self._addBoolProperty('isCompensation', False)
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
        self._addStringProperty('label', '')
        self._addNumberProperty('probability', 0)
