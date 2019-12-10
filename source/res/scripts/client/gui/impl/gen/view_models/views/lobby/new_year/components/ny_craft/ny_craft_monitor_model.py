# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_craft/ny_craft_monitor_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyCraftMonitorModel(ViewModel):
    __slots__ = ()
    SHARDS_NOT_AVAILABLE = 0
    NOT_ENOUGH_SHARDS_FOR_REGULAR = 1
    NOT_ENOUGH_SHARDS_FOR_MEGA = 2
    PARAMS_REGULAR = 3
    PARAMS_MEGA = 4
    FULL_REGULAR = 5
    FULL_REGULAR_SUBGROUP = 6
    FULL_MEGA = 7
    HAS_RANDOM_PARAM = 8
    HAS_NOT_FILLERS = 9

    def __init__(self, properties=8, commands=0):
        super(NyCraftMonitorModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getNumber(0)

    def setState(self, value):
        self._setNumber(0, value)

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

    def getAntiduplicateEnabled(self):
        return self._getBool(6)

    def setAntiduplicateEnabled(self, value):
        self._setBool(6, value)

    def getCountMegaToys(self):
        return self._getNumber(7)

    def setCountMegaToys(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(NyCraftMonitorModel, self)._initialize()
        self._addNumberProperty('state', -1)
        self._addNumberProperty('shardsCount', 0)
        self._addStringProperty('level', '')
        self._addResourceProperty('setting', R.invalid())
        self._addResourceProperty('type', R.invalid())
        self._addResourceProperty('objectType', R.invalid())
        self._addBoolProperty('antiduplicateEnabled', False)
        self._addNumberProperty('countMegaToys', 0)
