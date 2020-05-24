# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/reward_item_model.py
from frameworks.wulf import ViewModel

class RewardItemModel(ViewModel):
    __slots__ = ()
    SIZE_ADAPTIVE = 0
    SIZE_SMALL = 1
    SIZE_BIG = 2

    def __init__(self, properties=17, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(0)

    def setItem(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getValue(self):
        return self._getString(3)

    def setValue(self, value):
        self._setString(3, value)

    def getBigIcon(self):
        return self._getString(4)

    def setBigIcon(self, value):
        self._setString(4, value)

    def getHighlightType(self):
        return self._getString(5)

    def setHighlightType(self, value):
        self._setString(5, value)

    def getBigHighlightType(self):
        return self._getString(6)

    def setBigHighlightType(self, value):
        self._setString(6, value)

    def getOverlayType(self):
        return self._getString(7)

    def setOverlayType(self, value):
        self._setString(7, value)

    def getBigOverlayType(self):
        return self._getString(8)

    def setBigOverlayType(self, value):
        self._setString(8, value)

    def getHighlightIcon(self):
        return self._getString(9)

    def setHighlightIcon(self, value):
        self._setString(9, value)

    def getBigHighlightIcon(self):
        return self._getString(10)

    def setBigHighlightIcon(self, value):
        self._setString(10, value)

    def getOverlayIcon(self):
        return self._getString(11)

    def setOverlayIcon(self, value):
        self._setString(11, value)

    def getBigOverlayIcon(self):
        return self._getString(12)

    def setBigOverlayIcon(self, value):
        self._setString(12, value)

    def getLabel(self):
        return self._getString(13)

    def setLabel(self, value):
        self._setString(13, value)

    def getAlign(self):
        return self._getString(14)

    def setAlign(self, value):
        self._setString(14, value)

    def getTooltipId(self):
        return self._getNumber(15)

    def setTooltipId(self, value):
        self._setNumber(15, value)

    def getSize(self):
        return self._getNumber(16)

    def setSize(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('value', '')
        self._addStringProperty('bigIcon', '')
        self._addStringProperty('highlightType', '')
        self._addStringProperty('bigHighlightType', '')
        self._addStringProperty('overlayType', '')
        self._addStringProperty('bigOverlayType', '')
        self._addStringProperty('highlightIcon', '')
        self._addStringProperty('bigHighlightIcon', '')
        self._addStringProperty('overlayIcon', '')
        self._addStringProperty('bigOverlayIcon', '')
        self._addStringProperty('label', '')
        self._addStringProperty('align', '')
        self._addNumberProperty('tooltipId', 0)
        self._addNumberProperty('size', 0)
