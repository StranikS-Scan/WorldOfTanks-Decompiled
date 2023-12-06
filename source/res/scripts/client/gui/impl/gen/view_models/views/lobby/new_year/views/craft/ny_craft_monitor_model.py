# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/craft/ny_craft_monitor_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class MonitorState(Enum):
    INITIAL = 'INITIAL'
    SHARDS_NOT_AVAILABLE = 'SHARDS_NOT_AVAILABLE'
    NOT_ENOUGH_SHARDS_FOR_REGULAR = 'NOT_ENOUGH_SHARDS_FOR_REGULAR'
    PARAMS_REGULAR = 'PARAMS_REGULAR'
    FULL_REGULAR = 'FULL_REGULAR'
    FULL_REGULAR_SUBGROUP = 'FULL_REGULAR_SUBGROUP'
    HAS_RANDOM_PARAM = 'HAS_RANDOM_PARAM'
    HAS_NO_FILLERS = 'HAS_NO_FILLERS'


class NyCraftMonitorModel(ViewModel):
    __slots__ = ('onPlaySound', 'onStopSound')

    def __init__(self, properties=7, commands=2):
        super(NyCraftMonitorModel, self).__init__(properties=properties, commands=commands)

    def getMonitorState(self):
        return MonitorState(self._getString(0))

    def setMonitorState(self, value):
        self._setString(0, value.value)

    def getShardsCount(self):
        return self._getNumber(1)

    def setShardsCount(self, value):
        self._setNumber(1, value)

    def getLevel(self):
        return self._getString(2)

    def setLevel(self, value):
        self._setString(2, value)

    def getSetting(self):
        return self._getResource(3)

    def setSetting(self, value):
        self._setResource(3, value)

    def getType(self):
        return self._getResource(4)

    def setType(self, value):
        self._setResource(4, value)

    def getObjectType(self):
        return self._getResource(5)

    def setObjectType(self, value):
        self._setResource(5, value)

    def getIsAntiDuplicatorEnabled(self):
        return self._getBool(6)

    def setIsAntiDuplicatorEnabled(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NyCraftMonitorModel, self)._initialize()
        self._addStringProperty('monitorState')
        self._addNumberProperty('shardsCount', 0)
        self._addStringProperty('level', '')
        self._addResourceProperty('setting', R.invalid())
        self._addResourceProperty('type', R.invalid())
        self._addResourceProperty('objectType', R.invalid())
        self._addBoolProperty('isAntiDuplicatorEnabled', False)
        self.onPlaySound = self._addCommand('onPlaySound')
        self.onStopSound = self._addCommand('onStopSound')
