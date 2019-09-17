# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/tech_parameters_cmp_view_model.py
from frameworks.wulf import ViewModel

class TechParametersCmpViewModel(ViewModel):
    __slots__ = ()

    def getEngineSpeed(self):
        return self._getString(0)

    def setEngineSpeed(self, value):
        self._setString(0, value)

    def getEngineAcceleration(self):
        return self._getString(1)

    def setEngineAcceleration(self, value):
        self._setString(1, value)

    def getChassisHandling(self):
        return self._getString(2)

    def setChassisHandling(self, value):
        self._setString(2, value)

    def getGunDpm(self):
        return self._getString(3)

    def setGunDpm(self, value):
        self._setString(3, value)

    def getGunReload(self):
        return self._getString(4)

    def setGunReload(self, value):
        self._setString(4, value)

    def getBodyArmor(self):
        return self._getString(5)

    def setBodyArmor(self, value):
        self._setString(5, value)

    def getEngineSpeedHighlight(self):
        return self._getBool(6)

    def setEngineSpeedHighlight(self, value):
        self._setBool(6, value)

    def getEngineAccelerationHighlight(self):
        return self._getBool(7)

    def setEngineAccelerationHighlight(self, value):
        self._setBool(7, value)

    def getChassisHandlingHighlight(self):
        return self._getBool(8)

    def setChassisHandlingHighlight(self, value):
        self._setBool(8, value)

    def getGunDpmHighlight(self):
        return self._getBool(9)

    def setGunDpmHighlight(self, value):
        self._setBool(9, value)

    def getGunReloadHighlight(self):
        return self._getBool(10)

    def setGunReloadHighlight(self, value):
        self._setBool(10, value)

    def getBodyArmorHighlight(self):
        return self._getBool(11)

    def setBodyArmorHighlight(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(TechParametersCmpViewModel, self)._initialize()
        self._addStringProperty('engineSpeed', '')
        self._addStringProperty('engineAcceleration', '')
        self._addStringProperty('chassisHandling', '')
        self._addStringProperty('gunDpm', '')
        self._addStringProperty('gunReload', '')
        self._addStringProperty('bodyArmor', '')
        self._addBoolProperty('engineSpeedHighlight', False)
        self._addBoolProperty('engineAccelerationHighlight', False)
        self._addBoolProperty('chassisHandlingHighlight', False)
        self._addBoolProperty('gunDpmHighlight', False)
        self._addBoolProperty('gunReloadHighlight', False)
        self._addBoolProperty('bodyArmorHighlight', False)
