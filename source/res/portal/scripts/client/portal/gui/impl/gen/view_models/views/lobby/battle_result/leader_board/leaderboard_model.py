# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/battle_result/leader_board/leaderboard_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.leader_board.row_model import RowModel

class LeaderboardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(LeaderboardModel, self).__init__(properties=properties, commands=commands)

    def getPlacesList(self):
        return self._getArray(0)

    def setPlacesList(self, value):
        self._setArray(0, value)

    @staticmethod
    def getPlacesListType():
        return RowModel

    def _initialize(self):
        super(LeaderboardModel, self)._initialize()
        self._addArrayProperty('placesList', Array())
