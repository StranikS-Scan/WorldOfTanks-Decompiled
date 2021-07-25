# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/maps_training_result_model.py
from enum import IntEnum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class DoneValueEnum(IntEnum):
    UNDONE = 0
    PARTIALDONE = 1
    DONE = 2


class MapsTrainingResultModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=12, commands=1):
        super(MapsTrainingResultModel, self).__init__(properties=properties, commands=commands)

    def getDoneValue(self):
        return DoneValueEnum(self._getNumber(0))

    def setDoneValue(self, value):
        self._setNumber(0, value.value)

    def getMapID(self):
        return self._getString(1)

    def setMapID(self, value):
        self._setString(1, value)

    def getMapName(self):
        return self._getResource(2)

    def setMapName(self, value):
        self._setResource(2, value)

    def getSelectedScenario(self):
        return self._getString(3)

    def setSelectedScenario(self, value):
        self._setString(3, value)

    def getSelectedVehicleType(self):
        return self._getResource(4)

    def setSelectedVehicleType(self, value):
        self._setResource(4, value)

    def getKills(self):
        return self._getNumber(5)

    def setKills(self, value):
        self._setNumber(5, value)

    def getAllTargets(self):
        return self._getNumber(6)

    def setAllTargets(self, value):
        self._setNumber(6, value)

    def getTime(self):
        return self._getString(7)

    def setTime(self, value):
        self._setString(7, value)

    def getVehicleImage(self):
        return self._getResource(8)

    def setVehicleImage(self, value):
        self._setResource(8, value)

    def getWasDone(self):
        return self._getBool(9)

    def setWasDone(self, value):
        self._setBool(9, value)

    def getHangarReady(self):
        return self._getBool(10)

    def setHangarReady(self, value):
        self._setBool(10, value)

    def getRewards(self):
        return self._getArray(11)

    def setRewards(self, value):
        self._setArray(11, value)

    def _initialize(self):
        super(MapsTrainingResultModel, self)._initialize()
        self._addNumberProperty('doneValue')
        self._addStringProperty('mapID', '')
        self._addResourceProperty('mapName', R.invalid())
        self._addStringProperty('selectedScenario', '')
        self._addResourceProperty('selectedVehicleType', R.invalid())
        self._addNumberProperty('kills', 0)
        self._addNumberProperty('allTargets', 0)
        self._addStringProperty('time', '')
        self._addResourceProperty('vehicleImage', R.invalid())
        self._addBoolProperty('wasDone', False)
        self._addBoolProperty('hangarReady', False)
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
