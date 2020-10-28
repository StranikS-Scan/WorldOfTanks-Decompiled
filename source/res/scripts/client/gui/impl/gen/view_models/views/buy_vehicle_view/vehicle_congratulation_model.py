# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/vehicle_congratulation_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class VehicleCongratulationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(VehicleCongratulationModel, self).__init__(properties=properties, commands=commands)

    def getIsElite(self):
        return self._getBool(0)

    def setIsElite(self, value):
        self._setBool(0, value)

    def getIsCollectible(self):
        return self._getBool(1)

    def setIsCollectible(self, value):
        self._setBool(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getLvl(self):
        return self._getString(3)

    def setLvl(self, value):
        self._setString(3, value)

    def getVName(self):
        return self._getString(4)

    def setVName(self, value):
        self._setString(4, value)

    def getImage(self):
        return self._getString(5)

    def setImage(self, value):
        self._setString(5, value)

    def getImageAlt(self):
        return self._getString(6)

    def setImageAlt(self, value):
        self._setString(6, value)

    def getBtnLbl(self):
        return self._getResource(7)

    def setBtnLbl(self, value):
        self._setResource(7, value)

    def getBackBtnLbl(self):
        return self._getResource(8)

    def setBackBtnLbl(self, value):
        self._setResource(8, value)

    def getTitle(self):
        return self._getResource(9)

    def setTitle(self, value):
        self._setResource(9, value)

    def getResetAnimTrgigger(self):
        return self._getBool(10)

    def setResetAnimTrgigger(self, value):
        self._setBool(10, value)

    def getNeedBackBtn(self):
        return self._getBool(11)

    def setNeedBackBtn(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(VehicleCongratulationModel, self)._initialize()
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isCollectible', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('lvl', '')
        self._addStringProperty('vName', '')
        self._addStringProperty('image', '')
        self._addStringProperty('imageAlt', '')
        self._addResourceProperty('btnLbl', R.invalid())
        self._addResourceProperty('backBtnLbl', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addBoolProperty('resetAnimTrgigger', False)
        self._addBoolProperty('needBackBtn', False)
