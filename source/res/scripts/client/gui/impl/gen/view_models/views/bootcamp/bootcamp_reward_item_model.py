# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bootcamp/bootcamp_reward_item_model.py
from frameworks.wulf import ViewModel

class BootcampRewardItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BootcampRewardItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getTooltipId(self):
        return self._getNumber(2)

    def setTooltipId(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BootcampRewardItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('tooltipId', 0)
