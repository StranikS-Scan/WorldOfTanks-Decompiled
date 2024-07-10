# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardItemModel(BonusModel):
    __slots__ = ()
    SIZE_ADAPTIVE = 0
    SIZE_SMALL = 1
    SIZE_BIG = 2

    def __init__(self, properties=16, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(8)

    def setItem(self, value):
        self._setString(8, value)

    def getUserName(self):
        return self._getString(9)

    def setUserName(self, value):
        self._setString(9, value)

    def getIcon(self):
        return self._getString(10)

    def setIcon(self, value):
        self._setString(10, value)

    def getType(self):
        return self._getString(11)

    def setType(self, value):
        self._setString(11, value)

    def getBigIcon(self):
        return self._getString(12)

    def setBigIcon(self, value):
        self._setString(12, value)

    def getOverlayType(self):
        return self._getString(13)

    def setOverlayType(self, value):
        self._setString(13, value)

    def getIsCollectionEntity(self):
        return self._getBool(14)

    def setIsCollectionEntity(self, value):
        self._setBool(14, value)

    def getItemType(self):
        return self._getNumber(15)

    def setItemType(self, value):
        self._setNumber(15, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('type', '')
        self._addStringProperty('bigIcon', '')
        self._addStringProperty('overlayType', '')
        self._addBoolProperty('isCollectionEntity', False)
        self._addNumberProperty('itemType', 0)
