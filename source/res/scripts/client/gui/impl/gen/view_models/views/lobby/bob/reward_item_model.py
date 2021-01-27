# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bob/reward_item_model.py
from frameworks.wulf import ViewModel

class RewardItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(0)

    def setItem(self, value):
        self._setString(0, value)

    def getUserName(self):
        return self._getString(1)

    def setUserName(self, value):
        self._setString(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getValue(self):
        return self._getString(4)

    def setValue(self, value):
        self._setString(4, value)

    def getLabel(self):
        return self._getString(5)

    def setLabel(self, value):
        self._setString(5, value)

    def getTooltipId(self):
        return self._getNumber(6)

    def setTooltipId(self, value):
        self._setNumber(6, value)

    def getIsCompensation(self):
        return self._getBool(7)

    def setIsCompensation(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('value', '')
        self._addStringProperty('label', '')
        self._addNumberProperty('tooltipId', 0)
        self._addBoolProperty('isCompensation', False)
