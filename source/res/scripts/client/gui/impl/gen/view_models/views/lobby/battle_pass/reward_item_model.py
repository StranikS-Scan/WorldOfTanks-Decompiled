# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardItemModel(BonusModel):
    __slots__ = ()
    SIZE_ADAPTIVE = 0
    SIZE_SMALL = 1
    SIZE_BIG = 2

    def __init__(self, properties=20, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(7)

    def setItem(self, value):
        self._setString(7, value)

    def getIcon(self):
        return self._getString(8)

    def setIcon(self, value):
        self._setString(8, value)

    def getBigIcon(self):
        return self._getString(9)

    def setBigIcon(self, value):
        self._setString(9, value)

    def getHighlightType(self):
        return self._getString(10)

    def setHighlightType(self, value):
        self._setString(10, value)

    def getBigHighlightType(self):
        return self._getString(11)

    def setBigHighlightType(self, value):
        self._setString(11, value)

    def getOverlayType(self):
        return self._getString(12)

    def setOverlayType(self, value):
        self._setString(12, value)

    def getBigOverlayType(self):
        return self._getString(13)

    def setBigOverlayType(self, value):
        self._setString(13, value)

    def getHighlightIcon(self):
        return self._getString(14)

    def setHighlightIcon(self, value):
        self._setString(14, value)

    def getBigHighlightIcon(self):
        return self._getString(15)

    def setBigHighlightIcon(self, value):
        self._setString(15, value)

    def getOverlayIcon(self):
        return self._getString(16)

    def setOverlayIcon(self, value):
        self._setString(16, value)

    def getBigOverlayIcon(self):
        return self._getString(17)

    def setBigOverlayIcon(self, value):
        self._setString(17, value)

    def getAlign(self):
        return self._getString(18)

    def setAlign(self, value):
        self._setString(18, value)

    def getSize(self):
        return self._getNumber(19)

    def setSize(self, value):
        self._setNumber(19, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('bigIcon', '')
        self._addStringProperty('highlightType', '')
        self._addStringProperty('bigHighlightType', '')
        self._addStringProperty('overlayType', '')
        self._addStringProperty('bigOverlayType', '')
        self._addStringProperty('highlightIcon', '')
        self._addStringProperty('bigHighlightIcon', '')
        self._addStringProperty('overlayIcon', '')
        self._addStringProperty('bigOverlayIcon', '')
        self._addStringProperty('align', '')
        self._addNumberProperty('size', 0)
