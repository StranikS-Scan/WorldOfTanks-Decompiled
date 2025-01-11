# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/tooltips/pm3_tooltip_quest_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class QuestType(Enum):
    AND = 'and'
    OR = 'or'


class Pm3TooltipQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(Pm3TooltipQuestModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return QuestType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getIsMain(self):
        return self._getBool(1)

    def setIsMain(self, value):
        self._setBool(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getProgressIcon(self):
        return self._getString(3)

    def setProgressIcon(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(Pm3TooltipQuestModel, self)._initialize()
        self._addStringProperty('type')
        self._addBoolProperty('isMain', False)
        self._addStringProperty('description', '')
        self._addStringProperty('progressIcon', '')
