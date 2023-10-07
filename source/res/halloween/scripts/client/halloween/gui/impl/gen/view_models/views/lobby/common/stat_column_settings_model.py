# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/stat_column_settings_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ColumnEnum(Enum):
    VEHICLE = 'vehicle'
    EXPERIENCE = 'experience'
    PLACE = 'place'
    KILLS = 'kills'
    DAMAGE = 'damage'


class StatColumnSettingsModel(ViewModel):
    __slots__ = ('onSetSortBy',)

    def __init__(self, properties=2, commands=1):
        super(StatColumnSettingsModel, self).__init__(properties=properties, commands=commands)

    def getSortBy(self):
        return self._getString(0)

    def setSortBy(self, value):
        self._setString(0, value)

    def getSortDirection(self):
        return self._getBool(1)

    def setSortDirection(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(StatColumnSettingsModel, self)._initialize()
        self._addStringProperty('sortBy', '')
        self._addBoolProperty('sortDirection', False)
        self.onSetSortBy = self._addCommand('onSetSortBy')
