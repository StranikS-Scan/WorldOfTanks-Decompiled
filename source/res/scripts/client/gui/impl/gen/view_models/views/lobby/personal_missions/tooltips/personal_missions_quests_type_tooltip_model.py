# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/tooltips/personal_missions_quests_type_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class QuestsType(Enum):
    HIT = 'hit'
    KILLS = 'kills'
    ASSIST = 'assist'
    BATTLE = 'battle'
    MASTER = 'master'


class PersonalMissionsQuestsTypeTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PersonalMissionsQuestsTypeTooltipModel, self).__init__(properties=properties, commands=commands)

    def getQuestsType(self):
        return QuestsType(self._getString(0))

    def setQuestsType(self, value):
        self._setString(0, value.value)

    def getQuestType(self):
        return self._getString(1)

    def setQuestType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(PersonalMissionsQuestsTypeTooltipModel, self)._initialize()
        self._addStringProperty('questsType')
        self._addStringProperty('questType', '')
