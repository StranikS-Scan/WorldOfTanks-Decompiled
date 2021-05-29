# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardItemModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(7)

    def setIcon(self, value):
        self._setString(7, value)

    def getIsOpenable(self):
        return self._getBool(8)

    def setIsOpenable(self, value):
        self._setBool(8, value)

    def getPreviousIcon(self):
        return self._getString(9)

    def setPreviousIcon(self, value):
        self._setString(9, value)

    def getIsSelected(self):
        return self._getBool(10)

    def setIsSelected(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addBoolProperty('isOpenable', False)
        self._addStringProperty('previousIcon', '')
        self._addBoolProperty('isSelected', False)
