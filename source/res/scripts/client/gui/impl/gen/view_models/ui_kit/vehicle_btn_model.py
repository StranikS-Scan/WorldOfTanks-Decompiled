# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/vehicle_btn_model.py
from frameworks.wulf import ViewModel

class VehicleBtnModel(ViewModel):
    __slots__ = ()

    def getFlag(self):
        return self._getString(0)

    def setFlag(self, value):
        self._setString(0, value)

    def getVehType(self):
        return self._getString(1)

    def setVehType(self, value):
        self._setString(1, value)

    def getVehLvl(self):
        return self._getString(2)

    def setVehLvl(self, value):
        self._setString(2, value)

    def getVehIcon(self):
        return self._getString(3)

    def setVehIcon(self, value):
        self._setString(3, value)

    def getVehName(self):
        return self._getString(4)

    def setVehName(self, value):
        self._setString(4, value)

    def getVisible(self):
        return self._getBool(5)

    def setVisible(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(VehicleBtnModel, self)._initialize()
        self._addStringProperty('flag', '')
        self._addStringProperty('vehType', '')
        self._addStringProperty('vehLvl', '')
        self._addStringProperty('vehIcon', '')
        self._addStringProperty('vehName', '')
        self._addBoolProperty('visible', False)
