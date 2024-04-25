# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/battle_info_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BattleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(BattleInfoModel, self).__init__(properties=properties, commands=commands)

    def getMissionProgressLabel(self):
        return self._getResource(0)

    def setMissionProgressLabel(self, value):
        self._setResource(0, value)

    def getModeName(self):
        return self._getResource(1)

    def setModeName(self, value):
        self._setResource(1, value)

    def getMapId(self):
        return self._getString(2)

    def setMapId(self, value):
        self._setString(2, value)

    def getMapName(self):
        return self._getString(3)

    def setMapName(self, value):
        self._setString(3, value)

    def getStartDate(self):
        return self._getString(4)

    def setStartDate(self, value):
        self._setString(4, value)

    def getDuration(self):
        return self._getString(5)

    def setDuration(self, value):
        self._setString(5, value)

    def getIsHeroVehicle(self):
        return self._getBool(6)

    def setIsHeroVehicle(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(BattleInfoModel, self)._initialize()
        self._addResourceProperty('missionProgressLabel', R.invalid())
        self._addResourceProperty('modeName', R.invalid())
        self._addStringProperty('mapId', '')
        self._addStringProperty('mapName', '')
        self._addStringProperty('startDate', '')
        self._addStringProperty('duration', '')
        self._addBoolProperty('isHeroVehicle', False)
