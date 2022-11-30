# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_quest_card_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.guest_reward_item_model import GuestRewardItemModel

class CardState(IntEnum):
    LOCKED = 0
    ACTIVE = 1
    COMPLETED = 2
    JUSTCOMPLETED = 3


class NewYearQuestCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NewYearQuestCardModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getResource(self):
        return self._getString(2)

    def setResource(self, value):
        self._setString(2, value)

    def getRequiredAmount(self):
        return self._getNumber(3)

    def setRequiredAmount(self, value):
        self._setNumber(3, value)

    def getState(self):
        return CardState(self._getNumber(4))

    def setState(self, value):
        self._setNumber(4, value.value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return GuestRewardItemModel

    def _initialize(self):
        super(NewYearQuestCardModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('price', 0)
        self._addStringProperty('resource', '')
        self._addNumberProperty('requiredAmount', 0)
        self._addNumberProperty('state')
        self._addArrayProperty('rewards', Array())
