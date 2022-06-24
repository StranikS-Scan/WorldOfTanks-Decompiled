# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/battle_results/leaderboard/leaderboard_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.leaderboard.group_model import GroupModel

class LeaderboardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(LeaderboardModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getGroupList(self):
        return self._getArray(1)

    def setGroupList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getGroupListType():
        return GroupModel

    def _initialize(self):
        super(LeaderboardModel, self)._initialize()
        self._addStringProperty('type', 'solo')
        self._addArrayProperty('groupList', Array())
