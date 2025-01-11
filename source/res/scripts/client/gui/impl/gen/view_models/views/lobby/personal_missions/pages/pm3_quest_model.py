# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_quest_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quest_element_model import Pm3QuestElementModel

class QuestType(Enum):
    AND = 'and'
    OR = 'or'


class Pm3QuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(Pm3QuestModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return QuestType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getRewardList(self):
        return self._getArray(1)

    def setRewardList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardListType():
        return BonusModel

    def getList(self):
        return self._getArray(2)

    def setList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getListType():
        return Pm3QuestElementModel

    def _initialize(self):
        super(Pm3QuestModel, self)._initialize()
        self._addStringProperty('type')
        self._addArrayProperty('rewardList', Array())
        self._addArrayProperty('list', Array())
