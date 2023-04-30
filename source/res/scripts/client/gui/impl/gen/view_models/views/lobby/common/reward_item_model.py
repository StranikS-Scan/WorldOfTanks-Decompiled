# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/reward_item_model.py
from frameworks.wulf import ViewModel

class RewardItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getNumber(2)

    def setValue(self, value):
        self._setNumber(2, value)

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def getTooltipContentId(self):
        return self._getNumber(4)

    def setTooltipContentId(self, value):
        self._setNumber(4, value)

    def getOverlayType(self):
        return self._getString(5)

    def setOverlayType(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('name', '')
        self._addNumberProperty('value', 0)
        self._addStringProperty('tooltipId', '')
        self._addNumberProperty('tooltipContentId', 0)
        self._addStringProperty('overlayType', '')
