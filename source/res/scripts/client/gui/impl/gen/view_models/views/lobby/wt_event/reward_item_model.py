# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/reward_item_model.py
from frameworks.wulf import ViewModel

class RewardItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIsCompensation(self):
        return self._getBoolean(1)

    def setIsCompensation(self, value):
        self._setBoolean(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getBigIcon(self):
        return self._getString(3)

    def setBigIcon(self, value):
        self._setString(3, value)

    def getTooltipId(self):
        return self._getNumber(4)

    def setTooltipId(self, value):
        self._setNumber(4, value)

    def getValue(self):
        return self._getNumber(5)

    def setValue(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addBooleanProperty('isCompensation')
        self._addStringProperty('icon', '')
        self._addStringProperty('bigIcon', '')
        self._addNumberProperty('tooltipId', 0)
        self._addNumberProperty('value', 0)
