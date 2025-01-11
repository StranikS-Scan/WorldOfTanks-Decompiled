# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_quest_relation_group.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class Pm3QuestRelationGroup(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(Pm3QuestRelationGroup, self).__init__(properties=properties, commands=commands)

    def getGroups(self):
        return self._getArray(0)

    def setGroups(self, value):
        self._setArray(0, value)

    @staticmethod
    def getGroupsType():
        return unicode

    def _initialize(self):
        super(Pm3QuestRelationGroup, self)._initialize()
        self._addArrayProperty('groups', Array())
