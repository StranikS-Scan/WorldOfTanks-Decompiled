# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/leaderboard_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.table_record_model import TableRecordModel

class State(IntEnum):
    INITIAL = 0
    SUCCESS = 1
    ERROR = 2


class LeaderboardModel(ViewModel):
    __slots__ = ('onRefresh', 'getTableRecords')
    DEFAULT_POSITION = -1
    PAGE_SIZE = 50

    def __init__(self, properties=12, commands=2):
        super(LeaderboardModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getIsLoading(self):
        return self._getBool(1)

    def setIsLoading(self, value):
        self._setBool(1, value)

    def getPersonalPosition(self):
        return self._getNumber(2)

    def setPersonalPosition(self, value):
        self._setNumber(2, value)

    def getPersonalScore(self):
        return self._getNumber(3)

    def setPersonalScore(self, value):
        self._setNumber(3, value)

    def getPersonalBattlesCount(self):
        return self._getNumber(4)

    def setPersonalBattlesCount(self, value):
        self._setNumber(4, value)

    def getLastBestUserPosition(self):
        return self._getNumber(5)

    def setLastBestUserPosition(self, value):
        self._setNumber(5, value)

    def getLeaderboardUpdateTimestamp(self):
        return self._getNumber(6)

    def setLeaderboardUpdateTimestamp(self, value):
        self._setNumber(6, value)

    def getFrom(self):
        return self._getNumber(7)

    def setFrom(self, value):
        self._setNumber(7, value)

    def getTopPercentage(self):
        return self._getNumber(8)

    def setTopPercentage(self, value):
        self._setNumber(8, value)

    def getRecordsCount(self):
        return self._getNumber(9)

    def setRecordsCount(self, value):
        self._setNumber(9, value)

    def getOwnSpaID(self):
        return self._getNumber(10)

    def setOwnSpaID(self, value):
        self._setNumber(10, value)

    def getItems(self):
        return self._getArray(11)

    def setItems(self, value):
        self._setArray(11, value)

    @staticmethod
    def getItemsType():
        return TableRecordModel

    def _initialize(self):
        super(LeaderboardModel, self)._initialize()
        self._addNumberProperty('state')
        self._addBoolProperty('isLoading', False)
        self._addNumberProperty('personalPosition', -1)
        self._addNumberProperty('personalScore', 0)
        self._addNumberProperty('personalBattlesCount', 0)
        self._addNumberProperty('lastBestUserPosition', -1)
        self._addNumberProperty('leaderboardUpdateTimestamp', 0)
        self._addNumberProperty('from', 2000)
        self._addNumberProperty('topPercentage', 10)
        self._addNumberProperty('recordsCount', 0)
        self._addNumberProperty('ownSpaID', 0)
        self._addArrayProperty('items', Array())
        self.onRefresh = self._addCommand('onRefresh')
        self.getTableRecords = self._addCommand('getTableRecords')
