# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardItemModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(8)

    def setIcon(self, value):
        self._setString(8, value)

    def getIsOpenable(self):
        return self._getBool(9)

    def setIsOpenable(self, value):
        self._setBool(9, value)

    def getPreviousIcon(self):
        return self._getString(10)

    def setPreviousIcon(self, value):
        self._setString(10, value)

    def getIsSelected(self):
        return self._getBool(11)

    def setIsSelected(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addBoolProperty('isOpenable', False)
        self._addStringProperty('previousIcon', '')
        self._addBoolProperty('isSelected', False)
