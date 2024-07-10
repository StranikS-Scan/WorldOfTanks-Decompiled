# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/crew_book_reward_option_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class CrewBookRewardOptionModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(CrewBookRewardOptionModel, self).__init__(properties=properties, commands=commands)

    def getExpBonusValue(self):
        return self._getNumber(8)

    def setExpBonusValue(self, value):
        self._setNumber(8, value)

    def getIcon(self):
        return self._getString(9)

    def setIcon(self, value):
        self._setString(9, value)

    def getDescription(self):
        return self._getString(10)

    def setDescription(self, value):
        self._setString(10, value)

    def getItemID(self):
        return self._getNumber(11)

    def setItemID(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(CrewBookRewardOptionModel, self)._initialize()
        self._addNumberProperty('expBonusValue', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('itemID', 0)
