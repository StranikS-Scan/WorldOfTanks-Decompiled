# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_quest_part_relation_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_relation_group_model import Pm3QuestRelationGroupModel

class QuestRelationType(Enum):
    AND = 'and'
    OR = 'or'


class Pm3QuestPartRelationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(Pm3QuestPartRelationModel, self).__init__(properties=properties, commands=commands)

    def getRelationType(self):
        return QuestRelationType(self._getString(0))

    def setRelationType(self, value):
        self._setString(0, value.value)

    def getGroups(self):
        return self._getArray(1)

    def setGroups(self, value):
        self._setArray(1, value)

    @staticmethod
    def getGroupsType():
        return Pm3QuestRelationGroupModel

    def _initialize(self):
        super(Pm3QuestPartRelationModel, self)._initialize()
        self._addStringProperty('relationType')
        self._addArrayProperty('groups', Array())
