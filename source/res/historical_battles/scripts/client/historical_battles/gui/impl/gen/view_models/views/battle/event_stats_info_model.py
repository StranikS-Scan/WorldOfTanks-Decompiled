# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/battle/event_stats_info_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class EventStatsInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(EventStatsInfoModel, self).__init__(properties=properties, commands=commands)

    def getMapName(self):
        return self._getResource(0)

    def setMapName(self, value):
        self._setResource(0, value)

    def getMissionIcon(self):
        return self._getResource(1)

    def setMissionIcon(self, value):
        self._setResource(1, value)

    def getMissionTitle(self):
        return self._getResource(2)

    def setMissionTitle(self, value):
        self._setResource(2, value)

    def getMissionTask(self):
        return self._getResource(3)

    def setMissionTask(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(EventStatsInfoModel, self)._initialize()
        self._addResourceProperty('mapName', R.invalid())
        self._addResourceProperty('missionIcon', R.invalid())
        self._addResourceProperty('missionTitle', R.invalid())
        self._addResourceProperty('missionTask', R.invalid())
