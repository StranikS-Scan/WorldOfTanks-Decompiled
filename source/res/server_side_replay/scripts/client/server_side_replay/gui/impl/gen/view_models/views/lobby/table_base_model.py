# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/table_base_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.replay_model import ReplayModel

class StatParams(Enum):
    EARNEDXP = 'earnedXp'
    DAMAGEDEALT = 'damageDealt'
    DAMAGEASSISTED = 'damageAssisted'
    DAMAGEBLOCKEDBYARMOR = 'damageBlockedByArmor'
    KILLS = 'kills'
    MARKSOFMASTERY = 'marksOfMastery'
    DATE = 'date'


class State(IntEnum):
    INITIAL = 0
    SUCCESS = 1
    ERROR = 2


class TableBaseModel(ViewModel):
    __slots__ = ('onResetFilter', 'onSort', 'onRefresh', 'onWatch')
    DEFAULT_REPLAY_INDEX = -1

    def __init__(self, properties=7, commands=4):
        super(TableBaseModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getIsLoading(self):
        return self._getBool(1)

    def setIsLoading(self, value):
        self._setBool(1, value)

    def getIsPopoverEnabled(self):
        return self._getBool(2)

    def setIsPopoverEnabled(self, value):
        self._setBool(2, value)

    def getIsPopoverHighlighted(self):
        return self._getBool(3)

    def setIsPopoverHighlighted(self, value):
        self._setBool(3, value)

    def getSelectedSorting(self):
        return StatParams(self._getString(4))

    def setSelectedSorting(self, value):
        self._setString(4, value.value)

    def getItems(self):
        return self._getArray(5)

    def setItems(self, value):
        self._setArray(5, value)

    @staticmethod
    def getItemsType():
        return ReplayModel

    def getInitialReplayIndex(self):
        return self._getNumber(6)

    def setInitialReplayIndex(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(TableBaseModel, self)._initialize()
        self._addNumberProperty('state')
        self._addBoolProperty('isLoading', False)
        self._addBoolProperty('isPopoverEnabled', True)
        self._addBoolProperty('isPopoverHighlighted', False)
        self._addStringProperty('selectedSorting', StatParams.EARNEDXP.value)
        self._addArrayProperty('items', Array())
        self._addNumberProperty('initialReplayIndex', -1)
        self.onResetFilter = self._addCommand('onResetFilter')
        self.onSort = self._addCommand('onSort')
        self.onRefresh = self._addCommand('onRefresh')
        self.onWatch = self._addCommand('onWatch')
