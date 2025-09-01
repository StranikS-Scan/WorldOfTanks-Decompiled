# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/common/stat_column_settings_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel

class ColumnEnum(Enum):
    KILLS = 'kills'
    DAMAGE = 'damage'
    ASSIST = 'assist'
    BLOCKED = 'blocked'
    PLACE = 'place'
    KEYS = 'keys'


class StatColumnSettingsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(StatColumnSettingsModel, self).__init__(properties=properties, commands=commands)

    def getVisibleColumns(self):
        return self._getArray(0)

    def setVisibleColumns(self, value):
        self._setArray(0, value)

    @staticmethod
    def getVisibleColumnsType():
        return ColumnEnum

    def _initialize(self):
        super(StatColumnSettingsModel, self)._initialize()
        self._addArrayProperty('visibleColumns', Array())
