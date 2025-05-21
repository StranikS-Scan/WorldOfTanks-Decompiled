# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/battle/full_stats_view_model.py
from frameworks.wulf import ViewModel

class FullStatsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FullStatsViewModel, self).__init__(properties=properties, commands=commands)

    def getMissionTitle(self):
        return self._getString(0)

    def setMissionTitle(self, value):
        self._setString(0, value)

    def getMissionTask(self):
        return self._getString(1)

    def setMissionTask(self, value):
        self._setString(1, value)

    def getDifficultyLevel(self):
        return self._getNumber(2)

    def setDifficultyLevel(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(FullStatsViewModel, self)._initialize()
        self._addStringProperty('missionTitle', '')
        self._addStringProperty('missionTask', '')
        self._addNumberProperty('difficultyLevel', 0)
