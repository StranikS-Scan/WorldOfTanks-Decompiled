# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/vehicle_congratulation_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class VehicleCongratulationModel(ViewModel):
    __slots__ = ()

    def getIsElite(self):
        return self._getBool(0)

    def setIsElite(self, value):
        self._setBool(0, value)

    def getVehicleType(self):
        return self._getString(1)

    def setVehicleType(self, value):
        self._setString(1, value)

    def getLvl(self):
        return self._getString(2)

    def setLvl(self, value):
        self._setString(2, value)

    def getVName(self):
        return self._getString(3)

    def setVName(self, value):
        self._setString(3, value)

    def getImage(self):
        return self._getString(4)

    def setImage(self, value):
        self._setString(4, value)

    def getImageAlt(self):
        return self._getString(5)

    def setImageAlt(self, value):
        self._setString(5, value)

    def getBtnLbl(self):
        return self._getResource(6)

    def setBtnLbl(self, value):
        self._setResource(6, value)

    def getTitle(self):
        return self._getResource(7)

    def setTitle(self, value):
        self._setResource(7, value)

    def _initialize(self):
        super(VehicleCongratulationModel, self)._initialize()
        self._addBoolProperty('isElite', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('lvl', '')
        self._addStringProperty('vName', '')
        self._addStringProperty('image', '')
        self._addStringProperty('imageAlt', '')
        self._addResourceProperty('btnLbl', Resource.INVALID)
        self._addResourceProperty('title', Resource.INVALID)
