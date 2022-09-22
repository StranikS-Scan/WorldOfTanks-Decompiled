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

    def getImage(self):
        return self._getString(1)

    def setImage(self, value):
        self._setString(1, value)

    def getSpecial(self):
        return self._getString(2)

    def setSpecial(self, value):
        self._setString(2, value)

    def getValue(self):
        return self._getString(3)

    def setValue(self, value):
        self._setString(3, value)

    def getValueType(self):
        return self._getString(4)

    def setValueType(self, value):
        self._setString(4, value)

    def getTooltipArgs(self):
        return self._getString(5)

    def setTooltipArgs(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('image', '')
        self._addStringProperty('special', '')
        self._addStringProperty('value', '')
        self._addStringProperty('valueType', '')
        self._addStringProperty('tooltipArgs', '')
