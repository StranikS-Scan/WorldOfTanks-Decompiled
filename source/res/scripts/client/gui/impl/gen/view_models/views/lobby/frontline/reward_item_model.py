# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/frontline/reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardItemModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getBigIcon(self):
        return self._getString(7)

    def setBigIcon(self, value):
        self._setString(7, value)

    def getItem(self):
        return self._getString(8)

    def setItem(self, value):
        self._setString(8, value)

    def getUserName(self):
        return self._getString(9)

    def setUserName(self, value):
        self._setString(9, value)

    def getName(self):
        return self._getString(10)

    def setName(self, value):
        self._setString(10, value)

    def getTooltipId(self):
        return self._getString(11)

    def setTooltipId(self, value):
        self._setString(11, value)

    def getTooltipContentId(self):
        return self._getString(12)

    def setTooltipContentId(self, value):
        self._setString(12, value)

    def getValue(self):
        return self._getString(13)

    def setValue(self, value):
        self._setString(13, value)

    def getOverlayType(self):
        return self._getString(14)

    def setOverlayType(self, value):
        self._setString(14, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('bigIcon', '')
        self._addStringProperty('item', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('name', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
        self._addStringProperty('value', '')
        self._addStringProperty('overlayType', '')
