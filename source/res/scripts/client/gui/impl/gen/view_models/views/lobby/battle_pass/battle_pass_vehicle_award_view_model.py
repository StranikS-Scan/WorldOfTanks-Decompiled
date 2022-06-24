# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_vehicle_award_view_model.py
from frameworks.wulf import ViewModel

class BattlePassVehicleAwardViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(BattlePassVehicleAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleLevelPoints(self):
        return self._getNumber(0)

    def setVehicleLevelPoints(self, value):
        self._setNumber(0, value)

    def getBattlePassPointsAward(self):
        return self._getNumber(1)

    def setBattlePassPointsAward(self, value):
        self._setNumber(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getVehicleNation(self):
        return self._getString(3)

    def setVehicleNation(self, value):
        self._setString(3, value)

    def getVehicleLevel(self):
        return self._getNumber(4)

    def setVehicleLevel(self, value):
        self._setNumber(4, value)

    def getVehicleName(self):
        return self._getString(5)

    def setVehicleName(self, value):
        self._setString(5, value)

    def getTechName(self):
        return self._getString(6)

    def setTechName(self, value):
        self._setString(6, value)

    def getIsPremiumVehicle(self):
        return self._getBool(7)

    def setIsPremiumVehicle(self, value):
        self._setBool(7, value)

    def getIsEliteVehicle(self):
        return self._getBool(8)

    def setIsEliteVehicle(self, value):
        self._setBool(8, value)

    def getIsPostProgression(self):
        return self._getBool(9)

    def setIsPostProgression(self, value):
        self._setBool(9, value)

    def getChapterID(self):
        return self._getNumber(10)

    def setChapterID(self, value):
        self._setNumber(10, value)

    def getFinalReward(self):
        return self._getString(11)

    def setFinalReward(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(BattlePassVehicleAwardViewModel, self)._initialize()
        self._addNumberProperty('vehicleLevelPoints', 0)
        self._addNumberProperty('battlePassPointsAward', 0)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleNation', '')
        self._addNumberProperty('vehicleLevel', 0)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('techName', '')
        self._addBoolProperty('isPremiumVehicle', False)
        self._addBoolProperty('isEliteVehicle', False)
        self._addBoolProperty('isPostProgression', False)
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('finalReward', '')
