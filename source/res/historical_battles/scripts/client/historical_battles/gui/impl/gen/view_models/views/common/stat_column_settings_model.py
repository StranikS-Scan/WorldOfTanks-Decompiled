# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/common/stat_column_settings_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ColumnEnum(Enum):
    KILLS = 'kills'
    DAMAGE = 'damage'
    ASSIST = 'assist'
    BLOCKED = 'blocked'


class StatColumnSettingsModel(ViewModel):
    __slots__ = ('onSetSortBy',)

    def __init__(self, properties=3, commands=1):
        super(StatColumnSettingsModel, self).__init__(properties=properties, commands=commands)

    def getVisibleColumns(self):
        return self._getArray(0)

    def setVisibleColumns(self, value):
        self._setArray(0, value)

    @staticmethod
    def getVisibleColumnsType():
        return ColumnEnum

    def getSortBy(self):
        return self._getString(1)

    def setSortBy(self, value):
        self._setString(1, value)

    def getSortDirection(self):
        return self._getBool(2)

    def setSortDirection(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(StatColumnSettingsModel, self)._initialize()
        self._addArrayProperty('visibleColumns', Array())
        self._addStringProperty('sortBy', '')
        self._addBoolProperty('sortDirection', False)
        self.onSetSortBy = self._addCommand('onSetSortBy')
