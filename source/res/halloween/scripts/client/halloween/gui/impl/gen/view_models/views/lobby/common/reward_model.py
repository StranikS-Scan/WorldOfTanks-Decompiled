# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/reward_model.py
from frameworks.wulf import ViewModel

class RewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getLabelCount(self):
        return self._getString(1)

    def setLabelCount(self, value):
        self._setString(1, value)

    def getTooltipId(self):
        return self._getString(2)

    def setTooltipId(self, value):
        self._setString(2, value)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('labelCount', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('iconName', '')
        self._addStringProperty('description', '')
